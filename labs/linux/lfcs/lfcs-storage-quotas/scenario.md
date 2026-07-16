# Context — capping disk usage with XFS quotas

A shared filesystem with no quota is a filesystem one user can fill on their own.
**Quotas** cap how much space an account may consume — and on XFS they are not a
service you start: they are enabled **at mount time**, by a mount option. Forget
that option in `/etc/fstab` and your quotas silently vanish at the next reboot.

A dedicated 5 GB disk, **`/dev/vdb`**, is attached to the VM and still blank. The
user **`devops`** already exists.

Your mission, on the Ubuntu VM:

1. **Format** `/dev/vdb` as **XFS**.
2. **Mount** it on **`/srv/data`** with **user quotas enabled** (`uquota`), and
   make the mount **persistent** in `/etc/fstab` — with the quota option.
3. **Enforce** a block quota on `devops`: **40M soft**, **50M hard**.

The point: `xfs_quota -x -c "state -u" /srv/data` must report both
`Accounting: ON` **and** `Enforcement: ON` — accounting alone measures without
capping anything. And the fstab entry is what makes it all survive a reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/
