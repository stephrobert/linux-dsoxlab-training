# Lab — Extend a logical volume, persistently

## Reminder

[**LVM on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/)

A logical volume can grow while it is mounted. The order matters: first
`lvextend` the logical volume, then grow the **filesystem** on top
(`xfs_growfs` for XFS, `resize2fs` for ext4). Extending the LV without growing
the filesystem is the single most common mistake: the extra space stays
invisible. Persistence lives in `/etc/fstab`, always by **UUID**.

## The course

The examples below build a demonstration stack: a volume group `vgatelier`, a
logical volume `lvarchives` mounted on `/srv/archives`. The challenge will ask
you for different names, a different mount point and different sizes. The goal
is to learn the method, not to copy a line.

All the output below was produced on an **AlmaLinux 10.2** VM with
`lvm2-2.03.36`, `xfsprogs-6.16.0` and `e2fsprogs-1.47.1`. LVM messages have
changed shape between versions: read yours, do not assume them.

### First of all: know which disk you are working on

This is the precaution that looks like nothing until the day it is missing. An
LVM command does not ask for confirmation when it overwrites a system disk. So
look at **what exists** before naming a target:

```bash
lsblk
sudo pvs
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sr0     11:0    1   46K  0 rom
vda    252:0    0   10G  0 disk
├─vda1 252:1    0    1M  0 part
├─vda2 252:2    0  200M  0 part /boot/efi
├─vda3 252:3    0    1G  0 part /boot
└─vda4 252:4    0  8.8G  0 part /
vdb    252:16   0    2G  0 disk
```

`pvs` returns **nothing**: no LVM physical volume exists yet on this machine.
`lsblk` shows that `/dev/vda` carries `/boot`, `/boot/efi` and `/`, as plain
partitions. That is the system disk: leave it alone. The free disk is
`/dev/vdb`, 2 GiB, with no mount point at all.

On other installations, `/` is itself in a logical volume. In that case `pvs`
answers, and `lsblk` shows lines of type `lvm` under `vda`. All the more reason
to **always name the target explicitly** (`/dev/vdb1`) rather than rely on a
shortcut.

### The PV / VG / LV model

LVM stacks three layers, and everything else follows from that:

| Layer | What it is | Creation command |
|---|---|---|
| **PV** (*Physical Volume*) | a disk or a partition initialised for LVM | `pvcreate` |
| **VG** (*Volume Group*) | a pool of space aggregating one or more PVs | `vgcreate` |
| **LV** (*Logical Volume*) | a slice carved out of the VG, which you format and mount | `lvcreate` |

The benefit: an LV is no longer tied to a specific disk. When the LV fills up,
you grow it from the VG; when the VG runs out of space, you add a disk to it.
Without reformatting, without unmounting.

Three inspection commands, one per layer, to know by heart: `pvs`, `vgs`,
`lvs`. Their variants `pvdisplay`, `vgdisplay`, `lvdisplay` give more detail.

### Building the demonstration stack

First carve the free disk into two partitions flagged for LVM. Two partitions
and not one: they will be used later to show how to grow a volume group that is
already full.

```bash
sudo parted -s /dev/vdb mklabel gpt
sudo parted -s /dev/vdb mkpart lvm1 1MiB 1300MiB
sudo parted -s /dev/vdb mkpart lvm2 1300MiB 100%
sudo parted -s /dev/vdb set 1 lvm on
sudo parted -s /dev/vdb set 2 lvm on
sudo partprobe /dev/vdb
lsblk /dev/vdb
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
vdb    252:16   0    2G  0 disk
├─vdb1 252:17   0  1.3G  0 part
└─vdb2 252:18   0  747M  0 part
```

Then the stack itself:

```bash
sudo pvcreate /dev/vdb1
sudo vgcreate vgatelier /dev/vdb1
sudo lvcreate -L 512M -n lvarchives vgatelier
```

```text
  Physical volume "/dev/vdb1" successfully created.
  Creating devices file /etc/lvm/devices/system.devices
  Volume group "vgatelier" successfully created
  Logical volume "lvarchives" created.
```

The `Creating devices file` line appears on the very first `pvcreate` of the
machine: LVM 2.03 keeps in `/etc/lvm/devices/system.devices` the list of
devices it allows itself to use. It is an informational note, not an error.

The logical volume is reachable through two equivalent paths:
`/dev/vgatelier/lvarchives` and `/dev/mapper/vgatelier-lvarchives`. You inspect
it layer by layer:

```bash
sudo pvs
sudo vgs
sudo lvs
```

```text
  PV         VG        Fmt  Attr PSize  PFree
  /dev/vdb1  vgatelier lvm2 a--  <1.27g 784.00m

  VG        #PV #LV #SN Attr   VSize  VFree
  vgatelier   1   1   0 wz--n- <1.27g 784.00m

  LV         VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lvarchives vgatelier -wi-a----- 512.00m
```

`VFree` is the column that decides everything: 784 MiB still available in the
pool, which is exactly the room for extension.

What remains is to format and mount, like any other partition:

```bash
sudo mkfs.xfs /dev/vgatelier/lvarchives
sudo mkdir -p /srv/archives
sudo mount /dev/vgatelier/lvarchives /srv/archives
findmnt /srv/archives
df -h /srv/archives
```

```text
TARGET        SOURCE                           FSTYPE OPTIONS
/srv/archives /dev/mapper/vgatelier-lvarchives xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  448M   35M  414M   8% /srv/archives
```

A first discrepancy not to mistake for a bug: the LV is **512 MiB**, `df`
reports **448 MiB**. The difference is taken up by XFS metadata, including its
internal journal (16,384 blocks of 4 KiB, that is 64 MiB, visible in the output
of `mkfs.xfs`). `lvs` measures the container, `df` measures what is left for
your files: the two figures never match.

### Making the mount persistent, by UUID

A manual `mount` disappears on reboot. For it to come back, you need a line in
`/etc/fstab`, and that line refers to the filesystem by its **UUID**, never by
a device name.

```bash
sudo blkid /dev/vgatelier/lvarchives
```

```text
/dev/vgatelier/lvarchives: UUID="2b81f1ac-3778-4231-abe1-6c853d55ee33" BLOCK_SIZE="512" TYPE="xfs"
```

```text title="/etc/fstab"
UUID=2b81f1ac-3778-4231-abe1-6c853d55ee33  /srv/archives  xfs  defaults  0 0
```

The six columns, in order: the source (UUID), the mount point, the type, the
options, `dump` (0, a legacy feature) and the `fsck` pass at boot. The pass is
`0` for XFS, which does not use `fsck` at boot.

> **Back up before editing.** A faulty line in `/etc/fstab` can boot the machine
> into rescue mode. `sudo cp -a /etc/fstab /root/fstab.bak` costs one second.

The check is done **without rebooting**, with two complementary commands:

```bash
sudo mount -a           # actually tries to mount everything that is missing
sudo findmnt --verify   # analyses the file without mounting anything
```

`mount -a` saying nothing means success. `findmnt --verify`, for its part,
speaks even when everything is fine:

```text

0 parse errors, 0 errors, 1 warning
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload
```

This warning deserves an explanation, because it is anything but trivial:
systemd builds mount units **from** `/etc/fstab` at boot, and it works on the
copy it holds in memory. Until you reload, the mount is active but systemd
ignores the new entry. Hence the gesture, which the header of AlmaLinux's
`/etc/fstab` itself recalls in a comment:

```bash
sudo systemctl daemon-reload
sudo findmnt --verify
```

```text
Success, no errors or warnings detected
```

Now look at what a faulty line gives. A single letter changes in the UUID
(`...ee33` becomes `...ee34`), the kind of typo you do not catch on a reread:

```bash
sudo umount /srv/archives
# line modified in /etc/fstab, last character of the UUID
sudo mount -a
```

```text
mount: /srv/archives: can't find UUID=2b81f1ac-3778-4231-abe1-6c853d55ee34.
```

`findmnt --verify` is even more explicit, and does not even need to unmount
anything to detect the problem:

```text
/srv/archives
   [E] unreachable on boot required source: UUID=2b81f1ac-3778-4231-abe1-6c853d55ee34
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload

0 parse errors, 1 error, 1 warning
```

`unreachable on boot` says exactly what would happen at the next reboot. That
is why you **never** test an `fstab` entry by rebooting: you test it live, while
the machine is still repairable.

### Extending in two steps: what `lvs` sees, what `df` sees

Here is the heart of the matter, and the mistake that costs points in an exam.
The volume already contains data (a 50 MiB file has been dropped into
`/srv/archives`), and it is **not** unmounted: the whole operation is done
online.

```bash
sudo lvextend -L 768M /dev/vgatelier/lvarchives
```

```text
  Size of logical volume vgatelier/lvarchives changed from 512.00 MiB (128 extents) to 768.00 MiB (192 extents).
  Logical volume vgatelier/lvarchives successfully resized.
```

LVM reports plain success. And yet:

```bash
sudo lvs vgatelier/lvarchives
df -h /srv/archives
```

```text
  LV         VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lvarchives vgatelier -wi-ao---- 768.00m

Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  448M   85M  364M  19% /srv/archives
```

This is the intermediate state you must learn to recognise: **`lvs` says 768
MiB, `df` still says 448 MiB**. The container has grown, the filesystem knows
nothing about it. The 256 MiB added do exist, but no file will be able to
occupy them. A candidate who stops here has done half the work and believes it
is finished.

The second gesture wakes the filesystem up. For XFS, that is `xfs_growfs`:

```bash
sudo xfs_growfs /srv/archives
df -h /srv/archives
```

```text
data blocks changed from 131072 to 196608
```

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  704M   90M  615M  13% /srv/archives
```

This time `df` follows. Note that `xfs_growfs` takes **no** size argument: it
takes all the space the device offers it. You pass it the **mount point**, and
the filesystem must be **mounted**:

```bash
sudo xfs_growfs /dev/vgatelier/lvtest    # volume not mounted
```

```text
xfs_growfs: /dev/vgatelier/lvtest is not a mounted XFS filesystem
```

On a mounted volume, however, `xfs_growfs` accepts the mount point as well as
the device path: both forms worked here with `xfsprogs-6.16.0`. Still, get into
the habit of using the mount point, the form the manual documents.

### `lvextend -r`: both gestures in one command

The `-r` option (`--resizefs`) chains the extension of the volume **and** that
of the filesystem. This is the reflex to keep, precisely because it makes
forgetting impossible.

```bash
sudo lvextend -r -L +128M /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  Size of logical volume vgatelier/lvarchives changed from 768.00 MiB (192 extents) to 896.00 MiB (224 extents).
  Extending file system xfs to 896.00 MiB (939524096 bytes) on vgatelier/lvarchives...
xfs_growfs /dev/vgatelier/lvarchives
[...]
data blocks changed from 196608 to 229376
xfs_growfs done
  Extended file system xfs on vgatelier/lvarchives.
  Logical volume vgatelier/lvarchives successfully resized.
```

LVM hides nothing: it identifies the filesystem, says where it is mounted, then
**displays the command it runs for you**
(`xfs_growfs /dev/vgatelier/lvarchives`) and its result. `df` confirms:

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  832M   93M  740M  12% /srv/archives
```

Two size notations coexist, and the confusion is frequent:

| Form | Meaning | Example |
|---|---|---|
| `-L 768M` | target **absolute** size | the volume will be 768 MiB |
| `-L +128M` | **addition** to the current size | 128 MiB more than before |
| `-l +100%FREE` | in **extents**, all the free space of the VG | see below |

`-L` (uppercase) speaks in human units, `-l` (lowercase) speaks in **extents**,
the allocation unit of the volume group.

### What LVM refuses to do

Three refusals are worth more than a long speech, because they are what you
will read the day things get stuck.

**Extending beyond the free space.** The volume is 896 MiB, the VG has only 400
MiB free left, and you ask for 4 GiB:

```bash
sudo lvextend -r -L 4G /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  Insufficient free space: 800 extents needed, but only 100 available
```

The message counts in **extents**, not in gigabytes, which is disconcerting the
first time. The conversion can be read in the earlier output: `512.00 MiB (128
extents)` gives 4 MiB per extent, the default size. So 800 extents = 3.1 GiB
missing, and 100 extents = 400 MiB available, which `vgs` was already showing
as `VFree`. Nothing has been modified: the command fails before acting.

**Shrinking an XFS.** The guide says so, the machine confirms it:

```bash
sudo lvreduce -r -L 512M /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  File system size (896.00 MiB) is larger than the requested size (512.00 MiB).
  File system reduce is required and not supported (xfs).
```

`not supported (xfs)` is not a limit of LVM, but of XFS itself: this filesystem
cannot shrink, neither now nor anywhere else. The only way is to back up,
re-create smaller, restore. Practical corollary: **an XFS extension is a
one-way trip**, so do not take 100% of the VG without having thought about it.

Note too that `lvreduce` without `-r` would accept trimming the volume from
under its filesystem. That is the best way to lose data: on a reduction, the
order is the reverse of an extension (filesystem first, volume second), and
that is precisely what `-r` knows how to do correctly.

**Growing an unmounted XFS.** The operation is not impossible, but LVM asks for
permission to mount the volume along the way:

```bash
sudo lvextend -r -L +100M /dev/vgatelier/lvtest
```

```text
  File system xfs found on vgatelier/lvtest.
  File system mount is needed for extend.
Continue with xfs file system extend steps: mount, xfs_growfs? [y/n]:[n]
  File system not extended.
```

Answering `n` (the default) cancels **everything**: neither the volume nor the
filesystem has moved, and `lvs` confirms it. Above all, remember that the
question exists: in a non-interactive script, this prompt blocks or fails
silently.

### When the volume group is full: `vgextend`

`Insufficient free space` does not mean "you have to buy a bigger disk". The VG
is a pool: you add a second one to it.

```bash
sudo pvcreate /dev/vdb2
sudo vgextend vgatelier /dev/vdb2
sudo pvs
sudo vgs vgatelier
```

```text
  Physical volume "/dev/vdb2" successfully created.
  Volume group "vgatelier" successfully extended
```

```text
  PV         VG        Fmt  Attr PSize   PFree
  /dev/vdb1  vgatelier lvm2 a--   <1.27g 400.00m
  /dev/vdb2  vgatelier lvm2 a--  744.00m 744.00m

  VG        #PV #LV #SN Attr   VSize VFree
  vgatelier   2   1   0 wz--n- 1.99g <1.12g
```

The VG now counts 2 physical volumes (`#PV`) and 1.12 GiB free. That is how you
go beyond the size of a single disk, without migration and without downtime.

### `-r` picks the tool according to the filesystem

`-r` is not a synonym for `xfs_growfs`: LVM detects the filesystem type and
calls the matching tool. Let us create a second volume, in **ext4** this time:

```bash
sudo lvcreate -L 200M -n lvjournal vgatelier
sudo mkfs.ext4 -q /dev/vgatelier/lvjournal
sudo mkdir -p /srv/journal
sudo mount /dev/vgatelier/lvjournal /srv/journal
sudo lvextend -r -L +200M /dev/vgatelier/lvjournal
```

```text
  File system ext4 found on vgatelier/lvjournal mounted at /srv/journal.
  Size of logical volume vgatelier/lvjournal changed from 200.00 MiB (50 extents) to 400.00 MiB (100 extents).
  Extending file system ext4 to 400.00 MiB (419430400 bytes) on vgatelier/lvjournal...
resize2fs /dev/vgatelier/lvjournal
resize2fs 1.47.1 (20-May-2024)
Filesystem at /dev/vgatelier/lvjournal is mounted on /srv/journal; on-line resizing required
old_desc_blocks = 2, new_desc_blocks = 4
The filesystem on /dev/vgatelier/lvjournal is now 409600 (1k) blocks long.

resize2fs done
  Extended file system ext4 on vgatelier/lvjournal.
  Logical volume vgatelier/lvjournal successfully resized.
```

Compare the first line with the one from the XFS volume: `File system ext4
found` instead of `File system xfs found`, and `resize2fs` instead of
`xfs_growfs`. The command typed is strictly the same. That is the whole point
of `-r`: it spares you from knowing the tool of the filesystem in front of you.

And ext4, unlike XFS, does **shrink**:

```bash
sudo lvreduce -r -L 250M /dev/vgatelier/lvjournal
```

```text
  Rounding size to boundary between physical extents: 252.00 MiB.
  File system ext4 found on vgatelier/lvjournal mounted at /srv/journal.
  File system size (400.00 MiB) is larger than the requested size (252.00 MiB).
  File system reduce is required using resize2fs.
  File system unmount is needed for reduce.
  File system fsck will be run before reduce.
  Reducing file system ext4 to 252.00 MiB (264241152 bytes) on vgatelier/lvjournal...
unmount /srv/journal
unmount done
e2fsck /dev/vgatelier/lvjournal
/dev/vgatelier/lvjournal: 11/102400 files (0.0% non-contiguous), 32142/409600 blocks
e2fsck done
resize2fs /dev/vgatelier/lvjournal 258048k
[...]
remount /dev/vgatelier/lvjournal /srv/journal
remount done
  Reduced file system ext4 on vgatelier/lvjournal.
  Size of logical volume vgatelier/lvjournal changed from 400.00 MiB (100 extents) to 252.00 MiB (63 extents).
```

Three lessons in this single output. First, `250M` became `252.00 MiB`: a size
is always rounded up to the next multiple of an extent (4 MiB here), and LVM
says so. Second, the reduction is **not** an online operation: LVM unmounts,
checks with `e2fsck`, reduces, then remounts. Third, the order is indeed the
reverse of an extension, the filesystem shrinking before the volume.

### Taking it all: `-l +100%FREE`

When you simply want the volume to swallow everything that is left, `-l
+100%FREE` saves you from doing the arithmetic:

```bash
sudo lvextend -r -l +100%FREE /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  Size of logical volume vgatelier/lvarchives changed from 896.00 MiB (224 extents) to <1.75 GiB (447 extents).
  Extending file system xfs to <1.75 GiB (1874853888 bytes) on vgatelier/lvarchives...
xfs_growfs /dev/vgatelier/lvarchives
data blocks changed from 229376 to 457728
xfs_growfs done
  Extended file system xfs on vgatelier/lvarchives.
  Logical volume vgatelier/lvarchives successfully resized.
```

```bash
sudo vgs -o vg_name,vg_extent_size,vg_extent_count,vg_free_count vgatelier
df -h /srv/archives
```

```text
  VG        Ext   #Ext Free
  vgatelier 4.00m  510    0
```

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  1.7G  116M  1.6G   7% /srv/archives
```

`Free` drops to zero: not a single extent is left. This output also confirms
the extent size, 4 MiB, and the total of 510 extents for the two physical
volumes.

The `<` in front of `1.75 GiB` signals a rounding down in the display: the real
size is slightly below 1.75 GiB. You find it again in `pvs` (`<1.27g`) and in
`vgs`.

One last detail shows why LVM is better than a partition: the volume now spans
**both disks**, without anything showing on the filesystem side.

```bash
sudo lvs -o lv_name,seg_pe_ranges vgatelier/lvarchives
```

```text
  LV         PE Ranges
  lvarchives /dev/vdb1:0-223
  lvarchives /dev/vdb1:287-323
  lvarchives /dev/vdb2:0-185
```

Three segments, two physical volumes, one single mount point. The gap between
extents 224 and 286 of `vdb1` corresponds to the space taken by the other
logical volume.

### What does not change when the volume grows

A point that reassures when you check persistence: **the UUID of the filesystem
is not modified** by `lvextend` nor by `xfs_growfs`. After the three successive
extensions, `blkid` still returns the same value as at format time:

```text
2b81f1ac-3778-4231-abe1-6c853d55ee33
```

The `/etc/fstab` line written at the start therefore stays valid, and the data
written before the extensions is still there. In other words, growing a volume
requires **no** touch-up of `fstab`: persistence is settled once, at creation
time.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `df` has not moved after `lvextend` | the classic omission: `-r` missing, or `xfs_growfs` / `resize2fs` not run |
| `Insufficient free space: N extents needed, but only M available` | the VG is full: `vgs` to read `VFree`, then `vgextend` with a new PV |
| `File system reduce is required and not supported (xfs)` | XFS does not shrink: back up, re-create, restore |
| `xfs_growfs: … is not a mounted XFS filesystem` | XFS grows online only, mount first |
| `Continue with xfs file system extend steps: mount, xfs_growfs? [y/n]` | `lvextend -r` on an unmounted volume; in a script, mount first |
| `mount: … can't find UUID=…` on `mount -a` | wrong UUID in `/etc/fstab`; read it again with `blkid` |
| `[W] your fstab has been modified, but systemd still uses the old version` | `sudo systemctl daemon-reload` after editing `/etc/fstab` |
| `Rounding size to boundary between physical extents` | the requested size is not a multiple of the extent size; plain information |
| `lvs` not found, `command not found` | package `lvm2` missing (`sudo dnf install lvm2`) |

To undo everything and start over, unmount then remove in the reverse order of
creation: LV, VG, PV.

```bash
sudo umount /srv/archives /srv/journal
# remove the line added in /etc/fstab, then:
sudo systemctl daemon-reload
sudo lvremove -y vgatelier/lvarchives vgatelier/lvjournal
sudo vgremove vgatelier
sudo pvremove /dev/vdb1 /dev/vdb2
sudo wipefs -a /dev/vdb
sudo rmdir /srv/archives /srv/journal
```

Two gestures that get forgotten in this cleanup: removing the line from
`/etc/fstab` (leaving it there guarantees an error at the next boot) and
running `systemctl daemon-reload` again so that systemd forgets the
corresponding mount unit.
