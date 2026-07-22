# Lab — manage an AppArmor profile

## Reminder

[**AppArmor on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/)

AppArmor confines programs with per-binary profiles. `aa-status` lists loaded
profiles and their mode; `aa-complain <profile>` switches a profile to learning
mode (logs, does not block), `aa-enforce` puts it back in enforce, `aa-disable`
unloads it. It is the Debian counterpart of SELinux, but per profile.

## The course

The examples below confine a throwaway binary, `/usr/local/bin/atelier-lecteur`,
for which you write a profile from scratch: the challenge will be about a profile
already shipped by the distribution. Learn the observe / adjust / enforce cycle, do
not copy a line. Real output from an Ubuntu 24.04.4 LTS, `apparmor` and
`apparmor-utils` packages in `4.0.1really4.0.1-0ubuntu0.24.04.7`.

> **Never switch to `enforce` a profile that guards your own access.** Too tight on
> `sshd`, `dhclient`, `systemd` or `netplan`, it locks you out, and there is **no
> safety net** here: `student` goes through the same port 22, with no guest agent
> channel.

### Where AppArmor stands on this machine

`aa-status` (alias `apparmor_status`) is the **only** source of truth: neither
`systemctl` nor the presence of a file in `/etc/apparmor.d/` tells you what the
kernel enforces. Record the starting state, you will have to be able to restore it.

```bash
sudo aa-status
```

```text
apparmor module is loaded.
117 profiles are loaded.
23 profiles are in enforce mode.
   /usr/bin/man
   [...]
4 profiles are in complain mode.
   transmission-cli
   [...]
0 profiles are in prompt mode.
0 profiles are in kill mode.
90 profiles are in unconfined mode.   [...]
1 processes have profiles defined.
1 processes are in enforce mode.
   /usr/sbin/rsyslogd (710) rsyslogd
```

Remember the first six numbers and the last block, they are your reference points
for the end of the exercise. Two things to understand right away: the distribution
**already ships** profiles (117 loaded, four of them in complain that no
administrator asked for), and profiles are counted separately from **processes**,
only one being confined here. The kernel module is checked elsewhere, and the guide
insists: on Debian, Ubuntu and openSUSE, AppArmor is loaded **by default**, with no
GRUB parameter.

```bash
cat /sys/module/apparmor/parameters/enabled ; cat /sys/kernel/security/lsm
dpkg -l apparmor apparmor-utils | grep ^ii | awk '{print $2, $3}'
```

```text
Y
lockdown,capability,landlock,yama,apparmor
apparmor 4.0.1really4.0.1-0ubuntu0.24.04.7   [...]
```

Without `apparmor-utils`, no `aa-*` command at all: first reflex if `command not found`.

### One profile, one path: the difference with SELinux

Profiles live in `/etc/apparmor.d/`, one text file per program (109 entries here).
Let us write one for a throwaway binary, a copy of `cat`:

```bash
sudo install -d /srv/atelier/donnees /srv/atelier/prive
printf 'temperature=21.4\n' | sudo tee /srv/atelier/donnees/mesures.txt
printf 'jeton=demo\n'       | sudo tee /srv/atelier/prive/secret.txt
sudo cp /usr/bin/cat /usr/local/bin/atelier-lecteur
sudo tee /etc/apparmor.d/usr.local.bin.atelier-lecteur <<'EOF'
abi <abi/4.0>,
include <tunables/global>

/usr/local/bin/atelier-lecteur {
  include <abstractions/base>

  /usr/local/bin/atelier-lecteur mr,
  /srv/atelier/donnees/** r,
}
EOF
```

Three things to read. The **file name** is conventional (the path of the binary,
slashes replaced with dots) but it does not matter: it is the opening line
`/usr/local/bin/atelier-lecteur {` that designates the confined program. Each rule is
a **path** followed by permissions (`r` read, `w` write, `m` map) and a comma.
`include <abstractions/base>` brings the common ground every program requires;
without it, nothing starts.

This is the parting of the ways with SELinux, which labels the **inode**: the context
travels with the file, and a `mv` keeps it, as measured by the `l4-selinux-diagnose-avc`
course (a file moved from `~` lands in `/etc` as `user_home_t` and breaks the service).
AppArmor only knows the **path**. Let us check, with the profile loaded in enforce:

```bash
sudo cp -a /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-copie
sudo ln    /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-lien
stat -c '%i %n' /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-lien
/usr/local/bin/atelier-lien /srv/atelier/prive/secret.txt
```

```text
44963 /usr/local/bin/atelier-lecteur
44963 /usr/local/bin/atelier-lien
jeton=demo
```

The hard link carries the **same inode** (44963) and therefore points at the same
binary, but its path appears in no profile: it runs **unconfined** and reads a file
the profile forbids. The copy does the same. Under SELinux, the label being carried
by the inode, a hard link stays subject to the policy. This is the trade-off
announced by the guide: AppArmor is simpler, but a hard link, a bind mount or a
renamed binary can escape a rule.

### Loaded, enforced, confined: three distinct states

This distinction is worth the one between `enabled` and `active` for a systemd unit.

```bash
sudo aa-status | grep -c atelier-lecteur          # 0: file present, nothing loaded
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.atelier-lecteur
sudo aa-status | grep -E "^[0-9]+ profiles are (loaded|in enforce)"
```

```text
0
118 profiles are loaded.
24 profiles are in enforce mode.
```

First step: a file dropped in `/etc/apparmor.d/` **is not an active profile**. As
long as `apparmor_parser -r` has not injected it into the kernel, `aa-status` ignores
it. Note that loading happens **in enforce**, not in complain: unless stated
otherwise, a freshly written profile blocks from the first second. Second step:
loaded does not mean a process is subject to it. Let us start one that lasts:

```bash
setsid /usr/local/bin/atelier-lecteur > /dev/null < /dev/zero &
sudo aa-status | sed -n '/processes have profiles/,+3p'
cat /proc/$(pgrep -f atelier-lecteur | head -1)/attr/current
```

```text
2 processes have profiles defined.
2 processes are in enforce mode.
   /usr/local/bin/atelier-lecteur (3306)
   /usr/sbin/rsyslogd (707) rsyslogd
/usr/local/bin/atelier-lecteur (enforce)
```

`/proc/<pid>/attr/current` is the AppArmor equivalent of `ps -Z` under SELinux: it
gives the profile **actually carried** by a live process, mode included. The counter
drops back to 1 as soon as the process ends, whereas the profile stays loaded: it
protects nothing at that instant, but will apply at the next start.

### complain first, enforce afterwards

This is the method of the subject, and the reverse order breaks services in
production. `aa-complain` switches a profile to learning:

```bash
sudo aa-complain /usr/local/bin/atelier-lecteur
sudo aa-status | grep -E "^[0-9]+ profiles are in (enforce|complain)"
grep flags /etc/apparmor.d/usr.local.bin.atelier-lecteur
```

```text
Setting /usr/local/bin/atelier-lecteur to complain mode.
23 profiles are in enforce mode.
5 profiles are in complain mode.
/usr/local/bin/atelier-lecteur flags=(complain) {
```

Look at the last line: `aa-complain` **rewrites the profile file**, adding
`flags=(complain)` to it. A difference in nature with SELinux's `setenforce 0`, which
only lives in memory: here the mode is **persistent** and survives a reboot, verified
on this machine, `aa-status` showing after a `systemctl reboot` the same five profiles
in complain. The profile only allows `/srv/atelier/donnees/**`; in complain, let us
read a file outside that scope anyway:

```bash
/usr/local/bin/atelier-lecteur /etc/hostname
sudo journalctl -k --since -2min | grep -i apparmor | tail -1
```

```text
atelier.lab
kernel: audit: type=1400 audit(1784745049.196:123): apparmor="ALLOWED"
 operation="open" class="file" profile="/usr/local/bin/atelier-lecteur"
 name="/etc/hostname" pid=2292 comm="atelier-lecteur" requested_mask="r"
 denied_mask="r" fsuid=1001 ouid=0
```

The read goes through, and yet the trace carries `denied_mask="r"`: the kernel says
"I would have refused, I let it through, and I am recording it". The fields to know
how to read are always the same: `apparmor=` (the verdict), `operation=` (what was
attempted), `profile=` (the culprit), `name=` (the resource), `requested_mask` and
`denied_mask`. In enforce, the same line becomes `apparmor="DENIED"` and the call
fails:

```text
apparmor="DENIED" operation="open" class="file" profile="/usr/local/bin/atelier-lecteur"
 name="/srv/atelier/prive/secret.txt" pid=2751 requested_mask="r" denied_mask="r"
```

On the application side, it is a plain `Permission denied` while the Unix permissions
are fine: the signature of a MAC refusal, like a SELinux AVC.

> **The complain trap.** Complain is not "no protection": an **explicit** `deny` rule
> still blocks. Measured here, a `deny /srv/atelier/prive/** r,` refuses the read in
> complain as well as in enforce, and without writing **a single line** to the journal.
> A `deny` filters silently: when a refusal cannot be found in the traces, read the
> profile again.

### aa-logprof: turning traces into rules

Once traces have piled up, `aa-logprof` reads the journal again and offers to add the
observed rules. On Ubuntu 24.04, `rsyslog` is present and `/var/log/syslog` exists:
the tool finds its journal on its own. On **Debian 12** it does not exist, and the
guide gives the workaround (`journalctl -b -k -e -f > /var/tmp/aa.log` then
`aa-logprof -f`). Reducing the file to your own events also avoids parasitic
suggestions:

```bash
sudo journalctl -k --since -20min | grep atelier-lecteur > /var/tmp/aa-atelier.log
sudo aa-logprof -f /var/tmp/aa-atelier.log
```

```text
Reading log entries from /var/tmp/aa-atelier.log.
Complain-mode changes:
Profile:  /usr/local/bin/atelier-lecteur
Path:     /etc/hostname
New Mode: r
 [1 - /etc/hostname r,]
(A)llow / [(D)eny] / (I)gnore / (G)lob / Glob with (E)xtension / (N)ew / ...
Adding /etc/hostname r, to profile.
= Changed Local Profiles =
(S)ave Changes / Save Selec(t)ed Profile / [(V)iew Changes] / ...
Writing updated profile for /usr/local/bin/atelier-lecteur.
```

Two keystrokes are enough, `a` then `s`, but the tool **requires a terminal**: run
without a TTY it crashes on `termios.error: Inappropriate ioctl for device`. Sort
through what it offers rather than accepting everything, the guide pointing out that
it often suggests off-topic abstractions. The file comes back rewritten and sorted,
with the line `/etc/hostname r,` inserted. All that is left is to close the loop:
`aa-enforce` removes `flags=(complain)` and reloads right away.

```bash
sudo aa-enforce /usr/local/bin/atelier-lecteur
sudo aa-status --json | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['profiles']['/usr/local/bin/atelier-lecteur'])"
```

```text
Setting /usr/local/bin/atelier-lecteur to enforce mode.
enforce
```

`aa-status --json` is the form to prefer as soon as a script has to decide: it returns
a `profiles` dictionary mapping each profile to its mode, with no text to slice up.

### Reloading is not disabling

Two neighbouring gestures that the exam likes to confuse. After **editing** a profile,
`apparmor_parser -r` (as in *replace*) reads it again and replaces the version in
memory. Without it, the file has changed but the kernel still enforces the old policy:

```bash
# add the line "/srv/atelier/prive/** r," to the profile, then:
/usr/local/bin/atelier-lecteur /srv/atelier/prive/secret.txt   # Permission denied
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.atelier-lecteur
/usr/local/bin/atelier-lecteur /srv/atelier/prive/secret.txt   # jeton=demo
```

`aa-disable`, on the other hand, **unloads** the profile and puts a link in
`/etc/apparmor.d/disable/` so that it does not come back at boot:

```bash
sudo aa-disable /usr/local/bin/atelier-lecteur
ls -l /etc/apparmor.d/disable/ ; sudo aa-status | grep "profiles are loaded"
```

```text
Disabling /usr/local/bin/atelier-lecteur.
usr.local.bin.atelier-lecteur -> /etc/apparmor.d/usr.local.bin.atelier-lecteur
117 profiles are loaded.
```

The counter drops from 118 to 117, yet the profile file stays on disk, and the binary
is no longer mediated at all. Hence the classic symptom from the guide: a profile you
believe to be disabled **comes back** because you deleted the link without reloading,
or stays inert because you forgot to delete it. The two gestures go together:

```bash
sudo rm /etc/apparmor.d/disable/usr.local.bin.atelier-lecteur
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.atelier-lecteur
```

### Troubleshooting and back to the initial state

| Symptom | Likely cause | Fix |
|---|---|---|
| `aa-complain: command not found` | `apparmor-utils` missing | `sudo apt-get install apparmor-utils` |
| The edited profile has no effect | File modified, kernel not reloaded | `sudo apparmor_parser -r /etc/apparmor.d/<profile>` |
| A hand-written profile blocks straight away | `apparmor_parser -r` loads in **enforce** | `sudo aa-complain <binary>` before testing |
| `Permission denied` with correct Unix permissions | MAC refusal | `sudo journalctl -k \| grep -i apparmor`, look for `DENIED` |
| A refusal stays invisible in the journal | Explicit `deny` rule, silent | Read the profile again, not just the traces |
| `aa-logprof`: `termios.error` | Run without a terminal | Run it again in a real TTY |
| `aa-logprof`: `Can't find system log` (guide) | Debian 12 without `rsyslog` | `journalctl -b -k -e -f > /var/tmp/aa.log`, then `-f` |
| A disabled profile comes back (guide) | Link left in `disable/` | `rm /etc/apparmor.d/disable/<profile>` then `apparmor_parser -r` |

To undo everything, **unload before deleting**: erasing the file does not remove the
profile from the kernel, which would keep confining until the next reboot.

```bash
sudo apparmor_parser -R /etc/apparmor.d/usr.local.bin.atelier-lecteur   # R = remove
sudo rm /etc/apparmor.d/usr.local.bin.atelier-lecteur
sudo rm -f /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-copie /usr/local/bin/atelier-lien
sudo rm -rf /srv/atelier
```

Then compare with the initial record, including the two control directories:

```bash
sudo aa-status | grep -E "^[0-9]+ profiles"
ls -A /etc/apparmor.d/disable/ /etc/apparmor.d/force-complain/
```

```text
117 profiles are loaded.
23 profiles are in enforce mode.
4 profiles are in complain mode.   [...]
90 profiles are in unconfined mode.
```

The six counters are identical to the start and `disable/` is empty: the machine is
handed back. If one of them does not drop back, look for a forgotten `flags=(complain)`
in a file of `/etc/apparmor.d/`, since that is where the mode is written.
