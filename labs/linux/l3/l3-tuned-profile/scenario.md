# Context — tune the box for throughput

This machine runs data-heavy batch work but sits on the default **`balanced`**
tuned profile. Switch it to a profile built for **throughput**, so the kernel
knobs (CPU governor, I/O, VM) are set for sustained load — and make it survive a
reboot.

The point: `tuned` bundles dozens of kernel and sysfs settings into named
profiles, one per broad kind of workload. The chosen profile is recorded on disk,
and that is what makes it hold across reboots. What's left is picking the right
one and switching to it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/
