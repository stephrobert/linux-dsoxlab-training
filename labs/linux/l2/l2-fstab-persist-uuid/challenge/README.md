# Challenge — l2-fstab-persist-uuid

## Mission

An additional disk is already formatted as **ext4** on the VM, but it is neither
mounted nor declared. Mount it on `/srv/data` **persistently**.

## Goal (expected state)

1. `/srv/data` is an **active** mount point.
2. The mounted filesystem is **ext4**.
3. `/etc/fstab` has an entry for `/srv/data` referenced **by UUID** (not
   `/dev/vdX`), whose **type** field is `ext4` (or `auto`).
4. The fstab UUID matches the actually mounted disk.
5. `sudo findmnt --verify` reports **no `parse error` and no `error`** on your
   line: that is what proves the mount will happen again at boot.

## Constraints

- Get the UUID with `blkid` or `lsblk -f`. Do not write the device name.
- `sudo mount -a` is **not enough** to validate an `fstab`: it exits 0 on a
  faulty line that is already mounted, or whose source cannot be found but is
  covered by `nofail`. Always check with both commands:
  `sudo systemctl daemon-reload`, then `sudo findmnt --verify`, then
  `sudo mount -a`.
- Validation queries the **real state** of the VM (mount, type, fstab content,
  `findmnt --verify` verdict).

## Validation

```bash
dsoxlab check l2-fstab-persist-uuid
```
