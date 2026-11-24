# A kernel parameter that sticks

## The situation

You need the kernel to reboot automatically ten seconds after a panic
(`panic=10`) — and it must hold across reboots **and** kernel updates. Editing the
live `/proc/cmdline` is impossible; the parameter belongs in the **bootloader**.

The point: a kernel parameter has to reach two distinct populations, the kernels
already installed and the ones installed tomorrow. Nothing guarantees a single
move covers both, and on a distribution using BLS boot entries that is exactly
where the trap springs.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/grub/

## What is asked

### Mission

Add the kernel parameter `panic=10` persistently.

### Goal (expected state)

1. The default kernel's arguments include `panic=10`
   (`grubby --info=DEFAULT`).
2. `/etc/default/grub` contains `panic=10` (for future kernels).

### Constraints

- Both the current kernels (`grubby`) and the template (`/etc/default/grub`) must
  have it — otherwise it's lost on the next kernel update.
- Validation reads `grubby --info=DEFAULT` and `/etc/default/grub`.

### Validation

```bash
dsoxlab check l3-grub-kernel-args
```
