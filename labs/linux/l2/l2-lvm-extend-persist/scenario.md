# Context — /data is running out of space

On **alma-rhcsa-1.lab**, an application writes to `/data`, a 1 GiB XFS volume
backed by the logical volume `vgdata/lvdata`. The volume group still has free
space on its physical volume. You need to give `/data` more room **without
downtime** and make sure it stays that way after a reboot.

The trap: the logical volume and the filesystem sitting on it are two distinct
layers. Growing one is not enough, and until the other follows, the space you
added stays invisible to the application.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/
