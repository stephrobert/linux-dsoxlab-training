# Put a real filesystem on a partition

## The situation

A blank partition is waiting. A partition is just reserved space until it holds a
**filesystem**. Your job is to format it as **XFS** (the RHEL default, great for
large files and scaling), give it a **label** so it is easy to identify, and
mount it.

The point: a label is a tag carried by the filesystem itself. It lets you refer
to that filesystem by a stable name instead of a fragile device name that can
change from one boot to the next.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/xfs/

## What is asked

### Mission

A blank partition is ready on the VM (see `lsblk`). Format it and mount it.

### Goal (expected state)

1. The partition carries an **XFS** filesystem.
2. Its **label** is `DATA`.
3. It is **mounted** on `/srv/xfs`.
4. The mount is of type **xfs**.

### Constraints

- `mkfs.xfs -L DATA <partition>` for the format + label, `mount` for the mount.
  Spot the partition with `lsblk` (the one without a filesystem).
- Validation reads the **real state** (type, label, mount), not the command.

### Validation

```bash
dsoxlab check l2-filesystem-create-xfs
```
