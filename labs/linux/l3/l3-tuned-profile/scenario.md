# Context — tune the box for throughput

This machine runs data-heavy batch work but sits on the default **`balanced`**
tuned profile. Switch it to a profile built for **throughput**, so the kernel
knobs (CPU governor, I/O, VM) are set for sustained load — and make it survive a
reboot.

Your mission, on the VM:

1. Set the active tuned profile to **`throughput-performance`**
   (`tuned-adm profile throughput-performance`).
2. Confirm it with `tuned-adm active`.

The point: `tuned` bundles dozens of kernel/sysfs settings into named profiles;
`tuned-adm list` shows them, `tuned-adm profile <name>` switches, and the choice
is stored (in `/etc/tuned/active_profile`) so it holds across reboots.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/
