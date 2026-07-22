# Lab — per-user resource limits

## Reminder

[**Resource limits on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/)

`ulimit` shows and sets the limits of the current shell; the durable policy is
in `/etc/security/limits.conf` and `/etc/security/limits.d/*.conf`, one rule per
line `<domain> <type> <item> <value>`. `pam_limits` applies them at login. The
**soft** limit is the one that applies, the **hard** limit is the ceiling the
user cannot cross.

## The course

The examples below deal with the `nodeops` user, with the `nproc` item and with
demonstration systemd units: the challenge will ask you for another account,
another item and other values. The point is to learn the method and to know how
to prove the result, not to copy a line. All the outputs come from an AlmaLinux
10.

### Soft, hard, and who tells the truth

Every limit exists as two values: the **soft** one, actually applied and which
the user may raise up to the **hard** one, the absolute ceiling that cannot be
exceeded without privilege. `ulimit -a` lists everything, `-S` and `-H` target
one or the other, `-n` designates `nofile` (open files) and `-u` designates
`nproc` (processes per user):

```bash
ulimit -Sn ; ulimit -Hn     # 1024 then 524288
ulimit -Su ; ulimit -Hu     # 3351 then 3351
```

These values are those of **your session**. For an already running process, the
only source of truth is the kernel, exposed in `/proc/<pid>/limits`, which
`prlimit` knows how to read cleanly:

```bash
sudo prlimit --pid 1 --nofile
sudo grep -E "Max processes|Max open files" /proc/1/limits
```

```text
RESOURCE DESCRIPTION                    SOFT       HARD UNITS
NOFILE   max number of open files 1073741816 1073741816 files
Max processes             3351                 3351                 processes
Max open files            1073741816           1073741816           files
```

Remember the gap: your shell is at 1024 open files, `systemd` (PID 1) is above
a billion. Two processes on the same machine do not have the same ceilings,
because they do not get them from the same source.

### A durable per-user limit: limits.d and pam_limits

A value set with `ulimit` dies with the terminal. For it to survive
reconnections, you declare it in a dedicated file under
`/etc/security/limits.d/`, which the `pam_limits` module applies at login. Four
fields per line: the domain (a user, a group with `@`, `*` for everyone), the
type (`soft` or `hard`), the item and the value.

```bash
sudo useradd -m nodeops
sudo tee /etc/security/limits.d/70-nodeops.conf <<'EOF'
nodeops  soft  nproc  30
nodeops  hard  nproc  60
EOF
sudo runuser -l nodeops -c 'ulimit -Su; ulimit -Hu'
```

```text
30
60
```

`runuser -l` (like `su -`) opens a **real session**: this is where `pam_limits`
steps in. On this AlmaLinux 10, `/etc/pam.d/su` and `/etc/pam.d/sudo` both
include `system-auth`, which loads `pam_limits.so`: a `sudo -u nodeops bash -c
'ulimit -Su'` therefore also returns `30`. Do not rely on that detail, it
depends on the distribution's PAM stack; always test in a login session, it is
the only guaranteed case.

What never changes, on the other hand, is that an **already running process
keeps the limits it had at startup**. Let us modify the file while a process is
running:

```bash
sudo sed -i 's/nproc  30/nproc  45/' /etc/security/limits.d/70-nodeops.conf
sudo grep 'Max processes' /proc/$(pgrep -u nodeops -x sleep | head -1)/limits
sudo runuser -l nodeops -c 'ulimit -Su'
```

```text
Max processes             30                   60                   processes
45
```

The live process stayed at 30, the new session sees 45. This is exactly the
"but I did change the file" pattern: you had to open a new session.

A limit you have never seen bite teaches nothing. `nproc` is now 45 for
`nodeops`: let us ask it for 60 processes.

```bash
sudo runuser -l nodeops -c 'for i in $(seq 1 60); do sleep 20 & done; wait'
```

```text
-bash: fork: retry: Resource temporarily unavailable
[...]
-bash: fork: Resource temporarily unavailable
```

The shell did not crash, nor did the machine: the kernel simply refused the
`fork()` calls beyond the ceiling. That is the whole point of a limit, turning
a global collapse into a local refusal. Clean up afterwards with `sudo pkill -u
nodeops sleep`.

### Three families of constraints that get confused

On a service, "limiting" covers three different mechanisms, with three
different symptoms when they bite. Mixing them up means looking for a failure
in the wrong place.

| Family | Unit directives | Mechanism | Symptom when exceeded |
|---|---|---|---|
| Per-cgroup resources | `MemoryMax`, `CPUQuota`, `TasksMax` | cgroup v2, applied by the kernel to the group | process killed (`oom-kill`), slowed down, or `fork` refused |
| Limits inherited from ulimit | `LimitNOFILE`, `LimitNPROC` | `rlimit` set on the process at startup | system call in error: `Too many open files` |
| Access hardening | `ProtectSystem`, `PrivateTmp`, `ReadOnlyPaths`, `NoNewPrivileges` | namespaces and dedicated mounts | `Read-only file system`, file not found |

What they have in common: none of the three reads
`/etc/security/limits.conf`. A service started by systemd does not go through
the PAM stack, so it completely ignores `limits.d`. Let us check that on a unit
running as `nodeops` with no directive at all:

```bash
sudo tee /etc/systemd/system/atelier-fd.service <<'EOF'
[Unit]
Description=Atelier - service with no Limit* directive
[Service]
Type=simple
User=nodeops
ExecStart=/bin/sleep 600
EOF
sudo systemctl daemon-reload && sudo systemctl start atelier-fd.service
sudo grep 'Max processes' /proc/$(systemctl show -p MainPID --value atelier-fd.service)/limits
systemctl show --property=DefaultLimitNPROC
```

```text
Max processes             3351                 3351                 processes
DefaultLimitNPROC=3351
```

The service does run as `nodeops`, and yet it is at 3351, not at 45: it
inherited the **manager's default**, not `limits.d`. This is the most frequent
mistake on this subject.

### The ulimit family in a unit: LimitNOFILE

For a service, the limit is therefore set in the unit. Let us deliberately
tighten the open-files ceiling to see it give way, with a script that opens
files until it fails and exits with code 24:

```ini
[Service]
Type=oneshot
User=nodeops
LimitNOFILE=64
ExecStart=/usr/local/bin/atelier-ouvre-fd
```

```bash
sudo systemctl daemon-reload && sudo systemctl start atelier-fd.service
sudo journalctl -u atelier-fd.service -n 4 --no-pager -o short
```

```text
Job for atelier-fd.service failed because the control process exited with error code.
[...] atelier-ouvre-fd[23651]: stoppe apres 61 fichiers : [Errno 24] Too many open files: '/etc/hostname'
[...] systemd[1]: atelier-fd.service: Main process exited, code=exited, status=24/n/a
[...] systemd[1]: atelier-fd.service: Failed with result 'exit-code'.
```

Three pieces of information to read: the application message (`Too many open
files`), the **exit code** kept by systemd (`status=24`), and the result
(`exit-code`). The count stops at 61 and not 64, because standard input, output
and error already take three descriptors.

Careful when reading the properties: `systemctl show` distinguishes the hard
limit from the soft one. Here `systemctl show -p LimitNOFILE -p LimitNOFILESoft
atelier-fd.service` answers `LimitNOFILE=64` and `LimitNOFILESoft=64`, whereas
with no directive the same pair gave `524288` and `1024`: the classic "soft
1024" seen on throttled servers.

### The cgroup family: MemoryMax, and what the kernel really kept

`MemoryMax` caps the memory of the unit's **control group**. A demonstration
service that allocates 8 MiB every 200 ms, under 48 MiB:

```ini
[Service]
Type=simple
MemoryMax=48M
ExecStart=/usr/local/bin/atelier-mange-ram 0
```

As long as it stays under the ceiling, the cgroup tree shows the accepted
constraint and the current consumption:

```bash
sudo cat /sys/fs/cgroup/system.slice/atelier-ram.service/memory.max
systemctl show -p MemoryMax -p MemoryCurrent atelier-ram.service
systemd-cgls /system.slice/atelier-ram.service --no-pager
```

```text
50331648
MemoryCurrent=28487680
MemoryMax=50331648
CGroup /system.slice/atelier-ram.service:
└─23843 /usr/bin/python3 /usr/local/bin/atelier-mange-ram 24
```

`48M` is written `50331648` bytes on the kernel side: the value shown by
`systemctl show` is the one actually set in the cgroup, not the text of the
unit. Now let the service go over:

```bash
systemctl status atelier-ram.service --no-pager
```

```text
Active: failed (Result: oom-kill) since Wed 2026-07-22 15:48:59 UTC; 2s ago
Process: 23969 ExecStart=/usr/local/bin/atelier-mange-ram 0 (code=killed, signal=KILL)
Mem peak: 48M
[...] systemd[1]: atelier-ram.service: A process of this unit has been killed by the OOM killer.
[...] systemd[1]: atelier-ram.service: Main process exited, code=killed, status=9/KILL
```

The symptom has nothing to do with the one of `LimitNOFILE`: no application
error code, a `SIGKILL` and an `oom-kill` result. The killer is the **cgroup**
one: only the service died, the machine did not flinch. The two other
directives of the family are checked the same way:

```bash
systemctl show -p CPUQuotaPerSecUSec -p TasksMax atelier-cpu.service   # CPUQuota=20% TasksMax=25
sudo cat /sys/fs/cgroup/system.slice/atelier-cpu.service/cpu.max /sys/fs/cgroup/system.slice/atelier-cpu.service/pids.max
```

```text
CPUQuotaPerSecUSec=200ms
TasksMax=25
20000 100000
25
```

`systemd-cgtop --depth=2 -b -n 1 --order=memory` ranks the cgroups by
consumption, handy to find who weighs the most before setting a ceiling.

### Access hardening: PrivateTmp and ProtectSystem

Third family: it counts nothing, it **hides or locks**. `PrivateTmp=yes` gives
the service a `/tmp` of its own. Let us have it write a file there:

```ini
[Service]
Type=oneshot
PrivateTmp=yes
ExecStart=/bin/sh -c "echo trace-du-service > /tmp/marqueur-atelier.txt; ls -l /tmp"
```

```text
# seen by the service, in the journal
-rw-r--r--. 1 root root 17 Jul 22 15:49 marqueur-atelier.txt

# seen from the system, at the same moment
$ ls -l /tmp/marqueur-atelier.txt
ls: cannot access '/tmp/marqueur-atelier.txt': No such file or directory
```

The file exists, but in a private mount whose name gives the unit away:

```bash
sudo sh -c 'cat /tmp/systemd-private-*-atelier-tmp.service-*/tmp/marqueur-atelier.txt'
```

```text
trace-du-service
```

This is what puzzles people looking for a file a service claims to have
written. `ProtectSystem=strict`, for its part, remounts the whole filesystem
read-only except the paths listed in `ReadWritePaths`:

```ini
[Service]
ProtectSystem=strict
ReadWritePaths=/var/log
ExecStart=/bin/sh -c "echo essai > /etc/atelier-marqueur.conf"
```

```text
sh[24181]: /bin/sh: line 1: /etc/atelier-marqueur.conf: Read-only file system
systemd[1]: atelier-lecture.service: Main process exited, code=exited, status=1/FAILURE
```

The service nevertheless runs as `root`: hardening does not depend on the UID,
it acts lower down. The file exists nowhere afterwards.

### Check and troubleshoot

A directive that is **written** is not a directive that is **active**. A
misspelled key is silently ignored in the file, and systemd keeps its default:

```bash
sudo systemd-analyze verify /etc/systemd/system/atelier-typo.service
systemctl show -p MemoryMax atelier-typo.service
```

```text
/etc/systemd/system/atelier-typo.service:6: Unknown key 'MemoryMaximum' in section [Service], ignoring.
MemoryMax=infinity
```

The reflex is always the same: compare what is **configured** with what is
**actually applied**.

| Symptom | Likely cause | Where to look |
|---|---|---|
| A service stays at the default despite `limits.d` | Services do not go through `pam_limits` | Set `Limit*` in the unit, `daemon-reload`, restart |
| A new limit is not taken into account | Session or processes opened before the change | Open a new session; `/proc/<pid>/limits` for the live process |
| An account cannot raise its limit | It aims above its hard limit | Raise the `hard` value (requires root) |
| The directive seems to have no effect | Unknown key, ignored at load time | `systemd-analyze verify`, then `systemctl show -p <property>` |

Three commands are enough to decide: `systemctl show -p <property> <unit>` for
the value kept by systemd, `/sys/fs/cgroup/system.slice/<unit>/` for what the
kernel wrote, and `/proc/<pid>/limits` for what the process undergoes. Finally,
when a demonstration service is in `failed`, it stays listed by `systemctl
list-units --failed` until a `systemctl reset-failed`: deleting the unit and
running `daemon-reload` is not enough to erase the trace.
