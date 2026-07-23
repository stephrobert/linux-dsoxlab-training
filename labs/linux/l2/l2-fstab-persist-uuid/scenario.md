# Context — make a disk mount survive a reboot

The machine has a spare disk, already formatted as ext4, but it is not mounted
and nothing declares it. Your job is to mount it at `/srv/data` and make that
mount **permanent** — the kind of task that fails RHCSA candidates when they
mount by hand and declare nothing, or when they reference the disk by a device
name that can change on the next boot.

The point: device names (`/dev/vdb`) are not stable across reboots; a UUID is.
What remains is finding where a permanent mount is declared, and how to name the
disk there by something other than its device name.

And above all, a question most people skip: once the line is written, how do you
know it is correct **before** rebooting? A server that fails to come back up is
discovered at the worst possible moment, and the one tool everybody quotes does
not see everything.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/
