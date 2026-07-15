# Challenge — l2-filesystem-create-xfs

## Mission

A blank partition is ready on the VM (see `lsblk`). Format it and mount it.

## Goal (expected state)

1. The partition carries an **XFS** filesystem.
2. Its **label** is `DATA`.
3. It is **mounted** on `/srv/xfs`.
4. The mount is of type **xfs**.

## Constraints

- `mkfs.xfs -L DATA <partition>` for the format + label, `mount` for the mount.
  Spot the partition with `lsblk` (the one without a filesystem).
- Validation reads the **real state** (type, label, mount), not the command.

## Validation

```bash
dsoxlab check l2-filesystem-create-xfs
```
