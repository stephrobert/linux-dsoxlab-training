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

```bash
cat /root/raid-disks.env        # DISK1=... DISK2=...
. /root/raid-disks.env
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 "$DISK1" "$DISK2"
cat /proc/mdstat
sudo mkfs.xfs /dev/md0 && sudo mkdir -p /mnt/raid && sudo mount /dev/md0 /mnt/raid
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf
```

## Validation

```bash
dsoxlab check l2-raid-mdadm
```
