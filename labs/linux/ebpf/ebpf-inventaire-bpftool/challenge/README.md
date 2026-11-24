# The program nobody deployed

## The situation

During a security review, the team realises it does not know what this server's
kernel is running. eBPF probes are common here: systemd itself loads some to
filter the network and the devices of its services. But an eBPF program runs in
the kernel with extended rights, and whatever lands there without anybody having
decided it is exactly what an attacker settled on the machine would do to stay
discreet.

A colleague spotted a service with a bland name, something like "telemetry
collector", that nobody remembers deploying. The request is simple and precise:
say what is loaded, find what carries it, and if it has no business being there,
stop it for good, meaning the service must not come back at the next boot.
Without touching what the system loads by itself: an inventory that breaks the
machine is no better than the program it was looking for.

What gets checked is the state of the machine: what the kernel still holds,
whether the service can come back, and whether your answer names the service and
the type of the program correctly. Not the commands you typed.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/going-deeper/ebpf/hardening/attack-surface-bpf/

## What is asked

### Mission

A service with a harmless name loads an eBPF program into the kernel of this
machine, and nobody deployed it. Inventory the loaded programs with `bpftool`,
find the process and then the systemd service that carry the unknown one, stop
it for good, and record what you found.

### Goal (expected state)

1. The systemd service that carries the program is **stopped**: no process left,
   and systemd does not restart it.
2. It **does not come back at the next boot**: `systemctl is-enabled` must answer
   `disabled` or `masked` (or `not-found` if you removed the unit). Any other
   answer, `enabled` included, fails.
3. The kernel **no longer holds** the program loaded by that service: `bpftool`
   does not list it any more.
4. The file `/var/tmp/reponse-inventaire-bpf.txt` has a `service=` line giving
   the **name of the systemd unit** that carried the program. The name with or
   without the `.service` suffix is accepted.
5. The same file has a `type=` line giving the **type of the program** that was
   loaded, as `bpftool prog` shows it.
6. The programs the system loads by itself (systemd's, the kernel's) are **still
   loaded**: only the program of the unknown service must go.

Expected format of `/var/tmp/reponse-inventaire-bpf.txt`: two `key=value` lines,
no space around the equals sign.

### Constraints

- The service name changes at every `dsoxlab run`: an answer from a previous
  session is worthless.
- `bpftool` and `bpftrace` are already installed. Reading or listing the programs
  needs root rights (`sudo`).
- The **program type** is the one `bpftool prog show` gives as the second field
  of the first line of a program. It is not the type of a link (`bpftool link`),
  nor that of a file descriptor.
- Killing the process settles nothing: the service starts it again. Removing the
  unit file does not stop a process that is already running either.
- Only stop, mask or remove the unknown service: the system units and the
  programs they load must stay in place.
- Validation reads the state of the machine, not your command history.

### Validation

```bash
dsoxlab check ebpf-inventaire-bpftool                  # AlmaLinux 10 (default target)
dsoxlab check ebpf-inventaire-bpftool --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-inventaire-bpftool                  # a hint, at the cost of points
```
