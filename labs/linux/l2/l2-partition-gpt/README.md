# Lab — GPT partitioning with parted

> Prepare: `dsoxlab provision` then `dsoxlab run l2-partition-gpt`

## Recap

[**Partitions on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/)

`parted -s <disk> mklabel gpt` writes a GPT table; `mkpart` cuts a partition
between two offsets (`1MiB 513MiB` → a 512 MiB partition). GPT lifts the MBR
limits (4 primaries, 2 TiB). After editing, `partprobe <disk>` makes the kernel
re-read the table so `<disk>1`, `<disk>2` appear; `lsblk` shows them.

## Objectives

On the spare disk:

- put a GPT label;
- partition 1 = 512 MiB;
- partition 2 = 1 GiB;
- `partprobe` so the kernel sees them.

## Validate

```bash
dsoxlab check l2-partition-gpt
```
