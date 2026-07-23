# Context — capping disk usage with XFS quotas

A shared filesystem with no quota is a filesystem one user can fill on their own.
**Quotas** cap how much space an account may consume — and on XFS they are not a
service you start: they are enabled **at mount time**, by a mount option. Forget
that option in `/etc/fstab` and your quotas silently vanish at the next reboot.

A dedicated 5 GB disk, **`/dev/vdb`**, is attached to the VM and still blank. The
user **`devops`** already exists.

The point: accounting and enforcing are two different things. Quota accounting
that is on but not enforced protects nothing: the filesystem's quota state must
show both. And it is the `/etc/fstab` entry that makes the whole thing survive a
reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/
