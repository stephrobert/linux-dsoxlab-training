# Lab — tune a mount with noatime

> Prepare: `dsoxlab provision` then `dsoxlab run l2-storage-performance`

## Recap

[**Disk performance on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/)

Mount options change how a filesystem behaves. `noatime` disables access-time
updates — a common win for read-heavy or many-small-files workloads. Put it in
`/etc/fstab` (4th field) for persistence, and `mount -o remount <mnt>` to apply
it live. `findmnt <mnt>` shows the active options.

## Objectives

On `/srv/data`:

- add `noatime` to the fstab options (`defaults,noatime`);
- `mount -o remount /srv/data` to activate it;
- `findmnt /srv/data` must show `noatime`.

## Validate

```bash
dsoxlab check l2-storage-performance
```
