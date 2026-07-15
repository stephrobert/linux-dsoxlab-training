# Lab — Extend a logical volume, persistently

> Prepare the VM: `dsoxlab run l2-lvm-extend-persist`

## Reminder

[**LVM on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/)

A logical volume can grow while it is mounted. The order matters: first
`lvextend` the logical volume, then grow the **filesystem** on top
(`xfs_growfs` for XFS, `resize2fs` for ext4). Extending the LV without growing
the filesystem is the single most common mistake: the extra space stays
invisible. Persistence lives in `/etc/fstab`, always by **UUID**.

## Objectives

- Extend the logical volume `vgdata/lvdata` to at least **3 GiB**.
- Grow the **XFS** filesystem so `/data` actually reflects the new size.
- Keep the mount persistent across reboots (fstab by UUID).

## Run and validate

```bash
dsoxlab run l2-lvm-extend-persist
# … solve on the VM …
dsoxlab check l2-lvm-extend-persist
```
