# Challenge: ebpf-durcir-sysctl

## Mission

The audit is clear: eBPF is too open on this server. Close it to unprivileged
users, harden the JIT compiler for every program, and make it stick: the
settings must survive a reload of the sysctl configuration, hence the next boot.

## Goal (expected state)

1. `kernel.unprivileged_bpf_disabled` is **2** in the kernel.
2. `net.core.bpf_jit_harden` is **2** in the kernel.
3. A `bpf()` system call (creating an eBPF map) made by the unprivileged user
   `nobody` is **refused** by the kernel, with the `EPERM` error.
4. If both settings are put back to `0` at runtime and the configuration is
   then reloaded with `sysctl --system`, `net.core.bpf_jit_harden` comes back to
   `2`.
5. Under the same conditions, `kernel.unprivileged_bpf_disabled` comes back to
   `2` as well.

## Constraints

- The expected value for `kernel.unprivileged_bpf_disabled` is **2**, not 1.
  Both forbid eBPF to unprivileged users, but `1` cannot be changed again before
  the machine reboots: the lab could no longer reset itself.
- Reading `net.core.bpf_jit_harden` needs root rights (`sudo`).
- Do not reboot the VM: the validation replays the loading of the configuration
  by itself.
- You do not have to change the files in `/usr/lib/sysctl.d/`, which belong to
  the distribution.
- Validation reads the state of the machine, not your command history.

## Validation

```bash
dsoxlab check ebpf-durcir-sysctl                  # AlmaLinux 10 (default target)
dsoxlab check ebpf-durcir-sysctl --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-durcir-sysctl                  # a hint, at the cost of points
```
