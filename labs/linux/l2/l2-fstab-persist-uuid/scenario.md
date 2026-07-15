# Context — make a disk mount survive a reboot

The machine has a spare disk, already formatted as ext4, but it is not mounted
and nothing declares it. Your job is to mount it at `/srv/data` and make that
mount **permanent** — the kind of task that fails RHCSA candidates when they
mount by hand and forget `/etc/fstab`, or reference the disk by a device name
that can change on the next boot.

Your mission, on the VM:

1. Find the disk's **UUID** (`blkid` / `lsblk -f`).
2. Create the mount point `/srv/data`.
3. Add an `/etc/fstab` entry that mounts it at `/srv/data`, **by UUID** — never
   by `/dev/vdX`.
4. Prove the entry is valid with `mount -a`, so it will remount on every boot.

The point: device names (`/dev/vdb`) are not stable across reboots; a UUID is.
An fstab entry by UUID is what makes the mount truly persistent.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/
