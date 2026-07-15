# Context — /data is running out of space

On **alma-rhcsa-1.lab**, an application writes to `/data`, a 1 GiB XFS volume
backed by the logical volume `vgdata/lvdata`. The volume group still has free
space on its physical volume. You need to give `/data` more room **without
downtime** and make sure it stays that way after a reboot.

Your mission:

1. Extend `vgdata/lvdata` to at least **3 GiB**.
2. Grow the **XFS** filesystem so `/data` really shows the new size.
3. Confirm the mount is persistent (declared in `/etc/fstab` by UUID).

The trap: extending the logical volume is not enough. If you forget to grow the
filesystem, `df -h /data` still shows 1 GiB and the space you added is wasted.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/
