# Challenge — l2-lvm-extend-persist

## Mission

`/data` (XFS, 1 GiB, backed by `vgdata/lvdata`) is too small. Grow it, online,
and keep it persistent.

## Goal (expected state)

- `vgdata/lvdata` is **≥ 3 GiB**.
- The XFS filesystem of `/data` **reflects** the extension (`df` shows ≥ 3 G).
- `/data` is mounted and declared in `/etc/fstab` **by UUID** (survives reboot).

## Constraints

- Without unmounting `/data` (online extension).
- Validation checks the **system state**, not the commands typed:
  extending the LV without growing the XFS fails.

## Validation

```bash
dsoxlab check l2-lvm-extend-persist
```
