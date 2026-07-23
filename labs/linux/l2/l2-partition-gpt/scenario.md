# Context — carve a disk with GPT

The machine has a spare, blank disk: that one, and only that one, is what you
carve. Before it can hold a filesystem, LVM member or RAID device, it needs a
**partition table**. Modern systems use **GPT** (no 4-partition / 2 TiB limits of
the old MBR). Your job is to lay down GPT and cut two partitions.

The point: writing a partition table is not enough to make it visible. The kernel
keeps its view of the old one until you ask it to re-read the disk, or until the
machine reboots.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/
