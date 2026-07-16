# LFCS Capstone — Mock Exam

**Format**: 17 tasks, 100 points, 1 VM, 120 minutes.
**Passing score**: 70/100. **No hints** will be revealed.

## Your machine

| Host | Role |
|---|---|
| `ubuntu-lfcs-1.lab` | Ubuntu 24.04 — all 17 tasks |

Connect via `dsoxlab ssh ubuntu-lfcs-1.lab`. You are `student` with sudo NOPASSWD.

Changes must be **persistent after reboot**. A configuration that works right now
but was applied only with a live command (no persistence) does not count.

**Never touch `enp5s0`** — it is the management interface. Network tasks use the
dedicated `lab0` interface. The disk `/dev/vdb` (5 GiB) is attached and blank.

---

## Section A — Essential Commands (20 pts)

### Task 1 — Find and archive (5 pts)

Under `/srv/audit/` there are files scattered in subdirectories. Create the
archive **`/root/logs.tar.gz`** (gzip-compressed tar) containing **every file
whose name ends in `.log`** found anywhere under `/srv/audit/`, and nothing else.

### Task 2 — Extract a report (5 pts)

The file `/srv/audit/access.log` mixes several levels. Write to
**`/root/errors.txt`** only the lines containing `ERROR`, in their original
order. No other line.

### Task 3 — Links (4 pts)

For the file `/srv/audit/access.log`, create:

- a **hard link** at `/root/access.hard`
- a **symbolic link** at `/root/access.soft`

### Task 4 — Collaborative directory (6 pts)

The group `auditors` must share `/srv/shared`:

- owned by group `auditors`, mode `2770`
- any new file created inside inherits the group `auditors`

---

## Section B — Operations Deployment (25 pts)

### Task 5 — Install and freeze a package (5 pts)

Install **`tree`** and put it on **hold** so an upgrade can never move it.

### Task 6 — A service unit (7 pts)

Create the systemd service **`labwatch.service`** that runs
`/usr/local/bin/labwatch.sh` (already provided, executable). It must be
**enabled** and **running**, and come back after a reboot.

### Task 7 — A timer (7 pts)

Create the systemd timer **`labreport.timer`** that triggers
`labreport.service` **every day at 03:00**. The unit `labreport.service` must run
`/usr/local/bin/labreport.sh` (already provided). The timer must be **enabled**
and **active**.

### Task 8 — A cron job (6 pts)

For the user **`devops`**, schedule via **cron** the command
`/usr/local/bin/labreport.sh` **every 10 minutes**.

---

## Section C — Users and Groups (10 pts)

### Task 9 — Create an account (5 pts)

Create the user **`auditor1`**:

- UID **`3001`**
- login shell **`/bin/bash`**
- member of the supplementary group **`auditors`**

### Task 10 — Delegate sudo (5 pts)

Members of the group **`auditors`** must be able to run **only**
`/usr/bin/systemctl status *` as root, **without a password**. Declare it in a
file under `/etc/sudoers.d/`.

---

## Section D — Networking (25 pts)

### Task 11 — Static IP (8 pts)

On the dedicated interface **`lab0`** (dummy), declare with **netplan** the
static address **`198.51.100.10/24`**. It must be live and persistent.

### Task 12 — Static route (5 pts)

Still with netplan, add a static route to **`203.0.113.0/24` via
`198.51.100.1`**.

### Task 13 — Firewall (7 pts)

With **ufw**: allow **`8080/tcp`**, and enable the firewall. SSH
(`OpenSSH`) must remain allowed — if you lock yourself out, you lose the
remaining tasks.

### Task 14 — Name resolution (5 pts)

Make the name **`lab-target.lab`** resolve locally to **`198.51.100.10`**,
without any DNS server.

---

## Section E — Storage (20 pts)

### Task 15 — LVM and persistent mount (8 pts)

On `/dev/vdb`:

- create a partition `/dev/vdb1` of **2 GiB**
- make it an LVM physical volume, in the volume group **`vgdata`**
- create the logical volume **`lvapp`** of **1 GiB**, formatted **XFS**
- mount it on **`/data`** at boot, **by UUID** (not by device path)

### Task 16 — Quota (7 pts)

On a second partition `/dev/vdb2` of **1 GiB**, formatted **XFS** and mounted on
**`/srv/quota`** persistently with **user quotas** enabled: enforce on the user
`devops` a block quota of **20M soft / 30M hard**.

### Task 17 — Swap (5 pts)

Add **256 MiB** of swap as a **file** `/swapfile`, active and persistent at
boot. Total swap must grow by ~256 MiB.

---

## Validate

```bash
dsoxlab check lfcs-mock-exam
```
