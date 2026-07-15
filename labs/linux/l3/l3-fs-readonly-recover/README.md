# Lab — recover a read-only filesystem

> Prepare: `dsoxlab provision` then `dsoxlab run l3-fs-readonly-recover`

## Recap

[**Read-only filesystem recovery on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/)

`findmnt <mnt>` shows a mount's live options (`ro` vs `rw`). `mount -o remount,rw
<mnt>` switches it without unmounting. A bad option in `/etc/fstab` makes
`mount -a` fail — and a real boot would drop to emergency mode — so always test
fstab with `mount -a` after editing it.

## Objectives

- `/srv/data` remounted **read-write** and writable;
- `/etc/fstab` fixed so `mount -a` returns cleanly.

## Validate

```bash
dsoxlab check l3-fs-readonly-recover
```
