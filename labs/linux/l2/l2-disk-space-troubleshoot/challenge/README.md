# The disk is full

## The situation

An alert fires: writes to `/srv/data` fail, "No space left on device". A
filesystem there is nearly full. Your job is the everyday ops reflex: find what
is eating the space and reclaim it — **without** deleting the data that matters.

The point: measuring how full a filesystem is and attributing that usage to the
directories causing it are two different moves. A classic gotcha (RHCSA): when
the two measurements disagree, a process is still holding a deleted-but-open
file, and the space only comes back when it lets go. Here, rest assured, the
culprit really is a file sitting on disk.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/disk-space/

## What is asked

### Mission

`/srv/data` is almost full on the VM. Diagnose and reclaim space.

### Goal (expected state)

1. `/srv/data` is **still mounted**.
2. Its usage is **under 50%**.
3. The legitimate file `/srv/data/app.log` is **kept**.

### Constraints

- Diagnose with `df -h` then `du -h --max-depth=1 /srv/data`. Delete only the
  superfluous (the cache), not the legitimate data; do not unmount/reformat.
- Validation reads the **real state** (mount, `df` usage, presence of app.log).

### Validation

```bash
dsoxlab check l2-disk-space-troubleshoot
```
