# A data mount stuck read-only

## The situation

Applications writing to `/srv/data` are failing: the filesystem is mounted
**read-only**, and worse, a typo has crept into `/etc/fstab` — on a real reboot
the box would drop into emergency mode. Diagnose and repair.

The point: an invalid mount option in `/etc/fstab` stays invisible until
something re-reads the file; at boot, it stops everything. So you need both:
make `/srv/data` writable again, and make sure the declaration is sound before
you would ever reboot.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/troubleshoot/read-only-filesystem/

## What is asked

### Mission

`/srv/data` is read-only and `/etc/fstab` is broken. Fix it.

### Goal (expected state)

1. `/srv/data` is mounted **read-write** (and writable).
2. `mount -a` succeeds (returns 0).
3. The invalid option (`defalts`) is gone from `/etc/fstab`.

### Constraints

- Fix the fstab entry, then `mount -o remount,rw /srv/data`. Test with
  `mount -a`. Validation reads the **actual state** (mount options, writability,
  mount -a).

### Validation

```bash
dsoxlab check l3-fs-readonly-recover
```
