# Lab: harden a kernel setting and make it stick

## Reminder

[**Hardening eBPF on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/durcir-ebpf/)

The Linux kernel exposes hundreds of settings, readable and changeable with the
`sysctl` command. Some of them decide who is allowed to do what, for instance
loading an eBPF program into the kernel. This lab teaches the three gestures of
a reliable hardening: **read** a setting, **change** it, and above all make it
**durable**, meaning make sure it will still be there after the next boot. The
classic trap is not setting the value, it is believing that it holds.

## The course

The examples below use a setting unrelated to eBPF (`vm.swappiness`, which
decides how hard the kernel pushes memory out to swap): the challenge will pose
a different problem, and it is up to you to transfer what you have seen. Every
output reproduced here was obtained on AlmaLinux 10.2 (kernel 6.12) and on
Ubuntu 24.04 (kernel 6.8), on a fresh machine.

### Read and change a kernel setting: `sysctl`

A kernel setting is a file of the `/proc/sys` pseudo-filesystem, and `sysctl`
reads it as `key = value`. The dots of the key replace the slashes of the path.

```bash
sysctl vm.swappiness
```

```text
vm.swappiness = 30
```

On Ubuntu 24.04 the original value is `60`: **the default differs from one
distribution to another**, one more reason to read it before setting it. To
change it right away, add the `-w` option, with root rights:

```bash
sudo sysctl -w vm.swappiness=10
```

```text
vm.swappiness = 10
```

The kernel applies the new value immediately. Some settings cannot even be read
by an ordinary account: `sysctl` then answers `permission denied on key
'<key>'`, and `sudo` settles it. The `net.core.bpf_jit_harden` setting, which
concerns the just-in-time compiler of eBPF programs, is one of them:

```bash
sysctl net.core.bpf_jit_harden
sudo sysctl net.core.bpf_jit_harden
```

```text
sysctl: permission denied on key 'net.core.bpf_jit_harden'
net.core.bpf_jit_harden = 1
```

The second line comes from AlmaLinux; Ubuntu 24.04 returns `0` with the same
`sudo`. Here again, **the two distributions do not start from the same state**.

### The two eBPF settings, and what their values mean

eBPF lets you load small programs into the kernel, through a system call named
`bpf()`. Two settings frame that call. The first,
`kernel.unprivileged_bpf_disabled`, decides whether an **unprivileged** user (an
ordinary account, with neither `root` nor any particular capability) may call
it. The kernel documentation gives three values:

| Value | Effect on an unprivileged caller | Reversible? |
| --- | --- | --- |
| `0` | `bpf()` is allowed | yes |
| `1` | `bpf()` is refused | **no**, until the next reboot |
| `2` | `bpf()` is refused | yes |

The second, `net.core.bpf_jit_harden`, acts on the **JIT** (just-in-time), the
compiler that translates an eBPF program into processor instructions on the fly.
A "JIT spraying" attack consists in influencing the generated code; the
hardening "blinds" the constants to defeat it:

| Value | Effect |
| --- | --- |
| `0` | hardening disabled |
| `1` | enabled for programs loaded by unprivileged callers |
| `2` | enabled for **every** program, including those loaded by `root` |

Remember the "reversible" column of the first table: it matters further down.

### Changing at runtime does not last

A value set with `sysctl -w` lives in the kernel's memory, and nowhere else. At
the next boot the kernel starts from its defaults, then the `systemd-sysctl`
service applies the configuration files. Whatever is written in no file
therefore disappears. A reload of those files on demand is done with:

```bash
sudo sysctl --system > /dev/null
sysctl vm.swappiness
```

```text
vm.swappiness = 10
```

The value is still `10`, for a misleading reason: `sysctl --system` applies
**what the files say** and leaves alone the keys they do not mention. It does
not bring the original value back, it does not put anything in order. Only a
real reboot proves that a setting exists in memory alone. This reload is also
the way to get, without rebooting, what the boot would do: everything a file
sets is applied again.

### Make it durable: a file in `/etc/sysctl.d/`

The durable configuration lives in `.conf` files, read from two directories:
`/usr/lib/sysctl.d/` for those the packages provide, and `/etc/sysctl.d/` for
the administrator's, where you write. On AlmaLinux 10 the latter only holds one
file at the start, `99-sysctl.conf`; on Ubuntu 24.04 it holds about ten
(`10-kernel-hardening.conf`, `10-ptrace.conf`...). Each line of a file is a
`key = value`.

Let us create two demo files, with two different values for the same key:

```bash
echo 'vm.swappiness = 20' | sudo tee /etc/sysctl.d/50-demo-reglage.conf
echo 'vm.swappiness = 40' | sudo tee /etc/sysctl.d/90-demo-reglage.conf
sudo sysctl --system | grep -E "demo|swappiness"
sysctl vm.swappiness
```

```text
* Applying /etc/sysctl.d/50-demo-reglage.conf ...
* Applying /etc/sysctl.d/90-demo-reglage.conf ...
vm.swappiness = 20
vm.swappiness = 40
vm.swappiness = 40
```

This is the most useful reading of the course. `sysctl --system` announces each
file it reads (`Applying ...`), **in alphabetical order of the names**, all
directories mixed, and applies each value as it goes. When two files set the same
key, **the last one read wins**: here `90-demo-reglage.conf` overrides
`50-demo-reglage.conf`, and the kernel keeps `40`. This is why the files carry a
numeric prefix, and why a file named `99-...` has the last word over almost all
the others.

To know **who sets a key**, without guessing, search for its name in every place
`sysctl` reads:

```bash
sudo grep -rn swappiness /etc/sysctl.d /usr/lib/sysctl.d /etc/sysctl.conf
```

```text
/etc/sysctl.d/50-demo-reglage.conf:1:vm.swappiness = 20
/etc/sysctl.d/90-demo-reglage.conf:1:vm.swappiness = 40
```

The result names each file, with its line number. If one of them has no reason
to exist, delete or fix it, then reload: after removing `90-demo-reglage.conf`,
`sudo sysctl --system` gives `20` again. To finish, clean up the demo:

```bash
sudo rm /etc/sysctl.d/50-demo-reglage.conf /etc/sysctl.d/90-demo-reglage.conf
sudo sysctl -w vm.swappiness=30
```

(`30` is AlmaLinux's original value; use `60` on Ubuntu.)

### Check the behaviour, not just the value

Reading a value proves what the administrator wrote. To prove what the kernel
does, you ask it. The Python program below calls `bpf()` to create a small eBPF
map (the `BPF_MAP_CREATE` operation), pretending to be the `nobody` user, an
unprivileged account present on every distribution. The system call number
changes with the architecture: 321 on x86_64, 280 on aarch64.

```bash
sudo -u nobody python3 - <<'PY'
import ctypes, errno, os, platform, struct

numeros = {"x86_64": 321, "aarch64": 280}
libc = ctypes.CDLL(None, use_errno=True)
attr = ctypes.create_string_buffer(128)
struct.pack_into("IIIII", attr, 0, 2, 4, 4, 1, 0)
retour = libc.syscall(numeros[platform.machine()], 0, attr, 128)
if retour >= 0:
    print("accepted: the kernel created the map (uid %d)" % os.getuid())
else:
    code = ctypes.get_errno()
    print("refused: %s (%s), uid %d" % (errno.errorcode[code], os.strerror(code), os.getuid()))
PY
```

```text
refused: EPERM (Operation not permitted), uid 65534
```

`EPERM` is the "operation not permitted" error code: the kernel refused the call,
which proves the door is closed for that user. Depending on the starting state of
the machine you may see the "accepted" line instead: the door is then open. The
same program run with `sudo python3 -` (so as `root`) is always accepted. This
result is decided at the instant of the call, inside the running kernel: a
correct configuration file changes nothing as long as its value has not been
applied.

### Why the value `1` is a trap on a lab machine

The value `1` of `kernel.unprivileged_bpf_disabled` closes the door **with no way
back**. Here is what a kernel answers, on a throwaway VM, when you try to reopen
it after setting it (do not do this on the lab machine):

```text
sudo sysctl -w kernel.unprivileged_bpf_disabled=1
kernel.unprivileged_bpf_disabled = 1
sudo sysctl -w kernel.unprivileged_bpf_disabled=0
sysctl: setting key "kernel.unprivileged_bpf_disabled": Operation not permitted
sudo sysctl -w kernel.unprivileged_bpf_disabled=2
sysctl: setting key "kernel.unprivileged_bpf_disabled": Operation not permitted
```

Even towards `2` the kernel refuses: the value `1` is locked until the machine
reboots. It is a deliberate protection on a production server, where you do not
want an attacker to reopen it. It is an obstacle on a lab that must be able to
reset itself between two attempts, hence the value the challenge expects.
