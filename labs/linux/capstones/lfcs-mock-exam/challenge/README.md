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

**Never touch the management interface** — it is the management interface. Network tasks use the
dedicated `lab0` interface. The disk `/dev/vdb` (5 GiB) is attached and blank.

---

## Section A — Essential Commands (20 pts)

### Task 1 — Put `/srv/deploiement` under Git (5 pts)

The directory `/srv/deploiement` holds two working files and a `.cache/`
subdirectory that must never be versioned.

- Initialise a Git repository **in `/srv/deploiement`**
- `config.yml` and `notes.txt` are **tracked and committed**
- `.cache/` is **ignored**: `git status` must no longer mention it
- Create a branch named **`recette`**; you do not have to switch to it

### Task 2 — Repair `collecteur.service` (6 pts)

The `collecteur.service` unit is installed but refuses to start. The script it
is meant to run, `/usr/local/bin/collecteur.sh`, is correct: **do not rewrite
it**, the two faults are elsewhere.

- `systemctl start collecteur` must succeed
- The service must be **active** and **enabled at boot**
- `/var/log/collecteur.log` must start filling up

### Task 3 — Find the missing disk space (4 pts)

`df` reports several hundred megabytes used under `/var` that `du` cannot
account for. A process is holding a file that was **deleted but is still open**.

- Write the **systemd unit name** responsible into **`/root/diskspace.txt`**
  (one line, the name alone is enough)
- **Release the space**: that unit must no longer run, and must not come back at
  boot

### Task 4 — Self-signed certificate (5 pts)

Produce a certificate for the collector, under `/etc/ssl/lab/`:

- Private key **`/etc/ssl/lab/collecteur.key`**, readable **by root only**
- Certificate **`/etc/ssl/lab/collecteur.crt`**, self-signed with that key
- **CN = `collecteur.lab`**
- Valid for **at least 365 days** from today

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

### Task 10 — Open `/srv/rapports` with ACLs (5 pts)

`/srv/rapports` is owned by `root:root` with mode `0750`: the user `devops` has
no access at all. Let them in **without changing the owner or the group**, and
**without opening anything to the rest of the world**. A `chmod` that grants
access to everyone does not count.

- `devops` gets **`rwx`** on `/srv/rapports`
- `devops` gets **`rw`** on the existing `bilan.csv` file
- Every **new** file created in that directory must grant them **`rw`**
  automatically, with no further action

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

### Task 16 — On-demand automount (7 pts)

Create a second partition **`/dev/vdb2`** of **1 GiB** formatted **XFS**, then
have it mounted **on demand** by the automounter.

- The mount point is **`/mnt/auto/donnees`**
- It must **not** appear in `/etc/fstab`: `autofs` is what mounts it
- A plain `ls /mnt/auto/donnees` triggers the mount
- The `autofs` service is **active and enabled at boot**

### Task 17 — Swap (5 pts)

Add **256 MiB** of swap as a **file** `/swapfile`, active and persistent at
boot. Total swap must grow by ~256 MiB.

---

## Validate

```bash
dsoxlab check lfcs-mock-exam
```
