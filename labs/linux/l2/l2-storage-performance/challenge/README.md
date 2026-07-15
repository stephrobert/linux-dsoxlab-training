# Challenge — l2-storage-performance

## Mission

`/srv/data` is mounted with the default options (atime enabled). Optimize it
for a read-heavy workload with `noatime`, durably.

## Goal (expected state)

1. `/srv/data` is **mounted**.
2. The real mount includes the **`noatime`** option (`findmnt /srv/data`).
3. `/etc/fstab` declares **`noatime`** for `/srv/data` (reboot persistence).

## Constraints

- Edit the fstab options (4th field), then `mount -o remount /srv/data` to
  apply without a reboot. Do not unmount / do not reformat.
- Validation reads the **real state** (mount options + fstab content).

## Validation

```bash
dsoxlab check l2-storage-performance
```
