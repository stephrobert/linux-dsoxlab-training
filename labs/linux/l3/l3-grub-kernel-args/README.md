# Lab — persistent kernel boot parameter

## Reminder

[**GRUB on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/grub/)

`grubby --update-kernel=ALL --args="param"` adds a kernel argument to the
installed kernels; `--remove-args` removes it; `--info=DEFAULT` shows the
default kernel's args. The template for **future** kernels is
`GRUB_CMDLINE_LINUX` in `/etc/default/grub`.

The state to reach is the same in every case: the parameter present in **both**
places. How many moves it takes depends on the machine: on the AlmaLinux 10
measured in this course, `--update-kernel=ALL` writes both; when targeting a
specific kernel or `DEFAULT`, it only writes the entry you aimed at. Hence the
one rule that holds everywhere: **read both locations back**, never assume them.

## The course

The examples below set the `audit=1` and `rd.timeout=30` parameters: the
challenge will ask you for another parameter. The point is to learn the
mechanics and above all to know how to **check it before rebooting**, not to
copy a line. All the outputs on this page were taken on an **AlmaLinux 10.2**
(kernel `6.12.0-211.34.1.el10_2.x86_64`) booted in **UEFI**.

> A faulty parameter makes the machine unbootable, and on a VM without a
> console there is no way back. Before anything else: back up
> `/etc/default/grub` and record `cat /proc/cmdline`, which is your reference
> for returning. Never add a parameter you do not understand, and never
> **remove** a parameter that is already there (`console=`, `root=` and `ro`
> serve the platform).

### Three files, and none of them is the one you think

The command line actually received by the kernel is read in `/proc/cmdline`:

```bash
cat /proc/cmdline
```

```text
BOOT_IMAGE=(hd0,gpt3)/vmlinuz-6.12.0-211.34.1.el10_2.x86_64 root=UUID=1f5fce98-2902-4ac3-b784-b4f10857f44e ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0
```

This file is a view of the running kernel: you do not edit it, you change
**what produces it**. Three files contribute to it, with very different
statuses.

```bash
cat /etc/default/grub
```

```text
GRUB_TIMEOUT=0
GRUB_DEFAULT=saved
[...]
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0"
GRUB_ENABLE_BLSCFG=true
```

`/etc/default/grub` is **not** read at boot: it is an **input** file for
`grub2-mkconfig`. And the last line, `GRUB_ENABLE_BLSCFG=true`, governs
everything else: the boot entries do not live in `grub.cfg` but in **BLS**
(*BootLoaderSpec*) files, one per installed kernel.

```bash
ls /boot/loader/entries/
sudo cat /boot/loader/entries/*-6.12.0-211.34.1.el10_2.x86_64.conf
```

```text
title AlmaLinux (6.12.0-211.34.1.el10_2.x86_64) 10.2 (Lavender Lion)
version 6.12.0-211.34.1.el10_2.x86_64
linux /vmlinuz-6.12.0-211.34.1.el10_2.x86_64
initrd /initramfs-6.12.0-211.34.1.el10_2.x86_64.img $tuned_initrd
options root=UUID=1f5fce98-[...] ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 $tuned_params
[...]
```

It is the **`options`** line that becomes `/proc/cmdline`. The trailing
`$tuned_params` is a variable that GRUB expands at boot: it is normal, do not
remove it.

As for `grub.cfg`, it no longer contains any kernel entry:

```bash
sudo grep -nE 'insmod blscfg|^blscfg|set kernelopts' /boot/grub2/grub.cfg
```

```text
132:  set kernelopts="root=UUID=1f5fce98-[...] no_timer_check biosdevname=0 net.ifnames=0 "
135:insmod blscfg
136:blscfg
```

The `blscfg` command goes and reads `/boot/loader/entries/`. The `set
kernelopts` on line 132 is only a **fallback**, used if the variable is defined
neither in `grubenv` nor in the BLS entry. Here each entry carries its own
`options` line: that fallback is never used, and this explains the surprise to
come.

### The generated file: find it, do not assume it

The path of the active `grub.cfg` depends on the boot mode, and targeting the
wrong one is a classic mistake. So start by determining that mode:

```bash
ls -d /sys/firmware/efi     # present: UEFI ; absent: legacy BIOS
sudo find /boot -name grub.cfg
```

```text
/sys/firmware/efi
/boot/efi/EFI/almalinux/grub.cfg
/boot/grub2/grub.cfg
```

Two files, then, and you must know which one to regenerate. The one on the EFI
partition is only four lines long:

```text
search --no-floppy --root-dev-only --fs-uuid --set=dev cea79fb2-[...]
set prefix=($dev)/grub2
export $prefix
configfile $prefix/grub.cfg
```

It is a **stub**: it looks for the partition carrying that UUID (here
`/dev/vda3`, mounted on `/boot`, which `blkid` and `findmnt /boot` confirm),
then loads `/boot/grub2/grub.cfg`. The real configuration is therefore the one
in `/boot/grub2/`, even under UEFI, as the distribution's symbolic links
confirm:

```bash
ls -l /etc/grub2.cfg /etc/grub2-efi.cfg
```

```text
/etc/grub2.cfg -> ../boot/grub2/grub.cfg
/etc/grub2-efi.cfg -> ../boot/grub2/grub.cfg
```

The companion guide reports that on AlmaLinux 9.8 the active `grub.cfg` was
still in `/boot/efi/EFI/almalinux/` and that `/boot/grub2/grub.cfg` did not
exist. On the AlmaLinux 10.2 measured here, the unification is done, and its
lesson stands in full: **locate your `grub.cfg` with `find` instead of assuming
its path**. In every case you never edit it by hand, it is rewritten at every
kernel update.

### Editing `/etc/default/grub` is not enough: the demonstration

Let us add `audit=1` to the template, without regenerating anything. The `sed`
takes the existing content between quotes and appends the parameter at the end,
which guarantees that none is removed:

```bash
sudo cp /etc/default/grub /root/grub.bak
sudo sed -i 's/^GRUB_CMDLINE_LINUX="\(.*\)"/GRUB_CMDLINE_LINUX="\1 audit=1"/' /etc/default/grub
grep GRUB_CMDLINE_LINUX /etc/default/grub
```

```text
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 audit=1"
```

Nothing else moved on disk: the checksums of `grub.cfg` and of the two BLS
entries are unchanged. After a `sudo reboot`, `/proc/cmdline` is strictly
identical to the one at the top of this page, **without `audit=1`**: the file
we just edited is read by nobody at boot.

Now regenerate the configuration:

```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

```text
Generating grub configuration file ...
Adding boot menu entry for UEFI Firmware Settings ...
done
```

Here is the second surprise, specific to BLS systems: only the **fallback** in
`grub.cfg` received the parameter.

```text
132:  set kernelopts="root=UUID=1f5fce98-[...] net.ifnames=0 audit=1 "
```

The `options` lines of the BLS entries kept the same checksum, and `grubby
--info=DEFAULT` still does not show `audit=1`. A second reboot confirmed it:
`/proc/cmdline` is again identical to the original. On a machine in BLS mode,
`grub2-mkconfig` **does not rewrite the already installed boot entries**.

What the regeneration did do, on the other hand, is update the template for
**future** kernels:

```bash
sudo cat /etc/kernel/cmdline
```

```text
root=UUID=1f5fce98-[...] ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 audit=1
```

This is the file read by `/usr/lib/kernel/install.d/20-grub.install` to build
the BLS entry of a freshly installed kernel. The script says so itself, and
resynchronises along the way if `/etc/default/grub` is more recent:

```text
if [[ /etc/kernel/cmdline -ot /etc/default/grub ]]; then
    grub2-mkconfig -o /etc/grub2.cfg      # user modified /etc/default/grub manually; sync
fi
read -r -d '' -a BOOT_OPTIONS < /etc/kernel/cmdline
```

### `grubby`: the tool that touches existing entries

`grubby` (package `grubby`, installed by default) reads and writes the boot
entries directly.

```bash
sudo grubby --default-kernel        # which kernel boots by default
sudo grubby --info=DEFAULT          # its arguments
sudo grubby --info=ALL              # all entries, with their index
```

```text
index=1
kernel="/boot/vmlinuz-6.12.0-211.34.1.el10_2.x86_64"
args="ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 $tuned_params"
root="UUID=1f5fce98-[...]"
[...]
```

Let us add the parameter to the installed kernels:

```bash
sudo grubby --update-kernel=ALL --args="audit=1"
sudo grep -h ^options /boot/loader/entries/*.conf
```

```text
options root=UUID=1f5fce98-[...] net.ifnames=0 $tuned_params audit=1
options root=UUID=1f5fce98-[...] net.ifnames=0 audit=1
```

The effect is immediate in the entry files, without any regeneration. After a
reboot, the parameter is finally there:

```text
BOOT_IMAGE=(hd0,gpt3)/vmlinuz-6.12.0-211.34.1.el10_2.x86_64 root=UUID=[...] ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 audit=1
```

Two behaviours of `grubby` deserve to be known, because they were measured here
and the guide does not describe them. The first: with `--update-kernel=ALL`,
`grubby` also updates `GRUB_CMDLINE_LINUX` in `/etc/default/grub` **and**
`/etc/kernel/cmdline`. A single command therefore covers the installed kernels
and the future ones. The second: this is true **only** for `ALL`. When
targeting a specific kernel, or with the `DEFAULT` keyword, only the targeted
entry changes and the template stays intact.

```bash
sudo grubby --update-kernel=/boot/vmlinuz-6.12.0-211.7.3.el10_2.x86_64 --args="rd.timeout=30"
grep GRUB_CMDLINE_LINUX /etc/default/grub    # unchanged
```

Removal follows the same logic, and `--remove-args` on `ALL` also cleans the
three locations:

```bash
sudo grubby --update-kernel=/boot/vmlinuz-6.12.0-211.7.3.el10_2.x86_64 --remove-args="rd.timeout=30"
sudo grubby --update-kernel=ALL --remove-args="audit=1"
```

Do not conclude that remembering "`ALL` does everything" is enough: read both
places afterwards, that is the gesture that will save you on a machine whose
`grubby` version behaves otherwise.

### Check before rebooting, then afterwards

This is what separates a safe operation from a bet. **Before** the reboot,
re-read the line that will actually be used and make sure it still carries
`root=`, `ro` and the original parameters:

```bash
sudo grep -h ^options /boot/loader/entries/*.conf
sudo grubby --info=DEFAULT
```

An `options` line without `root=` is a lost machine. On a system without BLS
(`GRUB_ENABLE_BLSCFG=false`, or a Debian), the same check applies to the
`linux` lines of the generated `grub.cfg`:

```bash
sudo grep -E '^[[:space:]]+linux' /boot/grub2/grub.cfg
```

**After** the reboot, `/proc/cmdline` is authoritative. The kernel log gives
the same information, with a bonus:

```bash
sudo journalctl -k -b | grep -i 'command line'
```

```text
kernel: Kernel command line: BOOT_IMAGE=[...] net.ifnames=0 audit=1
kernel: Unknown kernel command line parameters "BOOT_IMAGE=(hd0,gpt3)/vmlinuz-6.12.0-211.34.1.el10_2.x86_64 biosdevname=0", will be passed to user space.
```

The second line lists what the kernel did not consume: this is where a
misspelled parameter shows up. Do not read it too quickly, it already contains
legitimate entries (here `BOOT_IMAGE` and `biosdevname=0`, meant for user
space); but a parameter you have just added and that ends up there is a
parameter being ignored.

### The volatile change in the GRUB menu

In the GRUB menu, the **`e`** key opens the selected entry for editing. You
move to the line starting with `linux`, add or remove a parameter, then
**`Ctrl+X`** (or `F10`) boots with that modified line. Nothing is written to
disk: at the next boot, the original entry comes back unchanged.

This is the recovery skill of the subject, and it is also the reason for the
GRUB password described in the companion guide: whoever reaches this menu can
add `init=/bin/bash` and get a root shell without authentication.

**This operation was not performed for this course**: it requires a graphical
or serial console, which the workshop machine does not have, and the
`GRUB_TIMEOUT=0` of this image leaves no delay to display the menu anyway. The
difference to remember is the one of medium: editing in the menu lives in
memory for the duration of one boot, `grubby` and `/etc/default/grub` write to
disk and survive reboots.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `/proc/cmdline` unchanged after editing `/etc/default/grub` | no regeneration, or a system in BLS mode where `grub2-mkconfig` does not touch existing entries: go through `grubby` |
| `grubby --info=DEFAULT` does not show the parameter | change made in `/etc/default/grub` only |
| Parameter present today, lost after a kernel update | the template did not follow: check `/etc/default/grub` and `/etc/kernel/cmdline` |
| The parameter appears in `Unknown kernel command line parameters` | typo, or parameter meant for user space |
| Changes lost after a package update | `grub.cfg` edited by hand, whereas it is regenerated: go through `/etc/default/grub` |
| `grub.cfg` not found at the expected path | the path varies between BIOS and UEFI: `find /boot -name grub.cfg` |
| Machine that no longer boots | `options` line without `root=`, or a parameter touching disk, network or init: no repair possible without a console, hence the systematic check **before** the reboot |

To undo everything and return to the initial state:

```bash
sudo grubby --update-kernel=ALL --remove-args="audit=1"
sudo cp /root/grub.bak /etc/default/grub
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo reboot
```

On return, `cat /proc/cmdline` must give back exactly the value recorded at the
start. That is the only check that matters.
