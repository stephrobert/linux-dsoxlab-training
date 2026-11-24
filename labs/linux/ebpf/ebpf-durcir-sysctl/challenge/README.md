# The audit that finds eBPF wide open

## The situation

Last week a contractor profiled an application on this server. Their tool ran
eBPF probes without being root, and to make that work someone relaxed the kernel
settings by hand, then forgot to put them back. The ticket is closed, the
contractor is gone, and this quarter's security audit has just landed: any
ordinary account on the machine can load code into the kernel, and the compiler
that turns those programs into processor instructions is not hardened.

This is not a detail. Several kernel flaws were only exploitable by an
unprivileged caller, and closing that door is one of the cheapest steps of Linux
hardening. But a kernel setting fixed at runtime is only fixed until the next
reboot, and whoever opened the door may also have left something that opens it
again.

What gets checked is the state of the machine: what the kernel applies right now,
what it really refuses to an unprivileged user, and what it will apply after a
reload of the configuration. Not the commands you typed.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/going-deeper/ebpf/hardening/harden-ebpf/

## What is asked

### Mission

The audit is clear: eBPF is too open on this server. Close it to unprivileged
users, harden the JIT compiler for every program, and make it stick: the
settings must survive a reload of the sysctl configuration, hence the next boot.

### Goal (expected state)

1. `kernel.unprivileged_bpf_disabled` is **2** in the kernel.
2. `net.core.bpf_jit_harden` is **2** in the kernel.
3. A `bpf()` system call (creating an eBPF map) made by the unprivileged user
   `nobody` is **refused** by the kernel, with the `EPERM` error.
4. If both settings are put back to `0` at runtime and the configuration is
   then reloaded with `sysctl --system`, `net.core.bpf_jit_harden` comes back to
   `2`.
5. Under the same conditions, `kernel.unprivileged_bpf_disabled` comes back to
   `2` as well.

### Constraints

- The expected value for `kernel.unprivileged_bpf_disabled` is **2**, not 1.
  Both forbid eBPF to unprivileged users, but `1` cannot be changed again before
  the machine reboots: the lab could no longer reset itself.
- Reading `net.core.bpf_jit_harden` needs root rights (`sudo`).
- Do not reboot the VM: the validation replays the loading of the configuration
  by itself.
- You do not have to change the files in `/usr/lib/sysctl.d/`, which belong to
  the distribution.
- Validation reads the state of the machine, not your command history.

### Validation

```bash
dsoxlab check ebpf-durcir-sysctl                  # AlmaLinux 10 (default target)
dsoxlab check ebpf-durcir-sysctl --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-durcir-sysctl                  # a hint, at the cost of points
```
