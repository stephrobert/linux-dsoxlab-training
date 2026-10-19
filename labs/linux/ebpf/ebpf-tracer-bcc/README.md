# Lab: trace the kernel with eBPF tools

## Reminder

[**bpftrace on the companion guide**](https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/tracer/bpftrace/)

eBPF lets you load small programs into the kernel to **observe** what it does:
every file opened, every program launched, every connection. Nothing is changed
on the machine and nothing has to be installed on the application side: you
watch the system calls go by. This lab teaches you to read those traces with two
families of tools: **BCC** (a collection of ready-made commands) and
**bpftrace** (a one-line language).

## The course

The examples below observe throwaway commands (`cat`, `ls`, `date`) that you
start by hand: the challenge will give you a different problem, where it is up
to you to find what to look at. Every output reproduced here was obtained on
AlmaLinux 10.2 (kernel 6.12, `bcc-tools 0.35.0`, `bpftrace 0.24.2`) and on
Ubuntu 24.04 (kernel 6.8, `bpfcc-tools 0.29.1`, `bpftrace 0.20.2`).

### You have to be root, always

An eBPF program is loaded into the kernel: only `root` can do that. Without
`sudo`, both families refuse, each in its own way:

```bash
bpftrace -e 'BEGIN { exit(); }'
```

```text
ERROR: bpftrace currently only supports running as the root user.
```

The BCC tools fail more noisily: a `could not open bpf map: infotmp, error:
Operation not permitted` followed by a Python traceback. If you see a Python
traceback ending with `Operation not permitted`, rerun with `sudo`, there is
nothing else to look for. The `kernel.unprivileged_bpf_disabled` setting explains
this behaviour: it is `2` on both distributions, which forbids eBPF to ordinary
users.

### Install BCC, and where the tools are

Package names and command names differ between distribution families. On
AlmaLinux 10:

```bash
sudo dnf install bcc-tools
rpm -ql bcc-tools | grep -E '/(open|exec)snoop$'
```

```text
/usr/share/bcc/tools/execsnoop
/usr/share/bcc/tools/opensnoop
```

The tools live in `/usr/share/bcc/tools/`, a directory that is **not in the
`PATH`**: a bare `opensnoop` answers `command not found`. You call them by their
full path, or add the directory to the `PATH` of your session.

On Ubuntu 24.04 the package is called `bpfcc-tools` and every command carries the
`-bpfcc` suffix, in a directory that is already in the `PATH`: `opensnoop-bpfcc`,
`execsnoop-bpfcc`. The options are the same, only the name changes. The manual
pages are named `bcc-opensnoop` on AlmaLinux and `opensnoop-bpfcc` on Ubuntu.

One installation detail is worth knowing. The `bcc-tools` package pulls
`kernel-devel` as a dependency, and dnf installs the **most recent** version, not
the one matching the running kernel. When this lab was prepared, the active
kernel was `6.12.0-211.64.1` while `kernel-devel` arrived as `211.65.1`:

```bash
uname -r
rpm -q kernel-devel
ls -L /lib/modules/$(uname -r)/build
```

In that case the `/lib/modules/<active kernel>/build` link points nowhere. The
tools still worked: BCC rebuilt kernel headers by itself in
`/tmp/kheaders-<active kernel>` from the `kheaders` kernel module. If a tool
complains that it cannot find the kernel headers, first compare `uname -r` with
`rpm -q kernel-devel`: a reboot onto the most recent kernel closes the gap.

### Opened files: `opensnoop`

`opensnoop` prints every file opening as it happens, with the name of the program
that asked for it. Isolate it on the `cat` command so the reading is not
drowned. In one terminal:

```bash
sudo /usr/share/bcc/tools/opensnoop -n cat
```

In a second terminal, run `cat /etc/hostname`. The first terminal prints:

```text
PID    COMM               FD ERR PATH
25205  cat                 3   0 /etc/ld.so.cache
25205  cat                 3   0 /lib64/libc.so.6
25205  cat                 3   0 /etc/hostname
```

Each column has a precise meaning:

- **PID**: the process that opens, handy to find it again with `ps`.
- **COMM**: the program name (limited to 15 characters by the kernel).
- **FD**: the descriptor obtained, or `-1` if the opening failed.
- **ERR**: the associated error code (`2` for file not found, for example).
- **PATH**: the path requested, as the program wrote it.

You can see that `cat` first opens two libraries to start, and only then the
requested file: startup noise always surrounds the useful information. Three
options help reduce it. `-n cat` keeps only programs whose name **contains**
`cat`. `-p 25205` follows a single process. `-d 10` stops the trace after ten
seconds, so you do not have to interrupt it by hand.

A redirection trap: if you send the output to a file, Python buffers the output
and a stop by `timeout` loses everything that had not been written yet. Set
`PYTHONUNBUFFERED=1` in front of the command, or prefer `-d`.

### Launched programs: `execsnoop`

`execsnoop` does the same for program launches: one line per `execve`, with the
parent. Start it in one terminal, then run
`bash -c 'ls /etc > /dev/null; date > /dev/null'` in a second one:

```bash
sudo /usr/share/bcc/tools/execsnoop
```

```text
COMM             PID     PPID    RET ARGS
bash             25219   25190      0 /bin/bash -c ls /etc > /dev/null; date > /dev/null
ls               25220   25219      0 /bin/ls /etc
date             25221   25219      0 /bin/date
```

The column that matters here is **PPID**: the number of the parent process. The
`bash` with PID 25219 launched two children, `ls` and `date`, which both carry
`PPID 25219`. The `bash` line itself shows a different parent (25190, the session
shell). When a program regularly launches commands, its children scroll by with a
constant PPID: that number is the thread to pull. `RET` is `0` when the launch
succeeded.

To go from a PID to a program name, `ps` is enough:

```bash
ps -o pid,ppid,comm,args -p 25219
```

```text
    PID    PPID COMMAND         COMMAND
  25219   25190 bash            bash -c ls /etc > /dev/null; date > /dev/null
```

On a real machine, `execsnoop` shows much more than your command: system tasks
also launch programs continuously. Filter with `-n` (a pattern searched in the
launched command) or `-P` (PID of the parent), otherwise the information drowns.

### bpftrace: the same thing in one line

`bpftrace` provides no ready-made tools: you describe the event to observe in a
mini-language. To reproduce `opensnoop` on `cat` in one line:

```bash
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat /comm == "cat"/ { printf("%s %s\n", comm, str(args->filename)); }'
```

```text
Attached 1 probe
cat /etc/ld.so.cache
cat /lib64/libc.so.6
cat /etc/hostname
```

Read the line from left to right. `tracepoint:syscalls:sys_enter_openat` is the
**probe**: it fires on every `openat` system call. The filter between slashes
(`/comm == "cat"/`) keeps only calls made by `cat`. The block between braces says
what to print: `comm` (the program name) and `str(args->filename)` (the requested
path, converted to text). On Ubuntu 24.04, bpftrace 0.20 prints
`Attaching 1 probe...` instead of `Attached 1 probe`: only the wording changes.

The two families complement each other. BCC answers the common questions right
away. bpftrace lets you ask a question that no tool covers, at the price of a bit
of syntax.

### Check that the tool really works

An installed tool is not a working tool: loading the eBPF program can fail for a
permissions or headers reason, and `--help` will not show it, because it prints
before anything is loaded. The shortest test is to run the tool for one second:

```bash
sudo /usr/share/bcc/tools/opensnoop -d 1 > /dev/null; echo $?
```

```text
0
```

A return code of `0` proves the tool compiled, loaded its program into the kernel
and stopped cleanly. This is the very check the challenge applies.
