# Capstone — RHCSA EX200 mock exam

**20 tasks, 2 machines, 180 minutes. Passing score: 70 points out of 100.
No hints.** This mock exam is **RHCSA only**: it runs on two AlmaLinux 10, a
server and a client, there is no Ubuntu target.

[**RHCSA on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/certifications/rhcsa/)

## What a mock exam is

A mock exam is neither a lab nor a drill. A drill revises one topic in twenty
minutes; this one reproduces a full three-hour session, with its fatigue, its
time trade-offs and its final score.

- **no hint is available**, not even in exchange for points;
- **the tasks do not all carry the same weight**, from 4 to 7 points depending on
  the work they require. Choosing the order in which to deal with them is part of
  the exam;
- **some tasks depend on others**, since two machines are involved: what you
  expose from the server, the client must be able to consume. A server task done
  badly brings down another one on the client side;
- **everything must survive a reboot**. A firewall rule lost at reboot, a mount
  absent from the filesystem table, a service started but not enabled: those
  three cases score zero, whatever command you typed.

## What you need to know before attempting it

Do not take this mock exam first. It is meant to be played **after** the labs and
the drills, when you are trying to measure a level, not to learn. Here is, domain
by domain, where each topic is taught.

| What the exam requires | The lab where it is taught |
|---|---|
| Partitioning a disk in GPT | `l2-partition-gpt` |
| LVM stack, and extending a volume online | `l2-lvm-extend-persist` |
| Creating and labelling an XFS filesystem | `l2-filesystem-create-xfs` |
| Persistent mount by UUID | `l2-fstab-persist-uuid` |
| Swap as a file, active and persistent | `l2-swap-management` |
| NFS share, on the export side and the mount side | `l2-nfs-mount-persist` |
| Creating an account with an imposed UID and shell | `l2-user-lifecycle` |
| Password ageing | `l2-password-policy` |
| Collaborative directory and set-GID bit | `l2-collaborative-setgid` |
| POSIX ACL without touching the classic permissions | `l2-acl-posix` |
| Persistent static address and host name | `l4-network-static-persist` |
| Diagnosing a network that does not answer | `l4-network-troubleshoot` |
| `firewalld` firewall, permanent rules and zones | `l4-firewall-persist` |
| Writing a service unit and enabling it at boot | `l3-service-create-unit` |
| Diagnosing a service that does not start | `l3-service-diagnose` |
| Persistent `OnCalendar` timer | `l3-scheduling-timers` |
| Time synchronisation with `chrony` | `l4-ntp-sync` |
| Fixing the SELinux context of a file | `l4-selinux-context-fix` |
| SELinux booleans and port labels | `l4-selinux-boolean-port` |
| Reading an SELinux denial in the log | `l4-selinux-diagnose-avc` |
| Installing and querying packages with DNF | `l2-package-management` |
| SSH key authentication and hardening | `l4-ssh-key-auth-harden` |

Two topics of the exam have no course here. **Root password recovery** by
interrupting the boot loader is the RHCSA gesture par excellence: the
`l3-grub-kernel-args` lab covers kernel parameters at boot, but its README points
to the online guide instead of teaching. **Flatpak** has no lab at all in this
repository: revise it in the guide before starting, it is the only exam topic
that nothing here prepares you for.

Before going in, the drills cover the same gestures in short form:
`drill-storage`, `drill-systemd`, `drill-users-groups`, `drill-network`,
`drill-firewall`, `drill-packages` and `drill-selinux`. Seven drills passed are
worth more than a mock exam failed twice.

## Getting into exam conditions

Three hours for twenty tasks spread over two machines leaves nine minutes per
task on average. The average means nothing here: it is your plan of attack that
decides the score.

- **Read the twenty tasks before the first command**, and spot three things: which
  tasks are played on the server, which on the client, and which depend on
  another. Doing the mount before the export, or the key authentication before
  creating the account, means doing the work twice;
- **keep for the end whatever requires a reboot**. Root password recovery needs
  two of them and is done at the console, not over SSH: placing it in the middle
  of the exam costs minutes you will not have;
- **do not cut off your own access by freezing the network**. This is the most
  expensive trap of this mock exam: the machine gets its network configuration
  from the address server, and you have to make it permanent. Keep the address the
  machine already carries. Changing it disconnects you, and disconnects the marker
  as well;
- **with `firewalld` and SELinux, write into the policy, not only into memory**. A
  firewall rule without the permanent option, a boolean flipped without the
  persistence option, a context set without being recorded in the naming policy:
  all three disappear at the first reload or the first relabel. That is exactly
  what the marking will trigger;
- **prove each task with the tool that reads the system**, not with the file you
  have just written: `systemctl show` and `systemctl is-enabled` for units,
  `findmnt` and `blkid` for mounts, `getfacl` for an ACL, `getent` for accounts,
  `firewall-cmd --list-all` after a reload, `semanage` and `getsebool` for
  SELinux;
- **reboot both machines before validating**, and keep half an hour for that in
  your budget. It is the only proof of persistence that counts.

On the real exam as here, `man`, `--help` and `/usr/share/doc/` are your only
resources. Consulting them is not an admission of weakness: it is the skill the
exam measures.

## Afterwards

The marking does not only give your score: it says **which task** failed and
**what the system contained** at the moment of the check. Read it as a diagnosis.
Failures grouped on the same domain point at a topic to go over again, and you
know which one. Scattered failures point at something else: time management that
was too optimistic, or changes that were never made persistent.

Then replay the labs of the tasks you missed, then the drills of the domain
concerned, before coming back to this mock exam. Redoing it straight away only
measures your memory of the wording, whereas on the day the wording will be
different and the gestures will be the same.
