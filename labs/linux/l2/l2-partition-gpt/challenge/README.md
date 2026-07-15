# Challenge — l2-partition-gpt

## Mission

The VM's additional disk is **blank**. Lay down a GPT table and two partitions.

## Goal (expected state)

1. The disk has a **GPT** partition table.
2. **Two** partitions.
3. Partition 1 = **512 MiB**.
4. Partition 2 = **1 GiB**.
5. The table is re-read by the kernel (`partprobe`) — the partitions appear
   in `lsblk`.

## Constraints

- `parted` (or `gdisk`) for the table and the partitions ; `partprobe` to
  inform the kernel. Locate the disk with `lsblk` (the disk without partitions).
- Validation reads the **real state** (PTTYPE, partitions, sizes), not the command.

## Validation

```bash
dsoxlab check l2-partition-gpt
```
