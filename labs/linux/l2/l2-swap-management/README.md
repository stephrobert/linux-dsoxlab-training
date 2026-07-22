# Lab — Add and manage swap space

## Reminder

[**Manage swap on Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/)

Swap is a disk area the kernel uses as an overflow for RAM: when memory
fills up, idle pages are moved there. It absorbs spikes and enables
hibernation, but a box that swaps constantly is slow. A swap file is the
most flexible option; it must be mode `0600` because it holds memory pages.

## The course

The examples below work on `/var/swap-demo`, a demonstration file: the
challenge will ask you for another one, elsewhere and of another size. The goal
is to learn the method, not to copy a line.

### Where the machine stands

Before touching anything, look at what already exists:

```bash
free -h                # "Swap" column: total, used, free
swapon --show          # the active swap areas, or nothing at all
```

An empty output from `swapon --show` means no swap is active. That is the
starting state on a lab VM.

### Creating a swap file

Four steps, in this order. The order matters: you secure the file **before**
formatting it.

```bash
sudo dd if=/dev/zero of=/var/swap-demo bs=1M count=64 status=none
sudo chmod 0600 /var/swap-demo
sudo mkswap /var/swap-demo
sudo swapon /var/swap-demo
```

- **`dd`** allocates the file block by block. `bs=1M count=64` gives 64 MiB:
  the size is the product of the two.
- **`chmod 0600`** is not a stylistic precaution. The file contains memory
  pages, so potentially passwords or keys in clear text. Readable by everyone,
  it exposes the memory of the machine.
- **`mkswap`** writes the swap area signature and gives it a UUID.
- **`swapon`** activates it immediately.

Check, then deactivate to test the rest cleanly:

```bash
swapon --show          # /var/swap-demo must appear, type "file"
sudo swapoff /var/swap-demo
```

> **`dd` rather than `fallocate`.** The `swapon(8)` manual is explicit: a file
> created with `fallocate` is not reliable as swap on some filesystems, because
> it can contain holes (unallocated extents) that the kernel refuses. `dd`
> really writes the blocks.

### Making the swap persistent

`swapon` does not survive a reboot. For the swap to come back, you need a line
in `/etc/fstab`:

```text title="/etc/fstab"
/var/swap-demo none swap sw 0 0
```

The five fields, in order: the file (or the UUID for a partition), the mount
point, which does not exist for swap hence `none`, the `swap` type, the options
(`sw` is enough), then `0 0` for dump and fsck.

Test **without rebooting**, with `swapon -a` which activates every swap entry
declared in `fstab`:

```bash
sudo swapon -a
swapon --show
```

> **A mistake in `fstab` can block boot.** Back it up before editing
> (`sudo cp -a /etc/fstab /etc/fstab.bak`) and always check with
> `sudo swapon -a`: if the command passes without an error, the line is correct.

### Tuning the swappiness

`vm.swappiness` controls how **aggressive** the kernel is at moving pages to
swap. Contrary to a widespread idea, it is not a percentage of remaining RAM:
it is a relative weight between reclaiming cache memory and moving pages.

```bash
sysctl -n vm.swappiness         # 60 on many distributions,
                                # 30 on the VM of this lab: check, do not assume
```

A **low** value keeps the data in RAM and swaps only as a last resort, which is
what you want on a server that has enough memory. A high value swaps earlier.

A setting made on the fly disappears at reboot. For it to hold, you drop a file
in `/etc/sysctl.d/`:

```bash
echo "vm.swappiness = 45" | sudo tee /etc/sysctl.d/99-demo.conf
sudo sysctl -p /etc/sysctl.d/99-demo.conf
sysctl -n vm.swappiness         # must return 45
```

The name of the file matters little, but it ends in `.conf` and its numeric
prefix sets the reading order: `99-` comes last, so it wins.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `swapon: insecure permissions 0644` | the `chmod 0600` was forgotten or done after `mkswap` |
| `swapon: read swap header failed` | the file was not formatted by `mkswap` |
| The swap disappears at reboot | no line in `/etc/fstab` |
| `vm.swappiness` goes back to its initial value at reboot | setting made on the fly (`sysctl -w`), with no file in `/etc/sysctl.d/` |
| The value does not go back down after deleting the file | deleting the file resets nothing: the value lives in memory until the reboot. Set it back with `sudo sysctl -w vm.swappiness=<value>` |

To undo everything and start over:

```bash
sudo swapoff /var/swap-demo
sudo rm -f /var/swap-demo /etc/sysctl.d/99-demo.conf
sudo sysctl -w vm.swappiness=30      # removing the file is not enough
```
