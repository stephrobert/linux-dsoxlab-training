# Mount only when needed

## The situation

Some filesystems shouldn't stay mounted all the time — a rarely-used disk, a
network share. **autofs** mounts them **on access** and unmounts them after an
idle timeout, saving resources and avoiding stale mounts. Here the spare disk
holds an XFS filesystem; wire it up so that touching `/autofs/data` mounts it.

The point: autofs mounts nothing until the path is actually used, and unmounts on
its own once nobody needs it. It still has to be told what to mount, and under
which path.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/autofs/

## What is asked

### Mission

Configure autofs to mount the extra disk on demand under `/autofs/data`.

### Goal (expected state)

1. The **autofs** service is running.
2. A **master** map maps `/autofs` to `/etc/auto.lab`.
3. The **mount** map `/etc/auto.lab` describes `data` as `xfs` toward the
   partition.
4. Accessing `/autofs/data` **triggers** the mount (`marker.txt` readable, xfs
   type).

### Constraints

- Target partition in `/root/autofs-disk.env`. `systemctl restart autofs` after
  editing the maps. Validation **triggers the access** and reads the real state.

### Validation

```bash
dsoxlab check l2-autofs-ondemand
```
