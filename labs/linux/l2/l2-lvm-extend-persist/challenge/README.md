# /data is running out of space

## The situation

On **alma-rhcsa-1.lab**, an application writes to `/data`, a 1 GiB XFS volume
backed by the logical volume `vgdata/lvdata`. The volume group still has free
space on its physical volume. You need to give `/data` more room **without
downtime** and make sure it stays that way after a reboot.

The trap: the logical volume and the filesystem sitting on it are two distinct
layers. Growing one is not enough, and until the other follows, the space you
added stays invisible to the application.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/lvm/

## What is asked

### Mission

`/data` (XFS, 1 GiB, backed by `vgdata/lvdata`) is too small. Grow it, online,
and keep it persistent.

### Goal (expected state)

- `vgdata/lvdata` is **≥ 3 GiB**.
- The XFS filesystem of `/data` **reflects** the extension (`df` shows ≥ 3 G).
- `/data` is mounted and declared in `/etc/fstab` **by UUID** (survives reboot).

### Constraints

- Without unmounting `/data` (online extension).
- Validation checks the **system state**, not the commands typed:
  extending the LV without growing the XFS fails.

### Validation

```bash
dsoxlab check l2-lvm-extend-persist
```
