# RHCSA Capstone — EX200 Mock Exam

**Format**: 20 tasks, 100 points, 2 VMs, 180 minutes.
**Passing score**: 70/100. **No hints** will be revealed.

## Your 2 machines

| Host | Initial IP | Role |
|---|---|---|
| `alma-rhcsa-1.lab` | DHCP (variable) | Main server — 16 tasks |
| `alma-rhcsa-2.lab` | DHCP (variable) | Client — 4 tasks dependent on the server |

Connect via `dsoxlab ssh alma-rhcsa-1.lab` (or `alma-rhcsa-2.lab` for the client). You are `student` with sudo NOPASSWD.

Changes must be **persistent after reboot**. A configuration that works after `reboot` but was applied only via a live command (without persistence) does not count.

---

## Section A — Storage and filesystems

### Task 1 — Partition the additional disk (4 pts)

The disk `/dev/vdb` (10 GiB) is attached to `alma-rhcsa-1`. Create a GPT table and 2 partitions:

- `/dev/vdb1`: 4 GiB, label `lvm-data`
- `/dev/vdb2`: 4 GiB, label `swap-extra`

### Task 2 — Create LVM and mount `/data` (6 pts)

On `/dev/vdb1`:

- Create a volume group `vgapp`
- Create a logical volume `lvdata` of **3 GiB**
- Format it as **XFS**
- Mount it on `/data` at boot via **UUID** (not by device path)

### Task 3 — Extend `lvdata` to 3.5 GiB online (5 pts)

Extend `lvdata` to **3.5 GiB**. The XFS filesystem must reflect the new size **without unmounting** or rebooting.

### Task 4 — 512 MiB swap file (4 pts)

Create `/swapfile` of 512 MiB enabled as swap, persistent at boot. Total swap (`free -m`) must increase by ~512 MiB.

### Task 5 — Export `/data/share` via NFS (6 pts)

On `alma-rhcsa-1`:

- Create `/data/share` (mode 0775, owner root, group `developers` — see task 7)
- Export it via NFS with **read/write** access only for `alma-rhcsa-2.lab`
- Open the required ports in `firewalld` (public zone, **permanent**)
- The `nfs-server` service must be active and enabled at boot

---

## Section B — Users, groups, permissions

### Task 6 — User `appuser` with password aging (5 pts)

Create the `appuser` account:

- UID exactly **1500**
- Shell `/bin/bash`
- Password aging: expiration every **60 days**, warning **7 days** before
- No initial password (key-based login only)

### Task 7 — Shared `developers` group (5 pts)

Create the group `developers` GID 2000.

- Create the user `devuser` (auto UID), add `devuser` and `appuser` to the `developers` group
- Create `/srv/shared` with:
  - Owner `root`, group `developers`
  - Permissions `2775` (setgid active → every created file inherits the group)
  - Every user in the group can write and everyone can read

### Task 8 — POSIX ACL on `/var/log/myapp.log` (4 pts)

The file `/var/log/myapp.log` exists (root:root, mode 0600). Grant `appuser` **rwx** rights via a POSIX ACL **without modifying** the file's standard owner/group/mode.

`getfacl /var/log/myapp.log` must show the line `user:appuser:rwx`.

---

## Section C — Networking

### Task 9 — Static IP + hostname + firewalld port on `srv-1` (6 pts)

On `alma-rhcsa-1`:

- Permanent static IP **`10.10.30.50/24`**, gateway **`10.10.30.1`**, DNS **`1.1.1.1`**
- Permanent hostname **`srv-rhcsa-1.lab`**
- Open port **8080/tcp** in firewalld public zone, permanent

### Task 17 — Client network configuration `srv-2` (4 pts)

On `alma-rhcsa-2`:

- Permanent static IP **`10.10.30.51/24`**, gateway **`10.10.30.1`**
- Permanent hostname **`srv-rhcsa-2.lab`**

---

## Section D — Services and scheduling

### Task 10 — systemd unit `myapp.service` (5 pts)

On `alma-rhcsa-1`, create `/usr/local/bin/myapp.sh` (a script that loops indefinitely, provides `/usr/local/bin/myapp.sh` bash shebang + `while true; do sleep 30; done`).

Create the unit `myapp.service`:

- `Type=simple`
- `ExecStart=/usr/local/bin/myapp.sh`
- `Restart=on-failure`
- `User=appuser`
- **Automatic startup at boot**
- The service must be active (running) at validation time

### Task 11 — Systemd timer `weekly-backup.timer` (4 pts)

On `alma-rhcsa-1`, create:

- `weekly-backup.service` that runs `/usr/local/bin/weekly-backup.sh` (you provide this script; it can just do `date >> /var/log/backup.log`)
- `weekly-backup.timer` that triggers the service every **Sunday at 03:00**, persistent
- The timer must be **active** and **enabled at boot**

### Task 12 — Chrony server on `srv-1` (4 pts)

Configure chrony on `alma-rhcsa-1` to:

- Synchronize with **`pool.ntp.org` iburst**
- **Allow `alma-rhcsa-2.lab` (10.10.30.51)** to query this server (`allow 10.10.30.51`)
- Service active and enabled at boot

---

## Section E — SELinux and security

### Task 13 — Restorecon `/var/www/html/index.html` (4 pts)

On `alma-rhcsa-1`, the file `/var/www/html/index.html` exists but has an incorrect SELinux context. Restore it to the standard context so that `httpd_t` can read it (`httpd_sys_content_t`).

### Task 14 — SELinux boolean `httpd_can_network_connect` (3 pts)

Enable the SELinux boolean `httpd_can_network_connect` **permanently** (persistent after reboot).

### Task 15 — SELinux port label 8888/tcp (3 pts)

Add the SELinux label **`http_port_t`** on port **8888/tcp**, permanent.

`semanage port -l | grep http_port_t` must list 8888.

### Task 19 — SSH key-only `srv-2 → srv-1/appuser` (7 pts)

On `alma-rhcsa-2`:

- Generate an ed25519 key in `~/.ssh/id_ed25519` (NoPass) for `appuser` (the user already exists after task 6 if you also created it on `srv-2`, otherwise create it locally with UID 1500)
- Place the public key in `appuser@alma-rhcsa-1.lab:~/.ssh/authorized_keys`
- `ssh appuser@10.10.30.50 hostname` from `srv-2` must return `srv-rhcsa-1.lab` **without a password prompt**
- Disable **`PasswordAuthentication no`** in `/etc/ssh/sshd_config` on `alma-rhcsa-2` (permanent, reload sshd)

---

## Section F — Client network storage

### Task 18 — Mount NFS at boot on `srv-2` (6 pts)

On `alma-rhcsa-2`, mount the NFS share exposed by `srv-1` (task 5):

- Mount point: `/mnt/share`
- Source: `alma-rhcsa-1.lab:/data/share`
- Persistent at boot via `/etc/fstab` with `_netdev` (and ideally `nofail` so it does not block boot if the server is down)

`mountpoint /mnt/share` must return `is a mountpoint` and the content must be readable.

---

## Section G — Software and boot

### Task 16 — Install `tree` via DNF + Flatpak `org.gnome.Calculator` (5 pts)

On `alma-rhcsa-1`:

- Install the **`tree`** package via `dnf` (from EPEL if not in the default repos — enable the `epel-release` repo if necessary)
- Configure access to the Flatpak **`flathub`** repo
- Install **`org.gnome.Calculator`** from Flathub (system-wide, not user)

### Task 20 — Reset root password on `srv-2` via rd.break (6 pts)

The root password on `alma-rhcsa-2` is **unknown** (your setup randomized it). You must reset it via the standard RHCSA procedure:

1. Reboot the VM
2. Interrupt GRUB (press `e` at the menu)
3. Add `rd.break` to the `linux …` line
4. Boot (Ctrl+X)
5. `mount -o remount,rw /sysroot`
6. `chroot /sysroot`
7. `passwd root` → set as the new password: **`SecureP@ss2026!`**
8. `touch /.autorelabel` (otherwise SELinux blocks the password file after reboot)
9. Exit, reboot

Validation: `ssh root@alma-rhcsa-2.lab` (from `alma-rhcsa-1` or locally) with the new password must work.

---

## Strategic tips

- **Order**: start with the **boot-persistent** tasks (1-9, 17), then the services. Do the root reset (task 20) **last** because it requires 2 reboots.
- **No live tinkering**: everything must be configured to persist across reboot. If you modified `/etc/sshd_config`, run `systemctl restart sshd`; if you modified `firewalld`, add `--permanent` then `--reload`.
- **Final check**: reboot both VMs before `dsoxlab check` to confirm persistence.
- **No internet help**: the `dsoxlab check` tests validate the **observable state**, not the path taken. man, `--help`, `/usr/share/doc/` are your only friends.

---

## Validation

```bash
dsoxlab check rhcsa-mock-exam       # affiche le score temps réel (sans le sauvegarder)
dsoxlab submit rhcsa-mock-exam       # soumission finale, enregistre dans l'historique
```

The score shows the weighting of each successful task. **70/100 = pass**.
