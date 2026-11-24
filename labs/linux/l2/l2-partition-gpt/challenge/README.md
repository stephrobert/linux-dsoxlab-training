# Carve a disk with GPT

## The situation

The machine has a spare, blank disk: that one, and only that one, is what you
carve. Before it can hold a filesystem, LVM member or RAID device, it needs a
**partition table**. Modern systems use **GPT** (no 4-partition / 2 TiB limits of
the old MBR). Your job is to lay down GPT and cut two partitions.

The point: writing a partition table is not enough to make it visible. The kernel
keeps its view of the old one until you ask it to re-read the disk, or until the
machine reboots.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/partitions/

## What is asked

### Mission

The VM's additional disk is **blank**. Lay down a GPT table and two partitions.

### Goal (expected state)

1. The disk has a **GPT** partition table.
2. **Two** partitions.
3. Partition 1 = **512 MiB**.
4. Partition 2 = **1 GiB**.
5. The table is re-read by the kernel (`partprobe`) — the partitions appear
   in `lsblk`.

### Constraints

- `parted` (or `fdisk`) for the table and the partitions ; `partprobe` to
  inform the kernel. Locate the disk with `lsblk` (the disk without partitions).
- Validation reads the **real state** (PTTYPE, partitions, sizes), not the command.

### Validation

```bash
dsoxlab check l2-partition-gpt
```
