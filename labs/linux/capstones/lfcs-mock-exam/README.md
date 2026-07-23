# Capstone — LFCS mock exam

**17 tasks, 100 points, 120 minutes, a single machine. Pass mark: 70/100. No
hints.** This mock exam is **LFCS only**: it is played on Ubuntu 24.04, there is
no AlmaLinux target.

[**LFCS on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/certifications/lfcs/)

## What a mock exam is

A mock exam is neither a lab nor a drill. A drill revises one subject in twenty
minutes; this one reproduces a full session, with its fatigue, its time
trade-offs and its final mark.

- **no hint is available**, not even in exchange for points;
- **the 5 official domains appear at their real weights**: Essential Commands
  20%, Operations Deployment 25%, Users and Groups 10%, Networking 25%, Storage
  20%. Two domains are therefore worth half the mark on their own;
- **everything must survive a reboot**. A firewall rule lost at reboot, a mount
  missing from the filesystem table, a service started but not enabled: those
  three cases are worth zero, whatever command you typed.

## What you need to know before attempting it

Do not take this mock exam first. It is meant to be played **after** the labs and
the drills, when you are looking to measure a level, not to learn. Here is,
domain by domain, where each subject is taught.

| Domain and what it asks for | The lab where it is taught |
|---|---|
| Essential Commands: finding files on a criterion | `l1-find-files` |
| Essential Commands: compressed archives | `l1-tar-archives` |
| Essential Commands: filtering lines | `l1-grep-regex` |
| Essential Commands: hard and symbolic links | `l1-links-hard-sym` |
| Essential Commands: permissions and octal notation | `l1-permissions-ugo` |
| Essential Commands: shared directory and set-GID bit | `l2-collaborative-setgid` |
| Operations: writing and enabling a service unit | `l3-service-create-unit` |
| Operations: diagnosing a service that does not start | `l3-service-diagnose` |
| Operations: `OnCalendar` timer | `l3-scheduling-timers` |
| Operations: a user's cron table | `l3-scheduling-cron` |
| Users and Groups: creating an account with imposed attributes | `l2-user-lifecycle` |
| Users and Groups: delegating `sudo` as narrowly as possible | `l2-sudo-delegation` |
| Networking: persistent static address and route | `l4-network-static-persist` |
| Networking: local name resolution, read with `getent hosts` | `l4-network-troubleshoot` |
| Networking: opening a port without cutting off your session | `l4-firewall-persist` |
| Storage: partitioning a disk | `l2-partition-gpt` |
| Storage: LVM stack and extension | `l2-lvm-extend-persist` |
| Storage: XFS filesystem | `l2-filesystem-create-xfs` |
| Storage: persistent mount by UUID | `l2-fstab-persist-uuid` |
| Storage: swap | `l2-swap-management` |

Four subjects of the exam have no course on site, because the labs that carry
them point to the online guide rather than teaching: `lfcs-package-apt` for
Debian package management and version pinning, `lfcs-netplan-static` for network
configuration, `lfcs-firewall-ufw` for the firewall and `lfcs-storage-quotas`
for quotas. These four labs are playable and worth doing beforehand: it is the
course that is missing, not the exercise. The labs `l4-network-static-persist`
and `l4-firewall-persist` teach the corresponding reasoning on the RHEL side,
with other tools.

## Getting into exam conditions

One hundred and twenty minutes for seventeen tasks makes seven minutes per task.
That budget only holds if you decide the order instead of suffering it.

- **Read the whole paper before the first command**, and note for each task its
  domain and its weight. Networking and Storage tasks weigh heavily and take
  time: keeping them for the end is the best way not to finish them. Essential
  Commands pays little per task but is handled quickly, it is margin to pick up
  along the way, not a place to linger;
- **set yourself a time per task and stick to it**. Past twice the planned
  budget, leave the task and move on: you will come back to it with a clear
  head, and seven minutes lost on a five-point task cost two more elsewhere;
- **do not cut yourself off from the machine**. Two steps of this exam can lock
  you out: enabling the firewall, and touching the network. Open a second
  session before either one, check that SSH access is still allowed before
  enabling filtering, and never configure the interface that carries your
  session: the network tasks target a dedicated interface, identify it and do
  not confuse it with the one `ip route get 1.1.1.1` gives you;
- **prove each task with the tool that reads the system**, not with the file you
  have just written: `systemctl is-enabled` and `systemctl is-active` for units,
  `findmnt` and `blkid` for mounts, `swapon --show` for swap, `getent` for
  accounts and names, `sudo -l -U` for a delegation;
- **reboot the machine before submitting**. It is the only proof of persistence
  that counts, and it is precisely what the exam measures. Plan those minutes
  into your budget from the start.

## Afterwards

The correction does not only tell you your score: it tells you **which task**
failed and **what the system contained** at the time of the check. Map those
failures onto the five domains: three tasks failed in the same domain do not
mean the same thing as three tasks failed here and there. In the first case, you
are missing a subject and you know which one; in the second, it is time
management or persistence that needs work.

Then replay the labs of the failed tasks, then the drills of the domain
concerned, before coming back to this mock exam. Redoing it immediately only
measures your memory of the paper.
