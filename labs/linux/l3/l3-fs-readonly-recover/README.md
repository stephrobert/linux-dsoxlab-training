# Lab — recover a read-only filesystem

## Reminder

[**Read-only filesystem recovery on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/)

`findmnt <mnt>` shows the live options of a mount (`ro` vs `rw`).
`mount -o remount,rw <mnt>` switches it without unmounting. A bad option in
`/etc/fstab` makes `mount -a` fail — and a real boot would drop to emergency mode —
so always test fstab with `mount -a` after editing it.

## The course

The examples below work on a scratch disk, `/dev/vdb`, split in two:
`/dev/vdb1` in ext4 mounted on `/mnt/depot`, `/dev/vdb2` in xfs mounted on
`/mnt/archive`. The challenge will give you another mount, elsewhere, with
another failure. The goal is to learn the method.

> **Never reproduce these operations on `/`.** A scratch filesystem can be broken
> and repaired without consequence; the root filesystem cannot. Check with
> `lsblk` which device you are on before every destructive command.

### Observing: the message, the options, the log

Three sources, and they do not say the same thing. Start with the message the
application receives:

```bash
sudo touch /mnt/depot/essai
```

```text
touch: cannot touch '/mnt/depot/essai': Read-only file system
```

Then the options actually active on the mount:

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS /mnt/depot
```

```text
TARGET     SOURCE    FSTYPE OPTIONS
/mnt/depot /dev/vdb1 ext4   ro,relatime,seclabel
```

To sweep the whole machine in one go, `findmnt -O ro -o TARGET,SOURCE,FSTYPE`
lists the mounts carrying the `ro` option (the `tmpfs` mounts of
`/run/credentials` always show up, they are intentional read-only mounts).

> **Beware of `grep` on the output of `mount`.** The often-quoted pattern,
> `mount | grep ' ro,'`, brings back nothing: `mount` writes the options between
> parentheses, so the line is `/dev/vdb1 on /mnt/depot type ext4 (ro,relatime,seclabel)`.
> You need `mount | grep '(ro,'`, or better `findmnt -O ro`, which queries the
> mount table rather than text.

Finally, the kernel log, the only one that says **why**:

```bash
sudo dmesg | grep -iE 'EXT4-fs|XFS|read-only'
```

```text
[ 2604.689943] EXT4-fs (vdb1): mounted filesystem 5a73ff73-[...] r/w with ordered data mode.
[ 2619.711686] EXT4-fs (vdb1): re-mounted 5a73ff73-[...] ro.
```

Read that last line carefully: `re-mounted ... ro.` is the trace of an
administrator action, not of an error. The kernel says it was asked for a
read-only remount. Remember that wording, it contrasts with the next one.

### Intended or suffered: two failures that are not repaired the same way

The error message points at the cause, and that is the heart of the diagnosis:

| Message obtained | Code | What it means |
|---|---|---|
| `Read-only file system` | `EROFS` | The mount is read-only **on purpose** |
| `Input/output error` | `EIO` | The **device gave up**, the filesystem protected itself |

To see the second case without breaking a real disk, insert a device-mapper
layer between the filesystem and the partition, then replace its table with the
`error` target, which makes every I/O fail:

```bash
sudo dmsetup suspend --nolockfs --noflush depot_fragile
echo "0 2097152 error" | sudo dmsetup reload depot_fragile
sudo dmsetup resume depot_fragile
sudo touch /mnt/depot/apres-panne
```

```text
touch: cannot touch '/mnt/depot/apres-panne': Input/output error
```

And the log, a few seconds later:

```text
Buffer I/O error on dev dm-0, logical block 0, lost sync page write
EXT4-fs (dm-0): I/O error while writing superblock
Aborting journal on device dm-0-8.
EXT4-fs error (device dm-0) in __ext4_new_inode:1093: IO failure
EXT4-fs (dm-0): Remounting filesystem read-only
```

Five lines, the whole diagnosis: write error, superblock impossible to update,
journal aborted, read-only remount decided by the kernel. Nothing to do with the
`re-mounted ... ro.` of the previous section.

A write straight afterwards returns `Read-only file system` and no longer
`Input/output error`: once the switch is done, the filesystem refuses cleanly
instead of failing on the disk.

### ext4: the `errors=remount-ro` protection is not always active

It is the `errors=` option that decides what ext4 does when facing an
inconsistency: continue, remount read-only, or panic. Its default value is
written **in the superblock**:

```bash
sudo tune2fs -l /dev/vdb1 | grep -iE 'errors behavior|filesystem state'
```

```text
Filesystem state:         clean
Errors behavior:          Continue
```

**`Continue` on a filesystem freshly created by `mkfs.ext4`**: the protection is
therefore not there by default on AlmaLinux 10, contrary to what is often read.
You set it on the superblock, once and for all:

```bash
sudo tune2fs -e remount-ro /dev/vdb1
sudo tune2fs -l /dev/vdb1 | grep -i 'errors behavior'
```

```text
Setting error behavior to 2
Errors behavior:          Remount read-only
```

It can also be given at mount time or in `/etc/fstab` (`errors=remount-ro`).
Useful detail: `findmnt` only shows the option when it **differs** from the
superblock. Mounted with `errors=continue` while the superblock says
`remount-ro`, you read `rw,relatime,seclabel,errors=continue`; otherwise,
nothing.

### xfs does not behave like ext4

On RHEL and its derivatives, the root filesystem is xfs by default. And **none
of the above applies to it**. First, the option does not exist:

```bash
sudo mount -o remount,errors=remount-ro /mnt/archive
```

```text
mount: /mnt/archive: fsconfig system call failed: xfs: Unknown parameter 'errors'.
```

Then the tools differ. `tune2fs` is an ext tool, it refuses the device
(`Bad magic number in super-block`). And `fsck` on xfs checks nothing:

```bash
sudo fsck -n /dev/vda4        # the root filesystem, in xfs
```

```text
fsck from util-linux 2.40.2
If you wish to check the consistency of an XFS filesystem or
repair a damaged filesystem, see xfs_repair(8).
```

Finally, the failure does not show up in the same way. With the same `error`
target under the xfs mount:

```text
XFS (dm-1): log I/O error -5
XFS (dm-1): Filesystem has been shut down due to log error (0x2).
XFS (dm-1): Please unmount the filesystem and rectify the problem(s).
```

xfs does not remount read-only: it **shuts down**. And `findmnt -no OPTIONS
/mnt/archive` keeps showing `rw,relatime,seclabel,attr2,...` without the
slightest clue, while both reads and writes return `Input/output error`. On
ext4, the kernel at least adds an `emergency_ro` marker in the options; on xfs,
the mount table says nothing.

### Repairing: unmount, check, remount

You **never** repair a mounted filesystem. This is not a matter of style, the
tools refuse:

```bash
sudo e2fsck -f /dev/vdb1      # mounted partition
```

```text
e2fsck 1.47.1 (20-May-2024)
/dev/vdb1 is mounted.
e2fsck: Cannot continue, aborting.
```

```bash
sudo xfs_repair -n /dev/vdb2  # mounted partition
```

```text
xfs_repair: /dev/vdb2 contains a mounted and writable filesystem
fatal error -- couldn't initialize XFS library
```

`e2fsck -n` does agree to run on an active mount, but it warns that its verdict
is worth nothing: `Warning! /dev/vdb1 is mounted.` then
`Warning: skipping journal recovery because doing a read-only filesystem check.`
A journal that has not been replayed means an image of the disk that is not the
real state.

So: unmount first. If `umount` answers `target is busy`, look for who is holding
the mount with `lsof +f -- /mnt/depot`, stop the process, and keep `umount -l`
for the last resort only. On the root filesystem, unmounting is impossible: you
have to reboot into a rescue system.

Offline check, then repair:

```bash
sudo e2fsck -n -f /dev/vdb1 ; echo "exit=$?"
```

```text
Pass 5: Checking group summary information
Inode bitmap differences:  +12
Fix? no
[...]
depot: ********** WARNING: Filesystem still has errors **********
exit=4
```

```bash
sudo e2fsck -f -y /dev/vdb1 ; echo "exit=$?"
```

```text
Inode bitmap differences:  +12
Fix? yes
depot: ***** FILE SYSTEM WAS MODIFIED *****
exit=1
```

`-f` forces the check even if the filesystem believes it is clean, `-y` answers
yes to everything, `-n` answers no to everything and writes nothing. The exit
codes matter: **0** nothing to fix, **1** errors were **fixed** (that is a
success), **4 and above** errors **not fixed**, and that is when to worry.

On the xfs side, `xfs_repair -n` does the same reporting job, and `xfs_repair`
without an option repairs. One particular case to know, described in
`man 8 xfs_repair`: if the journal is dirty, `xfs_repair` **exits with code 2 and
does nothing**, because only the kernel knows how to replay an xfs journal. The
manual gives the procedure: mount then immediately unmount the filesystem to let
the kernel replay it, and only resort to `xfs_repair -L`, which wipes the
journal, as a last resort, accepting the loss of the metadata being written.

### The trap: a successful remount is not a repair

This is what costs you the lab, and the exam. On the xfs mount shut down by the
kernel:

```bash
sudo mount -o remount,rw /mnt/archive ; echo "exit=$?"
sudo touch /mnt/archive/preuve
```

```text
exit=0
touch: cannot touch '/mnt/archive/preuve': Input/output error
```

**The remount succeeded. Nothing is repaired.** And even after making the device
perfectly healthy again, the write still fails: the filesystem stays shut down
until it is unmounted.

On ext4 in the same state, the remount does not even succeed:

```text
mount: /mnt/depot: fsconfig system call failed: ext4: Unknown parameter 'emergency_ro'.
```

Two lessons. The first: never conclude anything from the return code of a
`mount -o remount,rw`. The only proof that writing is back is **actually writing
a file**. The second: the only proof that the filesystem is healthy is an offline
check, `e2fsck -n -f` or `xfs_repair -n`, which changes nothing and gives you an
exit code.

And look for the cause. A mount that goes back to read-only after a remount has
a real problem: read `dmesg` again for the `Buffer I/O error on dev` lines, which
point at the faulty device. On physical hardware, `smartctl -H /dev/sdX` gives
the health status of the disk; on a VM, do not count on it, `smartctl -H
/dev/vdb` answers `Unable to detect device type` on a virtio disk.

### Never block the boot: `nofail`, `mount -a`, `findmnt --verify`

A faulty entry in `/etc/fstab` is not visible right away: it becomes visible at
reboot, when the machine drops to emergency mode. Two safeguards.

`findmnt --verify` re-reads `/etc/fstab` and reports what will not pass:

```bash
sudo findmnt --verify
```

```text
/mnt/depot
   [E] unreachable on boot required source: UUID=00000000-1111-2222-3333-444444444444
0 parse errors, 1 error, 1 warning
```

`mount -a` mounts everything declared by `fstab` and fails if one entry fails:

```text
mount: /mnt/depot: can't find UUID=00000000-1111-2222-3333-444444444444.
exit=32
```

The `nofail` option tells the system to carry on if the device is absent. With
it, on the **same** broken entry, `mount -a` returns 0:

```text
exit=0
```

Mind what that means: `nofail` fixes nothing, it only keeps the boot from
blocking. `findmnt --verify` still shows
`[E] unreachable on boot required source`. The two commands are complementary,
one tests the mount, the other re-reads the declaration.

The safe sequence, when touching `fstab`: back up the file
(`cp -a /etc/fstab /root/fstab.bak`), add `nofail` on any entry you are not sure
about, then check with `sudo findmnt --verify` **and** `sudo mount -a` before any
reboot.

> **After editing `fstab`, `findmnt --verify` reminds you to run
> `systemctl daemon-reload`**: systemd generates mount units from that file and
> is still working on the old version until it has been reloaded.
