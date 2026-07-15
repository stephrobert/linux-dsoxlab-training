# Context — a data mount stuck read-only

Applications writing to `/srv/data` are failing: the filesystem is mounted
**read-only**, and worse, a typo in `/etc/fstab` means `mount -a` errors out — on
a real reboot the box would drop into emergency mode. Diagnose and repair.

Your mission, on the VM:

1. Find why `/srv/data` is read-only and why `mount -a` fails (inspect
   `/etc/fstab` — one option is misspelled).
2. **Fix the fstab entry** so its options are valid.
3. **Remount** `/srv/data` read-write (`mount -o remount,rw /srv/data`).
4. Confirm `mount -a` now returns cleanly.

The point: an invalid mount option in `/etc/fstab` breaks `mount -a` and can
block boot; `findmnt` shows current options, `mount -o remount,rw` flips a mount
without unmounting, and `mount -a` is the safe way to test fstab before rebooting.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/
