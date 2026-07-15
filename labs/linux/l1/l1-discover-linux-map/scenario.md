# Lab l1-01 — Map Linux: kernel, distribution and key directories

| | |
|---|---|
| **Level** | L1 — Fundamentals (B0) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 20 min |
| **Reference** | [Notions fondamentales Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/) |

---

## What you will learn

By the end of this lab you will be able to:

- Distinguish Linux (kernel) from a Linux distribution
- Identify the kernel version running on your system
- Identify the distribution name and version
- State the purpose of `/etc`, `/var/log`, `/proc` and `/home`
- Use `uname`, `cat /etc/os-release` and directory listings to gather system information

No files are modified on the system. This lab is read-only exploration.

---

## Command reference

| Command | What it does |
|---------|-------------|
| `uname -r` | Print the running kernel version |
| `uname -a` | Print all kernel information |
| `cat /etc/os-release` | Show distribution name and version |
| `hostnamectl` | Show hostname and OS details (systemd systems) |
| `ls /etc \| head -20` | List first 20 entries in the config directory |
| `ls /var/log` | List log files |
| `ls /proc \| head -20` | List the first entries of the virtual process filesystem |
| `ls /home` | List user home directories |

---

## Exercise 1 — Identify the kernel

The **kernel** is the core of the operating system. It manages the hardware directly:
CPU scheduling, memory, disk I/O, network. It is not a userland application.

Run both commands and compare their output:

```bash
uname -r
```

```bash
uname -a
```

The first number in `uname -r` output (for example `6.1.0`) is the kernel version.
The full `uname -a` line also shows the architecture (`x86_64`, `aarch64`, etc.) and the build date.

---

## Exercise 2 — Identify your distribution

A **Linux distribution** bundles the kernel with a package manager, system tools and
a default configuration. Ubuntu, Debian and AlmaLinux are distributions built on top
of the same Linux kernel.

```bash
cat /etc/os-release
```

Look for the `NAME`, `VERSION` and `ID` fields. On RHEL-based systems you may also read:

```bash
cat /etc/redhat-release
```

---

## Exercise 3 — Explore /etc

`/etc` is where **configuration files** live. Almost every installed service stores
its configuration under `/etc`.

```bash
ls /etc | head -20
```

Pick 3 entries you recognise and think about what service or function each one configures.

A few examples you will likely see:

| File / directory | Purpose |
|-----------------|---------|
| `/etc/hostname` | Machine name |
| `/etc/hosts` | Static hostname → IP mappings |
| `/etc/passwd` | Local user accounts |
| `/etc/fstab` | Filesystem mount table |
| `/etc/ssh/` | SSH server and client configuration |

---

## Exercise 4 — Explore /var/log

`/var/log` stores **log files** — the written record of what programs are doing.

```bash
ls /var/log
```

On a Debian/Ubuntu system you will commonly see:

| File | Who writes to it |
|------|-----------------|
| `syslog` | General system messages |
| `auth.log` | Authentication events (login, sudo) |
| `dpkg.log` | Package installations and removals |
| `kern.log` | Kernel messages |

On RHEL/AlmaLinux the main file is `/var/log/messages`.

Read the last 10 lines of the main log to see it is live:

```bash
sudo tail -10 /var/log/syslog          # Debian/Ubuntu
sudo tail -10 /var/log/messages        # RHEL/AlmaLinux
```

---

## Exercise 5 — Peek at /proc

`/proc` is not a real directory on disk. It is a **virtual filesystem** created by the
kernel at boot. It exposes kernel data structures as readable files.

```bash
ls /proc | head -20
```

Each numbered entry (`1`, `42`, `1234`) is a running process ID. The directories named
with words (`cpuinfo`, `meminfo`, `uptime`) expose hardware and system state:

```bash
cat /proc/uptime          # seconds since boot
cat /proc/cpuinfo | head -20   # CPU details
```

---

## Fill in your knowledge map

Open the answer file prepared for you and replace every `VOTRE_RÉPONSE_ICI`
with your own words (1–3 sentences per question):

```bash
# From the lab directory:
cat challenge/work/notions.md        # read the template
nano challenge/work/notions.md       # fill it in
```

You do not need to memorise exact definitions.
Write what you understood from running the commands above.

```bash
dsoxlab check l1-discover-linux-map   # validate when done
```
