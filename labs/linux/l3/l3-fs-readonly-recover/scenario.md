# Context — a data mount stuck read-only

Applications writing to `/srv/data` are failing: the filesystem is mounted
**read-only**, and worse, a typo has crept into `/etc/fstab` — on a real reboot
the box would drop into emergency mode. Diagnose and repair.

The point: an invalid mount option in `/etc/fstab` stays invisible until
something re-reads the file; at boot, it stops everything. So you need both:
make `/srv/data` writable again, and make sure the declaration is sound before
you would ever reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/
