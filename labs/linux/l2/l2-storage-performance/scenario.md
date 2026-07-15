# Context — stop wasting I/O on access times

`/srv/data` serves a read-heavy workload. By default Linux updates each file's
**access time** (atime) on reads, which turns reads into writes and hurts
performance. The standard fix is the **`noatime`** mount option. Your job is to
apply it — now and permanently.

Your mission, on the VM:

1. Add **`noatime`** to the mount options of `/srv/data` in `/etc/fstab`.
2. Apply it **without rebooting** (`mount -o remount /srv/data`).
3. Confirm it is active (`findmnt /srv/data` shows `noatime`).

The point: mount options tune a filesystem's behaviour; `noatime` skips atime
updates. Editing `/etc/fstab` makes it survive a reboot; `mount -o remount` makes
it take effect immediately without unmounting.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/
