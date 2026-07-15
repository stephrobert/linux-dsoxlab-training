# Context — RHCSA EX200 under exam conditions

You are handed **two freshly provisioned RHEL-family machines** and **180
minutes**. This capstone reproduces the real EX200: performance-based tasks whose
result must **survive a reboot**, graded on the state of the system rather than
the commands you typed.

- **`alma-rhcsa-1.lab`** (server) carries 16 tasks: partitioning and LVM, XFS,
  swap, an NFS export, users/groups and ACLs, a static network, systemd units and
  timers, chrony, SELinux (context, boolean, port), software installation.
- **`alma-rhcsa-2.lab`** (client) carries 4 dependent tasks: mounting the NFS
  share, key-only SSH to the server, and recovering an unknown root password via
  the `rd.break` procedure.

Your mission:

1. Read the full task list with `dsoxlab challenge rhcsa-mock-exam`.
2. Work through the 20 tasks, always making changes **persistent**.
3. Reboot both VMs, then run `dsoxlab check rhcsa-mock-exam`.

Passing score is **70/100**. No hints. `man`, `--help` and `/usr/share/doc/` are
your only companions — exactly as on exam day.
