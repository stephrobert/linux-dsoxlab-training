# Challenge — l3-fs-readonly-recover

## Mission

`/srv/data` is read-only and `/etc/fstab` is broken. Fix it.

## Goal (expected state)

1. `/srv/data` is mounted **read-write** (and writable).
2. `mount -a` succeeds (returns 0).
3. The invalid option (`defalts`) is gone from `/etc/fstab`.

## Constraints

- Fix the fstab entry, then `mount -o remount,rw /srv/data`. Test with
  `mount -a`. Validation reads the **actual state** (mount options, writability,
  mount -a).

## Validation

```bash
dsoxlab check l3-fs-readonly-recover
```
