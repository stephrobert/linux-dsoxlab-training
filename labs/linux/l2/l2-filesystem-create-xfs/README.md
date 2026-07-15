# Lab — create an XFS filesystem

> Prepare: `dsoxlab provision` then `dsoxlab run l2-filesystem-create-xfs`

## Recap

[**XFS on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/)

`mkfs.xfs <device>` creates an XFS filesystem; `-L <label>` stamps a label
(`-f` forces over an existing signature). `blkid` and `lsblk -f` show the type,
label and UUID. A filesystem must be **mounted** on a directory to be used.

## Objectives

On the prepared partition:

- format it as XFS with label `DATA` (`mkfs.xfs -L DATA <part>`);
- create `/srv/xfs`;
- mount it there.

## Validate

```bash
dsoxlab check l2-filesystem-create-xfs
```
