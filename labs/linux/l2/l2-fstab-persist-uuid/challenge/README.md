# Challenge — l2-fstab-persist-uuid

## Mission

An additional disk is already formatted as **ext4** on the VM, but it is neither
mounted nor declared. Mount it on `/srv/data` **persistently**.

## Goal (expected state)

1. `/srv/data` is an **active** mount point.
2. The mounted filesystem is **ext4**.
3. `/etc/fstab` has an entry for `/srv/data` referenced **by UUID** (not `/dev/vdX`).
4. The fstab UUID matches the actually mounted disk (`mount -a` succeeds).

## Constraints

- Get the UUID with `blkid` or `lsblk -f`. Do not write the device name.
- Validation queries the **real state** of the VM (mount, type, fstab content).

## Validation

```bash
dsoxlab check l2-fstab-persist-uuid
```
