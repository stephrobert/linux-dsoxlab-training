# Lab: inventory the loaded eBPF programs and find what carries them

## Recap

[**The eBPF attack surface in the companion guide (FR)**](https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/surface-attaque-bpf/)

eBPF lets you load small programs into the Linux kernel. They run there with
extended rights, which makes them a valuable observability tool and a prime place
to hide. The good news is that **every loaded program can be seen**: the `bpftool`
command lists them, whichever tool loaded them. This lab teaches the four steps
of an inventory: **list** the programs, **find the process** holding one of them,
**go up to the systemd unit** that starts that process, then **stop** that unit so
it does not come back. The classic trap is not finding the program, it is
believing it is gone because its process was killed.

## The course

The examples below use demonstration probes and services (`demo-sonde`,
`demo-horloge`, `demo-veilleur`) that you create and then delete yourself: the
challenge poses a different problem, it is up to you to transfer what you have
seen. The outputs reproduced here were obtained on AlmaLinux 10.2 (kernel 6.12,
`bpftool` 7.7) and on Ubuntu 24.04 (kernel 6.8, `bpftool` 7.4), on a fresh
machine. On the lab machine, the list of the first example will have one more
line than below: that is what the challenge asks you to elucidate, do not touch
it before you have finished the course. Program and process numbers change at
every attempt.

Both tools are already installed by the lab preparation. To check, and to know
which version answers:

```bash
command -v bpftool bpftrace
sudo bpftool version
```

```text
/usr/sbin/bpftool
/usr/bin/bpftrace
bpftool v7.7.0
using libbpf v1.7
features: llvm, skeletons
```

The output comes from AlmaLinux; Ubuntu 24.04 gives `bpftool v7.4.0` and `libbpf
v1.4`. Listing programs needs root rights, hence the `sudo` everywhere in this
lab.

### List the loaded programs: `bpftool prog show`

The kernel keeps a registry of every eBPF program it holds, and `bpftool prog
show` prints it. Each program takes a block: an identity line, then indented
detail lines. The next command keeps only the first lines and counts the programs
**by type**, the second field:

```bash
sudo bpftool prog show | grep -E '^[0-9]+:' | awk '{print $2}' | sort | uniq -c | sort -rn
```

```text
     12 cgroup_skb
      7 cgroup_device
      1 socket_filter
      1 lsm
```

Here is what Ubuntu 24.04 gives:

```text
      6 cgroup_skb
      6 cgroup_device
      1 tracing
```

A program's **type** says where in the kernel it is hooked and what it may do:
`cgroup_skb` filters the network packets of a group of processes, `cgroup_device`
controls access to devices, `lsm` plugs into security decisions, `kprobe` hooks a
kernel function, `perf_event` fires on a performance event. The list of a healthy
idle machine is therefore **short and explainable**, and whatever departs from it
deserves an investigation. To read a line in detail, add an identifier:

```bash
sudo bpftool prog show id 47
```

```text
47: lsm  name restrict_filesystems  tag 7673068478f99ef8  gpl
	loaded_at 2026-10-17T05:44:08+0000  uid 0
	xlated 520B  jited 297B  memlock 4096B  map_ids 22
	btf_id 48
	pids systemd(1)
```

The first line gives, in order, the **identifier** (`47`), the **type** (`lsm`),
the program **name**, its **fingerprint** (`tag`) and its license (`gpl`). The
following lines give the load date, the user who loaded it (`uid 0` is root), the
code size and, depending on the tool version, the `pids` line. On AlmaLinux it
names the process holding the program: here `systemd`, PID 1. On Ubuntu 24.04
that line does not exist. The `sd_fw_egress`, `sd_fw_ingress` and `sd_devices`
programs have a name starting with `sd_`: they are systemd's, which loads them to
filter the network and the devices of its services.

### Load two throwaway probes to see a "foreign" program

To see what a program nobody deployed looks like, we load two with `bpftrace`, a
tool that compiles a one-line probe into an eBPF program and loads it. The
`systemd-run` command starts each in a **temporary** unit that we name ourselves:

```bash
sudo systemd-run --unit=demo-sonde bpftrace -e 'kprobe:vfs_read { @n = count(); }'
sudo systemd-run --unit=demo-horloge bpftrace -e 'profile:hz:19 { @n = count(); }'
```

```text
Running as unit: demo-sonde.service; invocation ID: 0272031155e8484ea48befef263010a3
Running as unit: demo-horloge.service; invocation ID: a58728f60e2145659cab0afcc47aebba
```

The first probe counts the calls to the kernel `vfs_read` function; the second
fires 19 times per second on the clock. Let us list again, leaving out systemd's
known noise:

```bash
sudo bpftool prog show | grep -E '^[0-9]+:' | grep -vE 'cgroup_(skb|device)'
```

```text
47: lsm  name restrict_filesystems  tag 7673068478f99ef8  gpl
69: socket_filter  tag 6418a962837b40fa
260: perf_event  name profile_hz_19_1  tag 3037f536e6e8b280  gpl
268: kprobe  name kprobe_vfs_read_1  tag 3037f536e6e8b280  gpl
```

Two programs appeared: one of type `perf_event` and one of type `kprobe`. Note
that **the type does not depend on the service**: it depends on the kind of probe
`bpftrace` compiled. On Ubuntu 24.04, `bpftrace` 0.20 names the programs
differently, but the types are the same:

```text
2: tracing  name hid_tail_call  tag 7cc47bbf07148bfe  gpl
64: perf_event  name 19  tag 8c75940e7e21306d  gpl
68: kprobe  name vfs_read  tag 8c75940e7e21306d  gpl
```

### Find the process that holds a program

On AlmaLinux, the `pids` line of the detail answers directly:

```bash
sudo bpftool prog show id 268
```

```text
268: kprobe  name kprobe_vfs_read_1  tag 3037f536e6e8b280  gpl
	loaded_at 2026-10-17T05:51:41+0000  uid 0
	xlated 512B  jited 296B  memlock 4096B  map_ids 119,120,122,123
	btf_id 316
	pids bpftrace(19797)
```

On Ubuntu 24.04, the same detail has no `pids` line. You then need another entry
of the tool, `bpftool perf show`, which lists the **processes holding a probe**
attached through the performance-event mechanism (kprobes, uprobes and
tracepoints):

```bash
sudo bpftool perf show
```

```text
pid 4408  fd 7: prog_id 68  kprobe  func vfs_read  offset 0
```

The line gives the process **PID**, the file descriptor number (`fd`), the
**program identifier** (`prog_id`) and what the probe is attached to. But this
command does not see everything: the `profile` probe, of type `perf_event`, is
not in its list. It does not show in `bpftool link show` on Ubuntu either. On
AlmaLinux, that `link show` does list the links with their processes, and it
reminds you that **a link has its own type**:

```bash
sudo bpftool link show | grep -A3 'prog 268'
```

```text
25: perf_event  prog 268  
	kprobe ffffffff87116ee4 vfs_read  
	bpf_cookie 0
	pids bpftrace(19797)
```

Program `268` is of type `kprobe`, but the link attaching it is of type
`perf_event`. When asked for "the type of a program", the first line of `bpftool
prog show` is authoritative, not that of a link.

What remains is the method that works everywhere, whatever the version: a process
holding an eBPF program keeps open a file descriptor whose target is called
`anon_inode:bpf-prog`. The `/proc/<pid>/fd` directory exposes them, and `find`
finds them all at once:

```bash
sudo find /proc -maxdepth 3 -path '/proc/[0-9]*/fd/*' -lname 'anon_inode:bpf-prog' 2>/dev/null
```

```text
/proc/1/fd/14
/proc/1/fd/61
/proc/1/fd/63
...
/proc/19797/fd/8
/proc/19801/fd/8
```

PID 1 is `systemd`, which holds the many system programs; it is no surprise. The
two other PIDs are those of our probes. A PID that neither `systemd` nor you can
explain is the one to examine.

Finally, every `bpftool` can print JSON with the `--json` (or `-j`) option, easier
to filter than a column output. With `jq`, present on both lab machines, systemd's
noise is dropped:

```bash
sudo bpftool prog show --json | jq -c '.[] | select(.type | startswith("cgroup") | not) | {id,type,name,pids}'
```

```text
{"id":47,"type":"lsm","name":"restrict_filesystems","pids":[{"pid":1,"comm":"systemd"}]}
{"id":69,"type":"socket_filter","name":null,"pids":null}
{"id":260,"type":"perf_event","name":"profile_hz_19_1","pids":[{"pid":19801,"comm":"bpftrace"}]}
{"id":268,"type":"kprobe","name":"kprobe_vfs_read_1","pids":[{"pid":19797,"comm":"bpftrace"}]}
```

On Ubuntu 24.04, the `pids` field is `null`, and `bpftool perf show` or
`/proc/<pid>/fd` provide the PID.

### From the process to the systemd unit

A PID does not say who started the process. Under systemd, each service runs in
its own **cgroup**, and the unit name is its last element. Three ways to read it,
with the PID `19797` of the example:

```bash
cat /proc/19797/cgroup
ps -o unit= -p 19797
systemctl status 19797 --no-pager | head -4
```

```text
0::/system.slice/demo-sonde.service
demo-sonde.service
● demo-sonde.service - [systemd-run] /bin/bpftrace -e "kprobe:vfs_read { @n = count(); }"
     Loaded: loaded (/run/systemd/transient/demo-sonde.service; transient)
  Transient: yes
     Active: active (running) since Sat 2026-10-17 05:51:41 UTC; 4s ago
```

The `systemctl status` command accepts a PID directly instead of a unit name: it
is the shortest. It also gives the unit file (`Loaded`) and its command line,
enough to know what was started.

### Stop a unit, and what that unloads

The kernel releases an eBPF program when no process and no pinning point holds it
any more. Stopping the unit kills its process, hence unloads the program:

```bash
sudo systemctl stop demo-sonde demo-horloge
sudo bpftool prog show | grep -E '^[0-9]+:' | grep -vE 'cgroup_(skb|device)'
sudo bpftool perf show
```

```text
47: lsm  name restrict_filesystems  tag 7673068478f99ef8  gpl
69: socket_filter  tag 6418a962837b40fa
```

Both probes are gone from the list, and `bpftool perf show` returns nothing. The
units created by `systemd-run` are temporary: once stopped, they exist nowhere,
which makes them unrepresentative of a real service. That is what we look at now.

### Keep a service from coming back

A real service lives in a unit file, often with `Restart=always` and an automatic
start. Let us create a demonstration one that does nothing useful:

```bash
sudo tee /etc/systemd/system/demo-veilleur.service >/dev/null <<'EOF'
[Unit]
Description=Veilleur de demonstration

[Service]
ExecStart=/usr/bin/sleep infinity
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now demo-veilleur.service
systemctl is-enabled demo-veilleur
systemctl is-active demo-veilleur
```

```text
Created symlink '/etc/systemd/system/multi-user.target.wants/demo-veilleur.service' → '/etc/systemd/system/demo-veilleur.service'.
enabled
active
```

The unit has **two independent states**: it is *active* (running now) and
*enabled* (it will start at the next boot, through the link created in
`multi-user.target.wants`). They are set separately. Killing the process is
useless, because of `Restart=always`:

```bash
ancien=$(systemctl show -p MainPID --value demo-veilleur)
sudo kill "$ancien"; sleep 1
echo "ancien $ancien, nouveau $(systemctl show -p MainPID --value demo-veilleur)"
```

```text
ancien 19970, nouveau 19979
```

Systemd started a new process within a fraction of a second. You have to stop
**the unit**, not its process. But a stop alone still lets the unit start at the
next boot:

```bash
sudo systemctl stop demo-veilleur
systemctl is-active demo-veilleur
systemctl is-enabled demo-veilleur
```

```text
inactive
enabled
```

It is stopped but still `enabled`: it will come back at reboot. The `systemctl
disable` command removes the link, and its `--now` option does the stop and the
disabling in one go:

```bash
sudo systemctl disable demo-veilleur
systemctl is-enabled demo-veilleur
```

```text
Removed '/etc/systemd/system/multi-user.target.wants/demo-veilleur.service'.
disabled
```

The `disabled` state means the unit exists but no longer starts by itself. A
third state, `masked`, forbids even a manual start: masking replaces the unit with
a link to `/dev/null`. But `systemctl mask` **refuses to overwrite a real unit
file**:

```bash
sudo systemctl mask demo-veilleur
```

```text
Failed to mask unit: File '/etc/systemd/system/demo-veilleur.service' already exists
```

Masking therefore only applies to a unit with no file in `/etc/systemd/system`,
for instance a package's (file under `/usr/lib/systemd/system`), or after the file
was removed. **Removal** is the other way, and it hides a trap. Let us start the
unit again, then delete its file **without having stopped it**:

```bash
sudo systemctl start demo-veilleur
sudo rm /etc/systemd/system/demo-veilleur.service
sudo systemctl daemon-reload
systemctl is-active demo-veilleur
systemctl is-enabled demo-veilleur
pgrep -a sleep
```

```text
active
not-found
21088 /usr/bin/sleep infinity
```

The file is gone (`not-found`), but the process still runs: removing the unit
does not kill what is already running. Hence the safe order: **stop first**,
disable next, remove last if needed. Let us finish the demo cleanly. The orphan
process stops through its unit name, which is still loaded:

```bash
sudo systemctl stop demo-veilleur
sudo systemctl mask demo-veilleur
systemctl is-enabled demo-veilleur
sudo systemctl unmask demo-veilleur
ls /etc/systemd/system | grep demo
```

```text
Created symlink '/etc/systemd/system/demo-veilleur.service' → '/dev/null'.
masked
Removed '/etc/systemd/system/demo-veilleur.service'.
Removed '/etc/systemd/system/multi-user.target.wants/demo-veilleur.service'.
```

With the file deleted, masking becomes possible (`masked` state), and `unmask`
removes both the link to `/dev/null` and the start link left dangling in
`multi-user.target.wants`. The machine is back to its state before the
demonstration.

### What an inventory must not break

An inventory is for deciding, not for stopping everything. The `sd_*` programs
and the kernel's are **legitimate**: unload them and the machine's services lose
their network filtering or their device control. That is why you isolate the
culprit before acting: one program, one PID, one unit. And afterwards you check
again that the list has not been emptied of what the system loads by itself.
