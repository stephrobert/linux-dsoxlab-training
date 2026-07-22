# Lab — persistent journald

## Reminder

[**systemd journals on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/)

`systemd-journald` writes either in `/run/log/journal` (in memory, lost at
reboot) or under `/var/log/journal` (on disk). Which regime applies depends on
the `Storage=` directive of the journald configuration **and** on the existence
of the destination directory. `journalctl --list-boots` and `journalctl -b -1`
tell you immediately which of the two you are in: without a persistent journal,
the machine knows only one boot, its own.

## The course

The measurements below were made on a workshop machine running AlmaLinux 10.2
(systemd 257), with a drop-in named `99-atelier.conf` and sizes chosen for the
demonstration (64 MiB, 16 MiB, 1 week). The challenge will ask you for another
setting: the goal here is to understand **what triggers what**, not to copy a
line.

### Where journald writes, and how to read it

A few commands are enough to establish the current regime: the locations, the
space used, the known history.

```bash
ls -ld /run/log/journal /var/log/journal
journalctl --disk-usage
journalctl --list-boots
journalctl -b -1
```

```text
drwxr-sr-x+ 3 root systemd-journal 60 Jul 22 13:29 /run/log/journal
ls: cannot access '/var/log/journal': No such file or directory
Archived and active journals take up 12M in the file system.
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
  0 8bad63d36f3c4974a4d73a72649a4d20 Wed 2026-07-22 13:29:55 UTC Wed 2026-07-22 15:30:58 UTC
Specifying boot ID or boot offset has no effect, no persistent journal was found.
```

One single boot listed, and a request for a previous boot that fails with an
unambiguous diagnosis. journald, for its part, announces its choice at every
boot: this is the most useful line of the whole lab.

```bash
journalctl -u systemd-journald | tail -2
```

```text
systemd-journald[2085]: Journal started
systemd-journald[2085]: Runtime Journal (/run/log/journal/0848e893...) is 2.3M, max 18.9M, 16.6M free.
```

`Runtime Journal` means memory, `System Journal` means disk. No other command
gives the information as directly.

### The proof by reboot

The rest of the course is only worth it once you have seen the loss happen. You
drop a marker, you reboot, you look for it:

```bash
logger -t atelier "REPERE-AVANT-REBOOT"     # Jul 22 15:30:58 atelier[22856]: REPERE-AVANT-REBOOT
sudo systemctl reboot
```

After the reboot, on this machine with a volatile journal:

```text
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
  0 23936a39b031438a85852d0580cb2752 Wed 2026-07-22 15:31:07 UTC Wed 2026-07-22 15:31:18 UTC
```

```bash
journalctl -t atelier      # -- No entries --
journalctl --disk-usage    # Archived and active journals take up 3M in the file system.
```

The marker is gone, the boot identifier has changed, the usage has dropped back.
This is the situation of a server that reboots on its own during the night: in
the morning, the cause no longer exists.

### What triggers persistence: three values and a directory

On AlmaLinux 10, **`/etc/systemd/journald.conf` does not exist**: the file
shipped by the package is at `/usr/lib/systemd/journald.conf` and contains only
commented-out values, which document the defaults.

```bash
ls /etc/systemd/journald.conf
grep -E '^#(Storage|SystemMaxUse|SystemKeepFree)' /usr/lib/systemd/journald.conf
```

```text
ls: cannot access '/etc/systemd/journald.conf': No such file or directory
#Storage=auto
#SystemMaxUse=
#SystemKeepFree=
```

So you do not modify an existing file: you add a drop-in under
`/etc/systemd/journald.conf.d/`, which overlays the shipped file. The following
table sums up what each value of `Storage=` produces, as measured on the
machine:

| `Storage=` | Observed behaviour |
|---|---|
| `volatile` | `Runtime Journal (/run/...)`, **even if `/var/log/journal` exists and contains files** |
| `auto` (default) | disk **if and only if** `/var/log/journal` exists; journald never creates it |
| `persistent` | journald creates `/var/log/journal` itself at flush time (not on a simple service restart), but with permissions that are not those of the distribution (see below) |

First consequence: under the `auto` default, creating the directory is enough,
no directive is needed. Second consequence, about the command everyone copies:

```bash
sudo systemd-tmpfiles --create --prefix /var/log/journal
echo "rc=$?" ; ls -ld /var/log/journal
```

```text
rc=0
ls: cannot access '/var/log/journal': No such file or directory
```

**`systemd-tmpfiles` does not create that directory.** It exits successfully and
does nothing, because the rule that concerns it is a `z` (adjust) and not a `d`
(create):

```bash
grep 'var/log/journal' /usr/lib/tmpfiles.d/systemd.conf
```

```text
z /var/log/journal 2755 root systemd-journal - -
a+ /var/log/journal - - - - d:group:adm:r-x,d:group:wheel:r-x,group:adm:r-x,group:wheel:r-x
```

Its role is to **fix** the permissions of a directory that is already there, not
to build it. An ordinary `mkdir`, for its part, does not give the right
attributes:

```bash
sudo mkdir -p /var/log/journal && ls -ld /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal && ls -ld /var/log/journal
```

```text
drwxr-xr-x. 2 root root            6 Jul 22 15:31 /var/log/journal
drwxr-sr-x+ 2 root systemd-journal 6 Jul 22 15:31 /var/log/journal
```

Three changes in one command: the group becomes `systemd-journal`, the
**set-GID** bit appears (the `s` of the group, mode `2755`, so that everything
created inside inherits the group), and the trailing `+` signals ACLs, the ones
that open read access to the `adm` and `wheel` groups.

This is not cosmetic. A user who belongs to none of those groups is told so by
`journalctl`:

```text
Users in groups 'adm', 'systemd-journal', 'wheel' can see all messages.
No journal files were opened due to insufficient permissions.
```

When journald creates the directory on its own, the result is worse:
`drwxr-xr-x. 3 root root` and files `-rw-r----- root root`. No set-GID, no
`systemd-journal` group, no ACL. So the habit is to run
`systemd-tmpfiles --create` afterwards, whatever the way the directory appeared,
and to check with `ls -ld` that the `s` and the `+` are there.

That leaves the most counter-intuitive measurement of the lab. Directory
created, permissions fixed, service restarted:

```bash
sudo systemctl restart systemd-journald
sudo find /var/log/journal -type f | wc -l
journalctl -u systemd-journald -n 1
```

```text
0
systemd-journald[2085]: Runtime Journal (/run/log/journal/0848e893...) is 2.3M, max 18.9M, 16.6M free.
```

Zero files, and journald still writes in memory. What triggers the switch is the
explicit flush request:

```text
# sudo journalctl --flush
systemd-journald[2085]: Received client request to flush runtime journal.
systemd-journald[2085]: Time spent on flushing to /var/log/journal/0848e893... is 3.327ms for 56 entries.
systemd-journald[2085]: System Journal (/var/log/journal/0848e893...) is 8M, max 894.9M, 886.8M free.
```

`Runtime Journal` has become `System Journal`: the switch has happened. At the
next boot, that flush will be automatic, which is the role of the
`systemd-journal-flush.service` unit, once `/var` is mounted. It is manual only
when you enable persistence on a machine that has already booted.

The result, after a second reboot, finally reads as hoped: two boots listed, and
the marker from the previous one still there.

```text
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
 -1 23936a39b031438a85852d0580cb2752 Wed 2026-07-22 15:31:07 UTC Wed 2026-07-22 15:32:05 UTC
  0 a6570b953d054a07a38240da3092b148 Wed 2026-07-22 15:32:08 UTC Wed 2026-07-22 15:32:17 UTC
# journalctl -b -1 -t atelier
Jul 22 15:32:03 atelier atelier[1376]: REPERE-AVANT-REBOOT-2
```

A detail that helps when troubleshooting: `journalctl` **reads** both locations.
After switching to `Storage=volatile`, the old files in `/var/log/journal` stay
readable and keep appearing in `--list-boots`, while journald no longer writes
there. So do not conclude from `--list-boots` alone that persistence is active:
read the `Journal started` line of the service.

### The size limits, the part people skip

A persistent journal without a limit is a production incident waiting to happen.
The directives read badly if you do not know what "System" designates. The
manual (`man journald.conf`) is explicit:

> Options prefixed with `System` apply to the journal files when stored on a
> persistent file system, more specifically `/var/log/journal`. Options prefixed
> with `Runtime` apply to the journal files when stored on a volatile in-memory
> file system, more specifically `/run/log/journal`.

So this is not about system services as opposed to user services:
`SystemMaxUse` does cap a user's journal, as soon as it is written to disk.

With no setting, journald displays a computed cap at startup: **10 % of the
filesystem**, which is 894.9 MiB here for an 8.8 GiB root. A drop-in is enough
to change it:

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nSystemMaxUse=64M\nSystemMaxFileSize=16M\nSystemKeepFree=1G\nMaxRetentionSec=1week\n' \
  | sudo tee /etc/systemd/journald.conf.d/99-atelier.conf
sudo systemctl restart systemd-journald
journalctl -u systemd-journald -n 1
# System Journal (/var/log/journal/0848e893...) is 16M, max 64M, 48M free.
```

| Directive | What it bounds |
|---|---|
| `SystemMaxUse` | the total size of all journal files on disk |
| `SystemKeepFree` | the free space journald forbids itself to eat into on the filesystem |
| `SystemMaxFileSize` | the size of a file before rotation, hence the granularity of the purge |
| `MaxRetentionSec` | the age beyond which an archived file is deleted |

The trap is `SystemKeepFree`, because the cap actually applied is the **more
constraining of the two**. On this 8.8 GiB machine of which 7.7 GiB are free,
raising `SystemKeepFree` to `7880M`:

```text
System Journal (/var/log/journal/0848e893...) is 16M, max 16M, 0B free.
```

`SystemMaxUse=64M` is still written, but the effective cap has dropped to 16 MiB
and there is nothing left to write. A badly calibrated value here does not fill
the disk: it silently makes the history you thought you were keeping disappear.
Hence the habit of reading the `System Journal` line again after every change,
rather than trusting the file.

Manual purging, for its part, acts right away:

```bash
journalctl --disk-usage          # Archived and active journals take up 40.1M
sudo journalctl --vacuum-size=24M
```

```text
Deleted archived journal /var/log/journal/0848e893.../system@cfb8915f...journal (3.7M).
Deleted archived journal /var/log/journal/0848e893.../user-1001@cfb8915f...journal (8.2M).
[...]
Vacuuming done, freed 24.1M of archived journals from /var/log/journal/0848e893...
# journalctl --disk-usage : Archived and active journals take up 16M
```

Two limits to know about. `--vacuum-size` and `--vacuum-time` only delete
**archived** files: active files are never touched, which explains why you do
not always reach the requested target. To go further, you first have to force a
rotation with `sudo journalctl --rotate`. And above all, a purge that is too
broad destroys exactly what persistence was there to keep: after a `--rotate`
followed by a `--vacuum-size=8M`, `--list-boots` knew only one boot again, as on
day one.

### Checking your configuration, before and after

There is **no** prior validation. `systemd-analyze cat-config
systemd/journald.conf` only assembles the files: it displays an invented
directive (`Compresss=yes`) without a flinch and exits with code 0. Reloading on
the fly is not an option either:

```bash
sudo systemctl reload systemd-journald
# Failed to reload systemd-journald.service: Job type reload is not applicable for unit systemd-journald.service.
```

So the only real check happens **when the service restarts**, and it only shows
up in the journal. The service starts anyway, `systemctl restart` returns 0, and
nothing is displayed on the terminal:

```bash
sudo systemctl restart systemd-journald && journalctl -u systemd-journald -n 5
```

```text
systemd-journald[2021]: .../99-atelier.conf:4: Unknown key 'Compresss' in section [Journal], ignoring.
systemd-journald[1252]: .../99-atelier.conf:2: Failed to parse Storage=persistant, ignoring: Invalid argument
```

The first message reports an unknown key, the second an invalid value on a
correct key. In both cases the line is **ignored** and the default applies. A
typo therefore does not show: it turns into a setting that never took effect.
The check to perform systematically after a service restart is thus the pair
error message / `Journal started` line that follows.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `no persistent journal was found` on `journalctl -b -1` | journal in memory, the on-disk directory does not exist |
| `/var/log/journal` created, but journald still says `Runtime Journal` | the flush was not requested, or `Storage=volatile` blocks it |
| Directory created, no file inside after a service restart | `restart` does not switch, you need `journalctl --flush` |
| `systemd-tmpfiles --create` exits 0 and creates nothing | the rule is a `z` (adjust), the directory must already exist |
| `No journal files were opened due to insufficient permissions` | user missing from `adm`, `systemd-journal` and `wheel` |
| No `s` and no `+` on `ls -ld /var/log/journal` | directory created by hand or by journald, run `systemd-tmpfiles --create` again |
| Directive with no effect, no visible error | key or value ignored, read `journalctl -u systemd-journald` after the restart |
| Cap much lower than `SystemMaxUse` | `SystemKeepFree` is more constraining, read the `System Journal` line |
| `--vacuum-size` does not reach the target | only archived files are purged, run `journalctl --rotate` first |
| `--list-boots` shows history although the journal is volatile | `journalctl` also reads the old files in `/var/log/journal` |

To go back to the volatile state and start over:

```bash
sudo rm -rf /etc/systemd/journald.conf.d /var/log/journal
sudo systemctl restart systemd-journald
journalctl -u systemd-journald -n 1   # must say "Runtime Journal" again
```
