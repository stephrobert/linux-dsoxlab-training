# Challenge — l2 : Software RAID 1 with mdadm

## Mission

Two disks are available on **alma-rhcsa-1.lab** (their device names are in
`/root/raid-disks.env`). Build a **redundant RAID 1** that survives the loss of
one disk.

1. Create a **RAID 1** array `/dev/md0` from the two disks.
2. Format it (`mkfs.xfs`) and **mount** it on `/mnt/raid`.
3. Make it **persistent** by declaring it in `/etc/mdadm.conf`.

## Constraints

- The array must be level **raid1** with **2 active devices**.
- It must be mounted on `/mnt/raid`.
- `/etc/mdadm.conf` must contain its `ARRAY` line.

## Useful approach

The steps follow from the companion guide linked in the course's
`## Reminder`. If you get stuck, `dsoxlab hint` spells them out, at the
stated cost.

## Validation

```bash
dsoxlab check l2-raid-mdadm
```
