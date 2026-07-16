# Context — a kernel parameter that sticks

You need the kernel to reboot automatically ten seconds after a panic
(`panic=10`) — and it must hold across reboots **and** kernel updates. Editing the
live `/proc/cmdline` is impossible; the parameter belongs in the **bootloader**.

Your mission, on the VM:

1. Add `panic=10` to the **existing** kernels:
   `grubby --update-kernel=ALL --args="panic=10"`.
2. Add `panic=10` to **`GRUB_CMDLINE_LINUX`** in `/etc/default/grub` so **future**
   kernels (after an update) get it too.

The point: `grubby` edits the boot entries of installed kernels; `/etc/default/grub`
is the template `grub2-mkconfig` uses for newly installed kernels — you need both
for a parameter that truly persists. `grubby --info=DEFAULT` shows the default
kernel's current arguments.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/grub/
