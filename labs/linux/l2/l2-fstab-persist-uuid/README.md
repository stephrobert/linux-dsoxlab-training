# Lab — persistent mount by UUID

> Prepare: `dsoxlab provision` then `dsoxlab run l2-fstab-persist-uuid`

## Recap

[**Persistent mounts on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/)

`blkid` and `lsblk -f` show a filesystem's UUID. An `/etc/fstab` line
(`<what> <where> <fstype> <options> <dump> <pass>`) mounts it at boot. Reference
the disk by `UUID=` — device names like `/dev/vdb` can shift across reboots.
`mount -a` mounts everything in fstab and validates your entry without rebooting.

## Objectives

On the VM, mount the spare ext4 disk persistently:

- find its UUID (`blkid`);
- create `/srv/data`;
- add an fstab entry `UUID=<uuid> /srv/data ext4 defaults 0 0`;
- run `mount -a` — `/srv/data` must be mounted.

## Validate

```bash
dsoxlab check l2-fstab-persist-uuid
```
