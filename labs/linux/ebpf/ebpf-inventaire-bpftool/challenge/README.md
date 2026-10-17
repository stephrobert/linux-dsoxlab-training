# Challenge: ebpf-inventaire-bpftool

## Mission

A service with a harmless name loads an eBPF program into the kernel of this
machine, and nobody deployed it. Inventory the loaded programs with `bpftool`,
find the process and then the systemd service that carry the unknown one, stop
it for good, and record what you found.

## Goal (expected state)

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

## Constraints

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

## Validation

```bash
dsoxlab check ebpf-inventaire-bpftool                  # AlmaLinux 10 (default target)
dsoxlab check ebpf-inventaire-bpftool --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-inventaire-bpftool                  # a hint, at the cost of points
```
