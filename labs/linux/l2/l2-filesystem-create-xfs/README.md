# Lab — create an XFS filesystem

## Reminder

[**XFS on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/)

`mkfs.xfs <device>` creates an XFS filesystem; `-L <label>` stamps a label
(`-f` forces over an existing signature). `blkid` and `lsblk -f` show the type,
label and UUID. A filesystem must be **mounted** on a directory to be used.

## The course

The examples below work on a test partition `/dev/vdb2`, labelled `archives`
then `depot`, mounted on `/mnt/labo-xfs`: the challenge, for its part, will ask
you for another partition, another label and another mount point. The point is
to learn the method, not to copy a line. All the output below was captured on
AlmaLinux 10, with `xfsprogs-6.16.0` and kernel `6.12.0`.

### Identify the target before any destructive command

`mkfs.xfs` asks no confirmation question: it writes. One wrong letter and the
system disk is gone. So the first move is always to find out where the root
lives, and to look at the disk tree:

```bash
findmnt -no SOURCE /
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

```text
/dev/vda4
NAME    SIZE TYPE FSTYPE  MOUNTPOINTS
sr0      46K rom  iso9660
vda      10G disk
├─vda1    1M part
├─vda2  200M part vfat    /boot/efi
├─vda3    1G part xfs     /boot
└─vda4  8.8G part xfs     /
vdb       2G disk
├─vdb1  200M part
└─vdb2  1.6G part xfs     /mnt/labo-xfs
```

Three things can be read at a glance: `/` lives on `/dev/vda4`, so **anything
starting with `vda` is off limits**; an empty `FSTYPE` column marks a partition
that carries no filesystem yet; the `MOUNTPOINTS` column shows what is already
mounted.

Get into the habit of **spelling the target out in full** in the command, rather
than taking it from a variable or from history: it is the only protection
against the wrong disk.

### Create the filesystem with mkfs.xfs

The command formats and, with `-L`, sets the label in the same move:

```bash
sudo mkfs.xfs -L archives /dev/vdb2
```

```text
meta-data=/dev/vdb2              isize=512    agcount=4, agsize=65536 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=1, rmapbt=1
         =                       reflink=1    bigtime=1 inobtcount=1 nrext64=1
         =                       exchange=0   metadir=0
data     =                       bsize=4096   blocks=262144, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1, parent=0
log      =internal log           bsize=4096   blocks=16384, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
         =                       rgcount=0    rgsize=0 extents
         =                       zoned=0      start=0 reserved=0
Discarding blocks...Done.
```

This block summarises the geometry: **4 allocation groups** (`agcount=4`, which
lets XFS write in parallel), **checksums** on the metadata (`crc=1`), a **block
size** of 4096 bytes and an **internal log** of 16384 blocks.

Two useful options before running it for real:

- **`-N`** simulates and writes nothing: the geometry is displayed, the disk is
  not touched. Checked on an unmounted partition whose label was `depot`: after
  a `mkfs.xfs -N -f -L essai /dev/vdb2`,
  `blkid -s LABEL -o value /dev/vdb2` still returned `depot`.
- **`-d su=<stripe>,sw=<disks>`** aligns the filesystem on a RAID, so that the
  writes land properly on the stripes.

### The three refusals of mkfs.xfs

These are three messages you had better have seen before.

**Too small.** `mkfs.xfs` refuses below 300 MB. On a 200 MiB partition:

```bash
sudo mkfs.xfs -L essai /dev/vdb1
```

```text
Filesystem must be larger than 300MB.
Usage: mkfs.xfs
[...]
```

**Existing signature.** Reformatting a partition that already carries a
filesystem requires an explicit agreement:

```bash
sudo mkfs.xfs -L archives /dev/vdb2
```

```text
mkfs.xfs: /dev/vdb2 appears to contain an existing filesystem (xfs).
mkfs.xfs: Use the -f option to force overwrite.
```

**Mounted filesystem.** And there, `-f` is of no use; it is the one safeguard
`mkfs.xfs` will not let you lift:

```bash
sudo mkfs.xfs -f -L autre /dev/loop0     # /dev/loop0 was mounted
```

```text
mkfs.xfs: /dev/loop0 contains a mounted filesystem
Usage: mkfs.xfs
```

The filesystem label was still `beta` after that attempt: nothing was written.
Remember the exact scope of that protection: it covers what is **mounted**, so
an unmounted partition will let itself be overwritten with no question other
than the `-f`.

The label also has a length limit, which the command help gives
(`-L label (maximum 12 characters)`) and which a test confirms:

```bash
sudo mkfs.xfs -f -L archives-projet /dev/vdb2
```

```text
Invalid value archives-projet for -L option
```

### Read the result

Three commands, three points of view.

```bash
sudo blkid /dev/vdb2
```

```text
/dev/vdb2: LABEL="archives" UUID="5fa995a5-90a2-4743-870b-7c48e31aeb18" BLOCK_SIZE="512" TYPE="xfs" PARTLABEL="essai-xfs" PARTUUID="4362f33c-8837-4458-862b-0803f020b0ba"
```

`blkid` reads the signature **on the disk**: type, label, UUID. Do not confuse
`LABEL`/`UUID` (the filesystem) with `PARTLABEL`/`PARTUUID` (the entry in the
GPT partition table): these are two different layers, and it is the first pair
that is used for mounting.

```bash
lsblk -f /dev/vdb
```

```text
NAME   FSTYPE FSVER LABEL    UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
vdb
├─vdb1
└─vdb2 xfs          archives 5fa995a5-90a2-4743-870b-7c48e31aeb18
```

`lsblk -f` gives the same information within the disk tree, which lets you see
at once what is formatted and what is not.

`xfs_info`, finally, specific to XFS, re-reads the geometry of a **mounted**
volume: same output as `mkfs.xfs`, but on demand.

```bash
sudo xfs_info /mnt/labo-xfs | head -2
```

```text
meta-data=/dev/vdb2              isize=512    agcount=7, agsize=65536 blks
         =                       sectsz=512   attr=2, projid32bit=1
```

### The label: setting it, reading it, changing it

`-L` at format time sets the label. Afterwards, `xfs_admin` reads it and changes
it, without unmounting:

```bash
sudo xfs_admin -l /dev/vdb2          # read
sudo xfs_admin -L depot /dev/vdb2    # change
```

```text
label = "archives"
label = "depot"
```

> **After a label change on a live volume, `lsblk -f` lies for a while.**
> Immediately after the `xfs_admin -L`, `blkid` did return `depot`, but
> `lsblk -f` still displayed `archives`: `lsblk` reads the udev database, which
> has not been re-probed. `sudo udevadm info --query=property --name=/dev/vdb2`
> confirmed `ID_FS_LABEL=archives`, and the `/dev/disk/by-label/archives` link
> still pointed at the partition. A `sudo udevadm trigger --settle /dev/vdb2`
> puts everything straight, and `lsblk -f` then displays `depot`.

### Mount and unmount

A filesystem only exists for the user once it is **mounted** on a directory,
which must exist beforehand:

```bash
sudo mkdir -p /mnt/labo-xfs
sudo mount /dev/vdb2 /mnt/labo-xfs
findmnt /mnt/labo-xfs
```

```text
TARGET        SOURCE    FSTYPE OPTIONS
/mnt/labo-xfs /dev/vdb2 xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

`findmnt` is more readable than `mount`: the `SOURCE` column confirms the right
device, `FSTYPE` the type actually mounted, `OPTIONS` what is active.

The mount can also designate the filesystem by its label or its UUID, which
avoids depending on the device name:

```bash
sudo mount LABEL=depot /mnt/labo-xfs
sudo mount UUID=c58910f2-1557-466f-9ee7-6e75299d7e3f /mnt/labo-xfs
```

A brand new XFS is never quite empty: on this 1.6 GiB partition, `df` already
reports 62 MB used, essentially the internal log and the metadata.

```bash
df -h /mnt/labo-xfs
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb2       1.5G   62M  1.5G   5% /mnt/labo-xfs
```

Unmounting detaches the filesystem: the data stays on the disk, but the
directory becomes an empty directory of the root again.

```bash
echo bonjour | sudo tee /mnt/labo-xfs/preuve.txt
sudo umount /mnt/labo-xfs
ls -A /mnt/labo-xfs                  # returns nothing
sudo mount LABEL=depot /mnt/labo-xfs
cat /mnt/labo-xfs/preuve.txt         # bonjour
```

If `umount` answers `target is busy`, a process is working in the mount point:
`sudo fuser -vm /mnt/labo-xfs` (or `lsof`) points it out.

### Device name or UUID

The UUID is not an affectation: a name like `/dev/vdb2` is **assigned by the
kernel in the order in which it discovers the disks**, whereas the UUID is
written **in the filesystem superblock** and travels with the data.

Here is the demonstration, done with two disk files attached to loop devices,
which makes it possible to replay an enumeration in a different order without
rebooting. Two XFS, one labelled `alpha`, the other `beta`:

```bash
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="alpha" UUID="d0299cfa-2791-459c-81db-72d952012490" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="beta" UUID="4de82a27-4521-422f-b891-6e047e7acd6c" BLOCK_SIZE="512" TYPE="xfs"
```

They are detached, then reattached in the reverse order, exactly what a server
does when two disks have been swapped or a controller changed:

```bash
sudo losetup -d /dev/loop0 ; sudo losetup -d /dev/loop1
sudo losetup -f --show /var/tmp/demo-uuid/disque-b.img    # takes loop0
sudo losetup -f --show /var/tmp/demo-uuid/disque-a.img    # takes loop1
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="beta" UUID="4de82a27-4521-422f-b891-6e047e7acd6c" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="alpha" UUID="d0299cfa-2791-459c-81db-72d952012490" BLOCK_SIZE="512" TYPE="xfs"
```

`/dev/loop0` now designates **another filesystem**. The UUIDs, for their part,
have not moved by a single character: they simply followed their data, and the
links the kernel maintains show it.

```bash
ls -l /dev/disk/by-uuid/ | grep loop
```

```text
4de82a27-4521-422f-b891-6e047e7acd6c -> ../../loop0
d0299cfa-2791-459c-81db-72d952012490 -> ../../loop1
```

An `/etc/fstab` line written with `/dev/loop0` would have mounted the wrong
volume; the same line written with `UUID=` would have mounted the right one.

> **The UUID changes at every format.** It belongs to the filesystem, not to the
> partition: `mkfs.xfs -f` makes a new one. Observed on the same partition,
> before and then after a reformat:
> `5fa995a5-90a2-4743-870b-7c48e31aeb18` became
> `c58910f2-1557-466f-9ee7-6e75299d7e3f`. Hence the order of operations: you
> format first, you re-read the UUID with `blkid`, **then** you write the
> `fstab` line. The other way round leaves a line pointing at a UUID that no
> longer exists.

### Make the mount persistent without risking the boot

`mount` does not survive a reboot. For the filesystem to come back, a line in
`/etc/fstab` is needed. Back the file up before touching it:

```bash
sudo cp -a /etc/fstab /root/fstab.orig
sudo blkid -s UUID -o value /dev/vdb2
```

The line has six fields: source, mount point, type, options, dump, check pass.

```text title="/etc/fstab"
UUID=c58910f2-1557-466f-9ee7-6e75299d7e3f  /mnt/labo-xfs  xfs  defaults,nofail  0 0
```

- **Source**: `UUID=`, for the reason demonstrated above. `LABEL=` is acceptable
  too, provided the label is unique on the machine.
- **Type**: `xfs`.
- **Options**: `defaults`, plus `nofail` on any volume that is not essential to
  the boot, so that its absence does not block the boot.
- **Pass**: `0` for XFS, which is not checked at boot. The three original lines
  of this machine's `/etc/fstab`, all XFS, do carry `0`.

**Never test by rebooting.** Two commands say the same thing without risk, and
they complement each other.

```bash
sudo systemctl daemon-reload   # otherwise findmnt --verify asks for it
sudo mount -a
sudo findmnt --verify
```

On the correct line, `mount -a` says nothing at all and returns 0, and the check
is clean:

```text
Success, no errors or warnings detected
```

Here now is the same line with **a single wrong character in the UUID**:

```text title="/etc/fstab (faulty)"
UUID=c58910f2-1557-466f-9ee7-6e75299d7e39  /mnt/labo-xfs  ext4  defaults  0 0
```

```bash
sudo findmnt --verify
```

```text
/mnt/labo-xfs
   [E] unreachable on boot required source: UUID=c58910f2-1557-466f-9ee7-6e75299d7e39

0 parse errors, 1 error, 0 warnings
```

```bash
sudo mount -a
```

```text
mount: /mnt/labo-xfs: can't find UUID=c58910f2-1557-466f-9ee7-6e75299d7e39.
```

This is exactly the message that, at boot, sends the machine into *emergency
mode*. `findmnt --verify` says it cold, with exit code 1 and the mention
`required source`: without `nofail`, this line is **blocking**.

Third case, more insidious, because the mount is possible but badly declared:
the right UUID, but the type `ext4` on an XFS filesystem.

```text
/mnt/labo-xfs
   [W] ext4 does not match with on-disk xfs

0 parse errors, 0 errors, 1 warning
```

```bash
sudo mount -a
```

```text
mount: /mnt/labo-xfs: wrong fs type, bad option, bad superblock on /dev/vdb2, missing codepage or helper program, or other error.
       dmesg(1) may have more information after failed mount system call.
```

Remember the division of roles: `findmnt --verify` **re-reads the file** and
reports what will not be able to work, including what `mount -a` would not
distinguish from a generic error; `mount -a` **actually attempts** the mounts
and proves that the line works. Do both before closing the file.

### Grow it live, and why you do not shrink it

This is XFS's great strength in production. The operation always happens in two
steps, **container first, filesystem second**: grow the container (the partition
with `parted`, the logical volume with `lvextend`), then extend the filesystem.
As long as the second step has not happened, nothing changes:

```bash
sudo parted /dev/vdb resizepart 2 1801MiB     # 1 GiB -> 1.6 GiB
sudo partprobe /dev/vdb
lsblk /dev/vdb ; df -h /mnt/labo-xfs
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
vdb    252:16   0    2G  0 disk
├─vdb1 252:17   0  200M  0 part
└─vdb2 252:18   0  1.6G  0 part /mnt/labo-xfs
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb2       960M   51M  910M   6% /mnt/labo-xfs
```

The partition is indeed 1.6 GiB, the filesystem stayed at 960 MB. It is
`xfs_growfs` that closes the gap, **without unmounting**, and without your
having to give a size: XFS takes all the room in its container.

```bash
sudo xfs_growfs /mnt/labo-xfs
```

```text
[...]
data blocks changed from 262144 to 409600
```

```bash
df -h /mnt/labo-xfs
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb2       1.5G   62M  1.5G   5% /mnt/labo-xfs
```

Incidentally, `xfs_info` then showed `agcount=7` where the format had created 4
allocation groups: growing adds some, it does not resize the existing ones.

> **Beware of `parted -s` on a mounted partition.** In script mode, the command
> displayed `Warning: Partition /dev/vdb2 is being used. Are you sure you want
> to continue?` and **did nothing**: the table stayed unchanged. You have to
> answer `Yes` explicitly for the resize to happen. A script that does not check
> the result will believe it grew the partition.

In the other direction, there is nothing. No `xfs_shrink` exists:

```bash
ls /usr/sbin/xfs_* | tr '\n' ' '
```

```text
/usr/sbin/xfs_admin /usr/sbin/xfs_bmap /usr/sbin/xfs_copy /usr/sbin/xfs_db /usr/sbin/xfs_estimate /usr/sbin/xfs_freeze /usr/sbin/xfs_fsr /usr/sbin/xfs_growfs /usr/sbin/xfs_info /usr/sbin/xfs_io /usr/sbin/xfs_logprint /usr/sbin/xfs_mdrestore /usr/sbin/xfs_mkfile /usr/sbin/xfs_ncheck /usr/sbin/xfs_property /usr/sbin/xfs_protofile /usr/sbin/xfs_quota /usr/sbin/xfs_repair /usr/sbin/xfs_rtcp /usr/sbin/xfs_spaceman
```

And asking `xfs_growfs` for a size smaller than the current one fails:

```bash
sudo xfs_growfs -D 262144 /mnt/labo-xfs
```

```text
[EXPERIMENTAL] try to shrink unused space 262144, old size is 409600
xfs_growfs: XFS_IOC_FSGROWFSDATA xfsctl failed: Invalid argument
```

The word `[EXPERIMENTAL]` shows that a shrink path exists in the code, but it
failed here: **do not count on it**. In practice, shrinking an XFS means backing
up, recreating smaller, restoring. So plan for the margin at creation time, or
put the filesystem on an LVM logical volume, where `lvextend -r` chains the
volume extension and `xfs_growfs` in a single command.

### Check and repair

XFS is not checked at boot (hence the `0` in the last column of `fstab`). The
dedicated tool is `xfs_repair`, and it requires an **unmounted** filesystem:

```bash
sudo xfs_repair -n /dev/vdb2      # -n: diagnosis only, writes nothing
```

```text
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
[...]
No modify flag set, skipping phase 5
Phase 6 - check inode connectivity...
[...]
No modify flag set, skipping filesystem flush and exiting.
```

On a mounted filesystem, it refuses flatly:

```text
xfs_repair: /dev/vdb2 contains a mounted and writable filesystem

fatal error -- couldn't initialize XFS library
```

And beware of the argument: `xfs_repair` expects a **device**, not a mount
point. Given `/mnt/labo-xfs`, it answers `xfs_repair: can't determine device
size`, a message that hardly helps in understanding the error.

Without `-n`, `xfs_repair` fixes things. The `-L` option wipes the log when it
is corrupted to the point of preventing the mount: it is a **last resort**, it
can lose recent writes.

### Useful mount options

| Option | Effect | For |
|---|---|---|
| `noatime` | does not write the access date | heavily used volumes |
| `nodev,nosuid,noexec` | hardens the mount | `/tmp`, external disks |
| `nofail` | the absence of the volume does not block the boot | any non-essential volume |
| `uquota` / `gquota` / `pquota` | enables XFS quotas | shared volumes |

XFS quotas are native: once the volume is mounted with `uquota`, they are driven
with `xfs_quota` (`xfs_quota -x -c 'report -h' <mount point>` for the state,
`-c 'limit bsoft=... bhard=... <user>'` to set a limit).

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Filesystem must be larger than 300MB.` | volume too small for XFS |
| `appears to contain an existing filesystem` | signature present; check the target, then `-f` if certain |
| `contains a mounted filesystem` | unmount first; `-f` does not lift this protection |
| `Invalid value ... for -L option` | label longer than 12 characters |
| `lsblk -f` shows the old label | udev database not re-probed: `sudo udevadm trigger --settle <dev>` |
| `mount: can't find UUID=...` | wrong UUID, or filesystem reformatted since the `fstab` was written |
| `wrong fs type, bad option, bad superblock` | type declared in `fstab` different from the real type |
| `umount: target is busy` | a process is occupying the mount point: `fuser -vm <mp>` |
| `xfs_repair: contains a mounted ... filesystem` | unmount before repairing |
| Impossible to shrink the volume | XFS does not shrink: back up, recreate, restore |

### Undo everything

```bash
sudo umount /mnt/labo-xfs
sudo cp -a /root/fstab.orig /etc/fstab     # restore the backup
sudo systemctl daemon-reload
sudo findmnt --verify                      # must go back to green
sudo rmdir /mnt/labo-xfs
```

The `daemon-reload` is not decorative: without it, systemd keeps using the old
version of the file, and `findmnt --verify` reports it with
`[W] your fstab has been modified, but systemd still uses the old version`.
