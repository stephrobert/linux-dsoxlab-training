# Context — RHCSA EX200 under exam conditions

You are handed **two freshly provisioned RHEL-family machines** and **180
minutes**. This capstone reproduces the real EX200: performance-based tasks whose
result must **survive a reboot**, graded on the state of the system rather than
the commands you typed.

- **`alma-rhcsa-1.lab`** (server) carries 15 tasks: partitioning and LVM, XFS,
  swap, a shell script, users/groups and ACLs, a static network, systemd units and
  timers, SELinux (context, boolean, port), software installation.
- **`alma-rhcsa-2.lab`** (client) carries 5 dependent tasks: mounting the NFS
  share, synchronizing against the time server, key-only SSH to the server, and
  recovering an unknown root password.

Two skills are deliberately **not graded**: exporting an NFS share and running a
time server. Neither appears in the EX200 objectives, which speak of mounting a
share and configuring a time **client**. Both services are therefore provided by
the lab.

Passing score is **70/100**. No hints. `man`, `--help` and `/usr/share/doc/` are
your only companions — exactly as on exam day.
