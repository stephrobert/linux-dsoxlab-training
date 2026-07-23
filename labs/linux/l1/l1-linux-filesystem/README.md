# Lab — the standard filesystem hierarchy (FHS)

## Reminder

[**Linux filesystem hierarchy: what each directory is for**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/arborescence-fhs/)

The **Filesystem Hierarchy Standard** (FHS) is the convention that says where
Linux files each type of file. The guide compares it to the plan of a building:
each floor has a function, and when you know the plan you find things first
time. This lab does not ask you to recite a list: it works on the few
**distinctions** that settle a real administration question, "where do I put
this?" and "where do I go and look for it?".

Writing paths is covered in `l1-paths-absolute-relative`, and reading `ls -l`,
`file` and `stat` in `l1-navigate-filesystem`: none of that is repeated here.

## The course

The examples below explore real directories in **read-only** mode: none of them
copies what the challenge asks for, which bears on other locations. No command
in this course needs `sudo` and none writes anything at all.

All the outputs reproduced here were taken on **Ubuntu 24.04.2 LTS**, kernel
`6.8.0-134-generic`, with `ls (GNU coreutils) 9.4`. That matters: the FHS is a
standard, but its application varies from one distribution to another and from
one version to another. On your machine, the dates, the sizes and a few entries
will differ. Run the same commands on your machine and compare.

### The root, and what it tells

Everything starts from `/`. A single command gives the complete map:

```bash
ls -l /
```

```text
lrwxrwxrwx   1 root root          7 avril 22  2024 bin -> usr/bin
drwxr-xr-x   2 root root       4096 févr. 26  2024 bin.usr-is-merged
drwxr-xr-x   5 root root       4096 juil. 18 06:31 boot
drwxr-xr-x  20 root root       4660 juil. 21 12:33 dev
drwxr-xr-x 128 root root      12288 juil. 22 06:25 etc
[...]
lrwxrwxrwx   1 root root          7 avril 22  2024 lib -> usr/lib
drwxr-xr-x   2 root root       4096 août  27  2024 media
drwxr-xr-x   6 root root       4096 juil.  2 19:19 mnt
drwxr-xr-x   8 root root       4096 juil.  2 18:34 opt
dr-xr-xr-x 975 root root          0 janv.  1  2022 proc
drwx------  13 root root       4096 juil.  6 08:15 root
drwxr-xr-x  42 root root       1380 juil. 22 18:03 run
lrwxrwxrwx   1 root root          8 avril 22  2024 sbin -> usr/sbin
drwxr-xr-x  13 root root       4096 févr.  5 18:12 snap
drwxr-xr-x   2 root root       4096 août  27  2024 srv
-rw-------   1 root root 4294967296 juil. 11  2025 swap.img
dr-xr-xr-x  13 root root          0 janv.  1  2022 sys
drwxrwxrwt 200 root root      36864 juil. 22 18:04 tmp
drwxr-xr-x  12 root root       4096 août  27  2024 usr
drwxr-xr-x  14 root root       4096 févr. 28 09:05 var
```

Three things stand out, and none of them is a detail:

- **The root is not populated only by directories.** For `bin`, `lib` and
  `sbin`, the first column begins with an `l`: they are symbolic links.
  `swap.img` begins with a `-`, it is an ordinary 4 GiB file.
- **Not everything there comes from the FHS.** `snap` and `swap.img` are Ubuntu
  additions, `bin.usr-is-merged` a trace of a migration. The standard describes
  the common base, not the whole of what you will see.
- **`proc` and `sys` show a size of 0** and a date frozen at 1 January 2022: they
  are not on the disk. We come back to that below.

Beware of a false friend: **`/root` is not `/`**. It is the home directory of the
administrator, and its `drwx------` permissions reserve it for them alone.

### The usr-merge: `/bin`, `/sbin` and `/lib` are no longer directories

This is the point where a good half of the documentation still online is out of
date. Historically, `/bin` and `/sbin` contained the binaries needed at boot,
before `/usr` was mounted; `/usr/bin` and `/usr/sbin` contained the rest. That
separation no longer has a reason to exist, and modern distributions have
removed it. Measure it:

```bash
ls -ld /bin /sbin /lib /lib64
```

```text
lrwxrwxrwx 1 root root 7 avril 22  2024 /bin -> usr/bin
lrwxrwxrwx 1 root root 7 avril 22  2024 /lib -> usr/lib
lrwxrwxrwx 1 root root 9 avril 22  2024 /lib64 -> usr/lib64
lrwxrwxrwx 1 root root 8 avril 22  2024 /sbin -> usr/sbin
```

All four are links: on this machine, `/bin` and `/usr/bin` **are the same
directory**. The guide dates this merge, the usr-merge, to Debian 12+,
Ubuntu 22.04+, RHEL 9+, Fedora and Arch; Alpine, for its part, keeps the
separation.

The distinction that **remains** alive is therefore not `/` against `/usr`, but
`bin` against `sbin`: `/usr/bin` carries everybody's commands, `/usr/sbin` the
administration ones (`fdisk`, `useradd`, `iptables` according to the guide). A
binary that cannot be found as an ordinary user is often simply in `sbin`,
outside your `PATH`.

Same story for the runtime state: `/var/run` has been replaced by `/run`, and is
now only a link to it.

```bash
ls -ld /var/run /var/lock
```

```text
lrwxrwxrwx 1 root root 9 août  27  2024 /var/lock -> /run/lock
lrwxrwxrwx 1 root root 4 août  27  2024 /var/run -> /run
```

Documentation that has you write a PID file into `/var/run` will still work,
through that link, but the location to write to today is `/run`.

### `/usr`, `/usr/local` and `/opt`: three ways of installing software

`/usr` is the application core: that is where the package manager drops
everything it installs.

| Path | Content (guide) |
|---|---|
| `/usr/bin/` | user commands |
| `/usr/sbin/` | administration commands |
| `/usr/lib/` | shared libraries and support files |
| `/usr/share/` | documentation and architecture-independent data |
| `/usr/local/` | software installed **manually**, outside the package manager |

The question an administrator really asks is: *I have just downloaded a binary,
where do I put it?* The answer fits in one rule: **not in `/usr/bin`**, which the
package manager will overwrite at the next update. Two locations are provided
for you, with two different conventions:

- `/usr/local/` reproduces the structure of `/usr` (`bin`, `sbin`, `lib`, `etc`,
  `share`) and takes in isolated binaries;
- `/opt/<product>/` takes in a **self-contained** third-party application, which
  keeps its files grouped in its own folder.

The two are often combined, and the test machine gives a clear example of it:

```bash
ls -l /opt/opentofu ; ls -l /usr/local/bin/tofu
```

```text
total 110740
[...]
-rwxr-xr-x 1 student  student  113348792 janv. 21 17:10 tofu
lrwxrwxrwx 1 root root        18 janv. 31 20:10 /usr/local/bin/tofu -> /opt/opentofu/tofu
```

The product lives grouped in `/opt`, and a simple link from `/usr/local/bin`
makes it callable. Why that one? Because it is in the `PATH`, and **before** the
system directories: `echo "$PATH"` here contains, in this order,
`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`. `/usr/local/bin`
precedes `/usr/bin`, so your home-made version wins over the packaged one. That
is intended, and it is also a classic troubleshooting trap.

### `/etc`, `/var`, `/srv`: the configuration, the state, the served data

These three directories answer three distinct questions, and mixing them up is
the most frequent filing mistake.

**`/etc`: what you decide.** Configuration only, in editable text files, one
subdirectory per service. `ls -d /etc/*/` lists them, and `ls -d /etc/*/ | wc -l`
counts 126 of them on the test machine: `/etc/apache2/`, `/etc/apt/`,
`/etc/cron.d/`, `/etc/ssh/`, `/etc/systemd/` and one hundred and twenty-one
others.

The golden rule of the guide is worth remembering word for word: **never modify
a file in `/usr/lib/` or `/usr/share/`**, copy it or override it in `/etc/`. A
real example of this mechanism:

```bash
ls -l /usr/lib/systemd/system/containerd.service /etc/systemd/system/containerd.service.d/
```

```text
-rw-r--r-- 1 root root 1242 déc.  18  2025 /usr/lib/systemd/system/containerd.service

/etc/systemd/system/containerd.service.d/:
total 4
-rw-r--r-- 1 root root 78 janv. 23 10:36 override.conf
```

The package provides the unit in `/usr/lib`, the administrator overrides it in
`/etc`. An update will replace the first and leave the second intact.

**`/var`: what the machine produces.** Everything that grows, changes,
accumulates while the system runs.

| Path | Content (guide) |
|---|---|
| `/var/lib/` | persistent state of the services (databases, packages) |
| `/var/cache/` | caches, cleanable to reclaim space |
| `/var/spool/` | queues (printing, mail, cron) |
| `/var/tmp/` | persistent temporary files |

`/var/lib` is the answer to "where does this service file its data?". On the
test machine it contains one entry per installed service: `apt`, `containerd`,
`docker`, `dpkg`, `libvirt`, `kubelet`. The guide warns that a saturated `/var`
can block the entire system when it shares the root partition, hence the habit
of separating it in production (`df -h /var`).

**`/srv`: what the machine serves to others.** The content a server exposes
(sites, repositories, shares). It is the only one of the three whose filling is
left free, and on a workstation it is simply empty: `ls -A /srv` prints no line
and yet returns exit code 0, the proof that the directory exists but that
nothing occupies it. Note that many distributions nevertheless serve their sites
from `/var/www`.

### `/tmp` against `/var/tmp`: which one survives a reboot

Both are writable by everybody, with the sticky bit (the final `t`) which
prevents deleting somebody else's file:

```bash
ls -ld /tmp /var/tmp
```

```text
drwxrwxrwt 200 root root 36864 juil. 22 18:04 /tmp
drwxrwxrwt  11 root root  4096 juil. 22 17:47 /var/tmp
```

The difference is **the lifetime**: `/tmp` is emptied at reboot, `/var/tmp`
survives. A received idea attributes that to `/tmp` supposedly being in RAM. It
is false here, and it is verifiable:

```bash
df -Th /tmp /var/tmp
```

```text
Filesystem                        Type  Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv ext4  914G  537G  339G  62% /
/dev/mapper/ubuntu--vg-ubuntu--lv ext4  914G  537G  339G  62% /
```

Both are on the same `ext4` partition, the root. `/tmp` is therefore not a
`tmpfs` on this machine, and it is nevertheless emptied: it is `systemd` that
takes care of it, on the strength of a declared rule:

```bash
grep -Ev '^#|^$' /usr/lib/tmpfiles.d/tmp.conf
systemctl cat systemd-tmpfiles-setup.service | grep ExecStart
```

```text
D /tmp 1777 root root 30d
ExecStart=systemd-tmpfiles --create --remove --boot --exclude-prefix=/dev
```

The `D /tmp` line is active, the one concerning `/var/tmp` is commented out in
that same file. The service runs at boot with `--remove --boot`. **The practical
conclusion does not change**: a file you want to find again after a reboot does
not go into `/tmp`. And in a script, create it with `mktemp` rather than with a
fixed name, to avoid collisions and symbolic link attacks.

### `/proc`, `/sys`, `/run`: files that are not on the disk

These are **virtual filesystems**, generated on the fly by the kernel. Their
files have no stored content, and their displayed size means nothing:

```bash
ls -l /proc/uptime ; cat /proc/uptime ; wc -c /proc/uptime
```

```text
-r--r--r-- 1 root root 0 juil. 14 18:39 /proc/uptime
728281.78 10823041.61
22 /proc/uptime
```

Zero bytes announced, twenty-two bytes read. The file is manufactured at the
moment you read it: those two numbers are the seconds elapsed since boot and the
cumulative idle time of the cores. On the `/sys` side, the announced size is not
0 but 4096, the size of a memory page, which says nothing more:
`ls -l /sys/class/net/lo/mtu` announces 4096 bytes, `cat` of the same file
answers `65536` and `wc -c` counts six.

The proof that they consume no disk fits in one command:

```bash
findmnt -t proc,sysfs,tmpfs -o TARGET,SOURCE,FSTYPE,SIZE
```

```text
TARGET     SOURCE  FSTYPE  SIZE
/sys       sysfs   sysfs      0
/proc      proc    proc       0
/run       tmpfs   tmpfs   4,7G
[...]
```

Their source is not a block device but `proc` and `sysfs` themselves, for a null
size; `df -hT /proc /sys` confirms it with `Size`, `Used` and `Avail` columns at
0. `/run` is a `tmpfs`, therefore RAM: it carries
the runtime state of the services (PID files, sockets, locks) and starts empty
again at every boot.

Hence the rule of the guide: **you never back up `/proc` or `/sys`**. Including
them in a `tar` or an `rsync` of the root copies no useful data and causes errors
or loops; always exclude them.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| a doc distinguishes `/bin` from `/usr/bin` and you observe no difference | usr-merge: they are the same | `ls -ld /bin /sbin /lib` |
| `command not found` on an administration command | it is in `sbin`, outside your `PATH` | `echo "$PATH"` |
| a manually installed command is ignored in favour of the old one | order of the `PATH`, `/usr/local/bin` first | `type -a <command>` |
| a modified setting is not taken into account | edited in `/usr/lib/`, overwritten by the update | override under `/etc/` |
| a file has disappeared after a reboot | it was in `/tmp` | use `/var/tmp` |
| a file in `/proc` shows 0 bytes | virtual filesystem | `cat` then `wc -c` |
| a backup of `/` fails or never ends | `/proc` and `/sys` not excluded | `findmnt -t proc,sysfs` |
| `No space left on device` although `df -h /` looks correct | `/var` on a separate partition | `df -h /var` |

No command in this course created anything: there is nothing to clean up.
