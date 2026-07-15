# Lab — Add and manage swap space

> Each lab is self-contained. Requirement: the lab VM must be running and
> reachable via SSH+sudo. Prepare it with:
>
> ```bash
> dsoxlab run l2-04-swap-management
> ```

## Reminder

[**Manage swap on Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/)

Swap is a disk area the kernel uses as an overflow for RAM: when memory
fills up, idle pages are moved there. It absorbs spikes and enables
hibernation, but a box that swaps constantly is slow. A swap file is the
most flexible option; it must be mode `0600` because it holds memory pages.

## Objectives

By the end of this lab, you will know how to:

- Create a **secure swap file** (`0600`) and activate it (`mkswap`, `swapon`).
- Make swap **persistent** across reboots via `/etc/fstab`.
- Tune **`vm.swappiness`** durably with a `/etc/sysctl.d/` drop-in.

## Run and validate

```bash
dsoxlab run   l2-04-swap-management    # prepare the VM
dsoxlab check l2-04-swap-management    # score your work
```
