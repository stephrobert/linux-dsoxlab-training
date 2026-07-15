# Lab l1-07 — Linux Filesystem Hierarchy (FHS)

| | |
|---|---|
| **Level** | L1 — Fundamentals (B1) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 20 min |
| **Reference** | [Système de fichiers Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/filesystem/) |

---

## What you will learn

- Name the purpose of each standard Linux top-level directory
- Locate configuration files, logs, binaries, and device files on any distribution
- Distinguish `/bin` vs `/sbin` vs `/usr/bin` vs `/usr/local/bin`
- Understand why `/tmp` is dangerous for long-term storage
- Classify files by their correct FHS location

---

## The FHS map

Every Linux distribution follows the Filesystem Hierarchy Standard (FHS).
The root `/` is the top. Everything else hangs below:

| Directory | Role |
|-----------|------|
| `/bin` | Essential user binaries (ls, cp, cat) |
| `/sbin` | System administration binaries (fdisk, reboot) |
| `/usr` | Secondary hierarchy — most installed software |
| `/usr/bin` | Non-essential user binaries |
| `/usr/local/bin` | Locally compiled/installed binaries |
| `/etc` | System-wide configuration files |
| `/var` | Variable data: logs, spools, caches |
| `/var/log` | Log files |
| `/tmp` | Temporary files — cleared on reboot |
| `/home` | User home directories |
| `/root` | Root user's home directory |
| `/dev` | Device files (disks, terminals, null) |
| `/proc` | Virtual filesystem — kernel and process info |
| `/sys` | Virtual filesystem — hardware and kernel state |
| `/lib` | Essential shared libraries |
| `/mnt` | Temporary mount points |
| `/media` | Removable media (USB, CD) |
| `/boot` | Kernel and bootloader files |
| `/opt` | Optional third-party software |
| `/srv` | Service data (web roots, FTP) |

---

## Exercise 1 — Explore the top level

```bash
ls /
ls /etc | head -20
ls /var/log | head -10
```

---

## Exercise 2 — Where does it live?

For each path, which directory contains it?

```bash
ls /etc/hostname          # system config
ls /var/log/syslog 2>/dev/null || ls /var/log/messages 2>/dev/null
ls /usr/bin/git 2>/dev/null || which git
ls /dev/null              # always present
ls /proc/version          # kernel info
```

---

## Exercise 3 — Classify files

Look at the `fhs.txt` template. For each listed path, write the role of its
parent directory (one or two words, e.g. "configuration", "logs", "user binaries").

Then for each of the five fictitious files, write where it **should** live
according to FHS conventions.

```bash
cat challenge/work/fhs.txt    # read the template
nano challenge/work/fhs.txt   # fill it in
dsoxlab check l1-07-linux-filesystem
```
