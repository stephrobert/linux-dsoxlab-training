# Challenge — l3-grub-kernel-args

## Mission

Add the kernel parameter `panic=10` persistently.

## Goal (expected state)

1. The default kernel's arguments include `panic=10`
   (`grubby --info=DEFAULT`).
2. `/etc/default/grub` contains `panic=10` (for future kernels).

## Constraints

- Both the current kernels (`grubby`) and the template (`/etc/default/grub`) must
  have it — otherwise it's lost on the next kernel update.
- Validation reads `grubby --info=DEFAULT` and `/etc/default/grub`.

## Validation

```bash
dsoxlab check l3-grub-kernel-args
```
