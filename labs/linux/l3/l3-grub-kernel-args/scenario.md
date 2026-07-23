# Context — a kernel parameter that sticks

You need the kernel to reboot automatically ten seconds after a panic
(`panic=10`) — and it must hold across reboots **and** kernel updates. Editing the
live `/proc/cmdline` is impossible; the parameter belongs in the **bootloader**.

The point: a kernel parameter has to reach two distinct populations, the kernels
already installed and the ones installed tomorrow. Nothing guarantees a single
move covers both, and on a distribution using BLS boot entries that is exactly
where the trap springs.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/grub/
