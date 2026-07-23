# Context — aggregate two links for redundancy

Two network links should act as one, with failover: if the active one drops, the
other takes over. That's a **bond** in `active-backup` mode, with `miimon=100`.
On top of it sits a **bridge** — the layer where VMs or containers would attach.
Build both with NetworkManager, on dedicated interfaces, and make it persistent.

You work on `dummy1`, `dummy2`, `bond0` and `br0`. **Never touch the management
interface** — the one carrying your default route: it is your link to the box.

The point: a bond aggregates links (`active-backup` = redundancy, one active at a
time, `miimon` polls link state), and a bridge sits above to give a single L2
domain. NetworkManager keeps each one as a connection profile on disk, and that
profile is what makes the whole thing survive a reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/
