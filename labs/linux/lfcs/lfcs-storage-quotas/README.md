# Lab — XFS user quotas

> Prepare: `dsoxlab provision` then `dsoxlab run lfcs-storage-quotas`

## Recap

[**Quotas on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/)

On XFS, quotas are enabled by a **mount option**, not by a service: `uquota`
(users) or `gquota` (groups). `xfs_quota -x -c "state -u" <mount>` shows two
distinct things — `Accounting` (measuring) and `Enforcement` (capping). Limits
are set with `xfs_quota -x -c "limit bsoft=… bhard=… <user>" <mount>` and read
back with `report -u -b`.

The mount option must be in `/etc/fstab`, otherwise the quotas are lost at the
next reboot.

## Objectives

- `/dev/vdb` formatted XFS and mounted on `/srv/data`;
- user quotas ON (accounting **and** enforcement), persistent via `/etc/fstab`;
- `devops` capped at 40M soft / 50M hard.

## Validate

```bash
dsoxlab check lfcs-storage-quotas
```
