# Stop wasting I/O on access times

## The situation

`/srv/data` serves a read-heavy workload. By default Linux updates each file's
**access time** (atime) on reads, which turns reads into writes and hurts
performance. The standard fix is the **`noatime`** mount option. Your job is to
apply it — now and permanently.

The point: mount options tune a filesystem's behaviour; `noatime` skips atime
updates. What remains is working out how to make it effective right away **and**
persistent across a reboot: those are two distinct moves.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/disk-performance/

## What is asked

### Mission

`/srv/data` is mounted with the default options (atime enabled). Optimize it
for a read-heavy workload with `noatime`, durably.

### Goal (expected state)

1. `/srv/data` is **mounted**.
2. The real mount includes the **`noatime`** option (`findmnt /srv/data`).
3. `/etc/fstab` declares **`noatime`** for `/srv/data` (reboot persistence).

### Constraints

- Edit the fstab options (4th field), then `mount -o remount /srv/data` to
  apply without a reboot. Do not unmount / do not reformat.
- Validation reads the **real state** (mount options + fstab content).

### Validation

```bash
dsoxlab check l2-storage-performance
```
