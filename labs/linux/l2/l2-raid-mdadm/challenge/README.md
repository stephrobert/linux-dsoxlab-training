# Add redundant storage with software RAID

## The situation

On **alma-rhcsa-1.lab**, a small service stores data that must survive a single
disk failure. You don't have a hardware RAID controller, so you'll use **Linux
software RAID** with `mdadm`.

Two spare disks are attached to the machine; their device names are recorded in
`/root/raid-disks.env`, and they are the only ones you may touch. What you need
out of them is a mirror that holds up, and that is still there after a reboot.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/raid-mdadm/

## L2 : Software RAID 1 with mdadm

### Mission

Two disks are available on **alma-rhcsa-1.lab** (their device names are in
`/root/raid-disks.env`). Build a **redundant RAID 1** that survives the loss of
one disk.

1. Create a **RAID 1** array `/dev/md0` from the two disks.
2. Format it (`mkfs.xfs`) and **mount** it on `/mnt/raid`.
3. Make it **persistent** by declaring it in `/etc/mdadm.conf`.

### Constraints

- The array must be level **raid1** with **2 active devices**.
- It must be mounted on `/mnt/raid`.
- `/etc/mdadm.conf` must contain its `ARRAY` line.

### Useful approach

The steps follow from the companion guide linked in the course's
`## Reminder`. If you get stuck, `dsoxlab hint` spells them out, at the
stated cost.

### Validation

```bash
dsoxlab check l2-raid-mdadm
```
