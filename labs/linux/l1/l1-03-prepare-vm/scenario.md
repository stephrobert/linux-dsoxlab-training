# Lab l1-03 — Identify your Linux machine

| | |
|---|---|
| **Level** | L1 — Fundamentals (B0) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 15 min |
| **Reference** | [Installer une VM Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/) |

---

## What you will learn

- Retrieve the hostname of a Linux machine
- Identify the distribution name and version with a single command
- Read the running kernel version
- Find the local IP address of a machine
- Write a machine identity card that you can reuse on any server

---

## Command reference

| Command | What it shows |
|---------|--------------|
| `hostname` | Short hostname |
| `hostname -f` | Fully qualified domain name (if set) |
| `cat /etc/hostname` | Hostname stored in the config file |
| `cat /etc/os-release` | Distribution name, version, ID |
| `grep PRETTY_NAME /etc/os-release` | One-line distro summary |
| `hostnamectl` | Hostname + OS + kernel (systemd systems) |
| `uname -r` | Running kernel version |
| `ip addr show` | All network interfaces with IP addresses |
| `hostname -I` | All local IP addresses, space-separated |
| `ip route` | Routing table — shows the default gateway |

---

## Exercise 1 — Hostname

The hostname identifies the machine on the network. It is stored in `/etc/hostname`
and displayed by the `hostname` command.

```bash
hostname
cat /etc/hostname
```

Note the difference: `hostname` reads the running system state; `/etc/hostname` is
the persistent file that sets it at boot.

---

## Exercise 2 — Distribution

```bash
cat /etc/os-release
```

Look for:
- `NAME` — short distribution name (e.g. `Ubuntu`, `Debian GNU/Linux`, `AlmaLinux`)
- `VERSION` — the release version string
- `PRETTY_NAME` — a human-readable single line combining both

Shorter:

```bash
grep PRETTY_NAME /etc/os-release
```

---

## Exercise 3 — Kernel version

```bash
uname -r
```

The version follows the pattern `MAJOR.MINOR.PATCH-extra`.
For example: `6.8.0-55-generic`

```bash
uname -a     # full line: kernel + hostname + date + architecture
```

---

## Exercise 4 — IP address

```bash
hostname -I
```

This prints all configured IP addresses on one line.
If you have multiple interfaces (loopback, ethernet, Wi-Fi), all are shown.

For details with interface names:

```bash
ip addr show
```

Look for lines starting with `inet ` (IPv4) — the address is the value before `/`.
Ignore `127.0.0.1` (loopback) — that is not a real network address.

---

## Write your machine identity card

Open the template and fill in the four fields with the real values from your system:

```bash
cat challenge/work/vm-info.txt   # read the template
nano challenge/work/vm-info.txt  # fill it in
```

```bash
dsoxlab check l1-03-prepare-vm
```
