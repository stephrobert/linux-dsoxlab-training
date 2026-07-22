# Lab — mapping Linux: kernel, distribution, free software

## Reminder

[**Linux fundamentals**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/)

Strictly speaking, Linux is a **kernel**: the central program written by Linus
Torvalds in 1991, distributed under the GPL licence, which manages the hardware,
the memory, the processes and the files. In everyday use, "Linux" means the
complete system, and that system is in fact provided by a **distribution** that
assembles libraries, utilities, an init system and a package manager around the
kernel. The guide lays down this vocabulary, the layered architecture and the
seven boot stages. This lab demonstrates them on a real machine: the kernel can
be seen there as a file, and the two version numbers that everybody confuses are
printed side by side.

This is the first lab of the track, it opens the way and does not cover
everything. Opening a terminal and reading its prompt is the subject of
`l1-first-terminal`, the structure of a command that of `l1-read-a-command`, the
documentation that of `l1-get-help`, the directory tree that of
`l1-linux-filesystem`: none of that is repeated here.

## The course

The commands below answer no question of the challenge: they describe the
machine on which this course was written, not yours, and **every value printed
will be different on your machine**. What matters is not the number, it is
knowing which command produces it and what it means. All of them are
**read-only**: none writes, none needs `sudo`, none installs anything. You can
run them without the slightest risk.

The outputs reproduced here were taken on a workstation running
**Ubuntu 24.04.2 LTS**, kernel `6.8.0-134-generic`, in a French locale, hence
the dates of the form `juin 26 18:36`.

### The kernel is a file, and you can look at it

People speak of the kernel as an abstraction. It is nonetheless an ordinary
file, sitting on the disk, that the boot loader reads and puts in memory (stage
2 of the boot in the guide). It carries a conventional name, `vmlinuz`, and
lives in `/boot`:

```bash
ls -l /boot/vmlinuz*
```

```text
lrwxrwxrwx 1 root root       25 juil. 18 06:30 /boot/vmlinuz -> vmlinuz-6.8.0-136-generic
-rw------- 1 root root 15042952 juin  26 18:36 /boot/vmlinuz-6.8.0-134-generic
-rw------- 1 root root 15063432 juil.  1 21:50 /boot/vmlinuz-6.8.0-136-generic
lrwxrwxrwx 1 root root       25 juil. 18 06:30 /boot/vmlinuz.old -> vmlinuz-6.8.0-134-generic
```

Fifteen megabytes, a date, `-rw-------` permissions that reserve it for the
administrator: you can **list** it without privilege, but not read it, and
`file` on that file answers `regular file, no read permission`.

Look more closely: there are **two** kernels installed, and the `/boot/vmlinuz`
link points at the more recent one, `6.8.0-136-generic`. Which one is actually
running?

```bash
uname -r
cat /proc/cmdline
```

```text
6.8.0-134-generic
BOOT_IMAGE=/vmlinuz-6.8.0-134-generic root=/dev/mapper/ubuntu--vg-ubuntu--lv ro
```

The running kernel is the `-134`, not the `-136`: `/proc/cmdline` gives the
exact line the boot loader passed to the kernel at the last boot, and it names
the file that was loaded. Remember the lesson, it will serve you your whole
career: **installing a kernel does not make it run**. The new one waits on the
disk, and only a reboot switches to it. That is why a kernel security update
ends in a "reboot required" that must not be dodged.

### Two version numbers that have nothing to do with each other

Here is the beginner's number one confusion. Compare these two outputs:

```bash
uname -r
cat /etc/os-release
```

```text
6.8.0-134-generic
PRETTY_NAME="Ubuntu 24.04.2 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.2 LTS (Noble Numbat)"
VERSION_CODENAME=noble
[...]
ID_LIKE=debian
[...]
```

`6.8.0` is the version of the **kernel**, `24.04` that of the
**distribution**: two projects, two teams, two rhythms, two numbering schemes
with no relation whatsoever. The version table in the guide shows it well,
Ubuntu numbers by year and month of release (26.04 came out in April 2026),
where the kernel follows its own sequence. Answering "I am on 24.04" to the
question "which kernel version?" is a misunderstanding, and the other way round
too.

The fields of `/etc/os-release` you will read most often:

| Field | What it gives |
|---|---|
| `PRETTY_NAME` | the human-readable name, to be displayed |
| `NAME` | the name of the distribution, without the version |
| `VERSION_ID` | the version, in a form a script can compare |
| `VERSION_CODENAME` | the code name of the version (`noble` here) |
| `ID` | the short, normalised identifier, the one a script tests |
| `ID_LIKE` | the family the distribution derives from (`debian` here) |

`ID_LIKE` is the most useful in practice: it says that Ubuntu derives from
Debian, and therefore that the commands of that family apply to it.

A single command prints both numbers together, on systems equipped with systemd
(`dpkg -S "$(command -v hostnamectl)"` confirms that `hostnamectl` is shipped by
the `systemd` package):

```bash
hostnamectl
```

```text
[...]
Operating System: Ubuntu 24.04.2 LTS
          Kernel: Linux 6.8.0-134-generic
    Architecture: x86-64
[...]
```

The operating system on one side, the kernel on the other, the hardware
architecture as a bonus. `uname -a` gives the same thing in a rawer form, on a
single line, adding the **build** date of the kernel by the distribution, which
is not the date it was installed on your machine.

### The kernel is not the first program you see

The kernel takes control of the hardware, then it starts a first program, and
that program is not itself. This is stage 6 of the boot described in the guide,
the famous **PID 1**:

```bash
ps -p 1 -o pid,comm,args
ls -l /sbin/init
```

```text
    PID COMMAND         COMMAND
      1 systemd         /sbin/init
lrwxrwxrwx 1 root root 22 juin   5 17:36 /sbin/init -> ../lib/systemd/systemd
```

Process number 1 is called `systemd`, it was started under the name
`/sbin/init`, and that path is only a symbolic link to the real program. Three
things follow: PID 1 is an **ordinary program** sitting on the disk, it is
**provided by the distribution** and not by the kernel, and it is therefore
**replaceable**. According to the guide, it is the one that manages everything
that follows.

The same logic holds for the smallest command. The guide describes the journey
of `ls`: the shell starts it, `ls` calls the C library, which translates into
system calls, the kernel answers. That journey can be read in the binary:
`ldd /usr/bin/ls` lists `libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6`, the **C
library** (here the GNU libc `2.39`, according to `ldd --version`). It is the
library, and not `ls`, that talks to the kernel. The kernel itself appears
nowhere in that list, and that is precisely the point: the border between user
space and kernel mode is only crossed through system calls.

### What a distribution adds to the kernel

A kernel on its own does nothing useful: it has no shell, no commands, no way to
install software. The guide lists what the distribution assembles around it.
Each brick can be identified on your machine:

| Brick | Role | Taken on the writing machine | Command |
|---|---|---|---|
| Package manager | install and update | `apt 2.8.3` | `apt --version` |
| Init system (PID 1) | start and supervise the services | `systemd 255` | `systemctl --version` |
| C library | interface between programs and kernel | GNU libc `2.39` | `ldd --version` |
| Base tools | handle files, text, processes | GNU coreutils `9.4` | `ls --version` |
| Shell | interpret your commands | GNU bash `5.2.21` | `bash --version` |

To which is added a brick that is not software but a **policy**: the choice of
versions, the pace of releases and the length of time during which the flaws
will be fixed. The assembly is not symbolic: on this workstation,
`dpkg-query -f '.\n' -W | wc -l` counts **1296 packages**, the whole distance
between "the Linux kernel" and "a Linux system". The guide sorts the server
distributions into two families, on concrete criteria:

| Criterion | Debian family | Red Hat family |
|---|---|---|
| Distributions | Debian, Ubuntu Server | RHEL, Rocky Linux, AlmaLinux |
| Package manager | `apt` (`.deb` packages) | `dnf` (`.rpm` packages) |
| Support length | Debian about 5 years, Ubuntu LTS 5 years (+5 in ESM) | RHEL 10 years |
| Cost | free of charge | RHEL paid by subscription, Rocky and Alma free of charge |
| Favourite ground | web, cloud, containers, homelab | enterprise, critical IT, RHCSA certification |
| Init | systemd | systemd |

The "Init" line is not there by chance: both families have **the same** init
system. What separates them comes down to the packages, the configuration paths
and the support policy, not to the architecture. The guide also mentions Alpine,
whose manager is `apk`, as well as Arch and openSUSE, which it gives as rare on
production servers without detailing them: this course will therefore say no
more about them.

### The vocabulary that muddles everything, one line per trap

- **Linux** is the kernel and nothing else: `uname -s` answers `Linux`, and
  speaks only about it.
- **GNU/Linux** means the complete team, Torvalds' kernel plus the tools of the
  GNU project. This is not a militant stance: it is what the machine answers to
  `uname -o`, and `ls --version` names its author in passing, Richard
  M. Stallman.
- **Kernel** and **operating system** are not synonyms: the second adds to the
  first a C library, an init, tools and a package manager.
- **Distribution** and **version** are not on the same level: Ubuntu is the
  distribution, `24.04` the version, `noble` the code name of that version.
- **Package** and **software** are not the same thing: `dpkg -S /usr/bin/ls`
  answers `coreutils`, so `ls` has no package of its own, it travels in a parcel
  that holds dozens of them. That parcel carries its own number,
  `9.4-3ubuntu6`, where the software announces itself as `9.4`: the suffix is
  the packaging work of the distribution.
- **Repository** is not an **app store**: it is a server of signed packages,
  declared in the configuration of the system, with no account and no payment.
  `apt-cache policy coreutils` gives its real address,
  `http://fr.archive.ubuntu.com/ubuntu noble/main`, and the final component
  (`main` here) says what level of commitment the distribution takes on that
  package.
- **Free** is not **free of charge**: `ls --version` prints `License GPLv3+` and
  `This is free software: you are free to change and redistribute it`, a freedom
  that says nothing about the price. The counter-example is in the guide, RHEL is
  built on free software and is sold by subscription, while Rocky Linux and
  AlmaLinux are free rebuilds of it.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `uname -r` does not match the most recent file in `/boot` | a kernel is installed but has not been booted yet | `cat /proc/cmdline`, then reboot |
| you are asked "which version of Linux?" and you hesitate | the question is ambiguous, it aims at the kernel or at the distribution | `uname -r` for the kernel, `/etc/os-release` for the distribution |
| a command from a tutorial does not exist on your machine | the tutorial aims at the other family of distributions | read `ID_LIKE` in `/etc/os-release` |
| `hostnamectl: command not found` | the command comes from the `systemd` package | fall back on `uname -a` and `cat /etc/os-release` |
| impossible to read the kernel in `/boot` | `-rw-------` permissions, reserved for the administrator | `ls -l` is enough, there is nothing to read inside |

No command in this course created or changed anything: there is nothing to clean
up.
