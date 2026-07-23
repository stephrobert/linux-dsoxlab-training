# Lab — persistent mount by UUID

## Reminder

[**Persistent mounts on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/)

`blkid` and `lsblk -f` show a filesystem's UUID. An `/etc/fstab` line
(`<what> <where> <fstype> <options> <dump> <pass>`) mounts it at boot. Reference
the disk by `UUID=` — device names like `/dev/vdb` can shift across reboots.
`mount -a` mounts everything in fstab and validates your entry without rebooting.

## The course

The examples below work on `/mnt/depot`, a demonstration mount point backed by
an XFS partition: the challenge itself will ask you for another directory,
another filesystem and another disk. The point is to learn the method and
transpose it, not to copy a line.

Every output reproduced here comes from an AlmaLinux 10 with an extra blank
disk. UUIDs differ from one machine to the next: never copy the ones from the
course, always read your own.

### The demonstration setup

A one gibibyte partition is created on the extra disk, then formatted as XFS
with the label `depot`:

```bash
sudo parted -s /dev/vdb mklabel gpt mkpart depot xfs 1MiB 1025MiB
sudo partprobe /dev/vdb
sudo mkfs.xfs -L depot /dev/vdb1
```

```text
NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
vdb    252:16   0   2G  0 disk
└─vdb1 252:17   0   1G  0 part
```

This step is only there to build the setup. The real question starts now: how
to designate that partition in a durable way.

### Finding the stable identifier of the filesystem

`blkid` queries the signature written in the filesystem:

```bash
sudo blkid /dev/vdb1
```

```text
/dev/vdb1: LABEL="depot" UUID="75605d28-9cd5-4ed4-aac4-a74fbbad926f" BLOCK_SIZE="512" TYPE="xfs" PARTLABEL="depot" PARTUUID="dcb8647b-a77a-4fb8-92bf-004409becd49"
```

Four identifiers come out at once, and they do not designate the same thing:

| Field | What it identifies | Set by |
|---|---|---|
| `UUID` | the **filesystem** | `mkfs` |
| `LABEL` | the filesystem, by a name you choose | `mkfs -L` |
| `PARTUUID` | the **partition** in the partition table | `parted` |
| `PARTLABEL` | the partition, by a name you choose | `parted` |

It is the `UUID` that this lab uses. To get only it, without the rest:

```bash
sudo blkid -s UUID -o value /dev/vdb1
```

```text
75605d28-9cd5-4ed4-aac4-a74fbbad926f
```

`lsblk -f` gives the same information, as a tree, and additionally shows the
current mount point:

```bash
lsblk -f /dev/vdb
```

```text
NAME   FSTYPE FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
vdb
└─vdb1 xfs          depot 75605d28-9cd5-4ed4-aac4-a74fbbad926f
```

The `MOUNTPOINTS` column is empty: the filesystem exists, but it is mounted
nowhere. A formatted disk is not a usable disk.

### Mounting and unmounting by hand

The mount point is a directory that must exist before the mount:

```bash
sudo mkdir -p /mnt/depot
sudo mount /dev/vdb1 /mnt/depot
findmnt /mnt/depot
```

```text
TARGET     SOURCE    FSTYPE OPTIONS
/mnt/depot /dev/vdb1 xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

`findmnt` is more readable than `mount` with no argument: it only shows what you
ask for. `SOURCE` confirms the device, `FSTYPE` the type, `OPTIONS` the options
actually in effect.

`mount` also takes the UUID directly, which saves you from guessing the device
name:

```bash
sudo mount UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f /mnt/depot
```

This mount stays **temporary**: it disappears at the next boot as long as
nothing writes it into `/etc/fstab`.

To unmount, the command is spelled `umount`, without the first `n`. It fails as
long as a process is working in the directory:

```bash
sudo umount /mnt/depot
```

```text
umount: /mnt/depot: target is busy.
```

Two tools name the culprit. `fuser -vm` lists the processes, but its column
alignment is misleading, the `kernel` value spilling onto the header line:

```bash
sudo fuser -vm /mnt/depot
```

```text
kernel                     USER        PID ACCESS COMMAND
/mnt/depot:          root      mount /mnt/depot
                     16607 root      ..c.. sleep
```

`lsof` says the same thing, with no ambiguity about the PID:

```bash
sudo lsof /mnt/depot
```

```text
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
sleep   16607 root  cwd    DIR 252,17        6  128 /mnt/depot
```

The `FD` column here is `cwd`: the process holds no open file, it simply has its
**current directory** inside the mount point. That is enough to block the
unmount. Leave the directory or stop the process, then try again. Once
unmounted, `findmnt` prints nothing and returns the code `1`, which makes it a
test usable in a script.

### Making the mount persistent in /etc/fstab

`/etc/fstab` (*file systems table*) lists what the system mounts at boot. One
line, six fields separated by spaces:

```text title="/etc/fstab"
UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f  /mnt/depot  xfs  defaults,nofail  0 0
```

| Field | Value here | Role |
|---|---|---|
| what | `UUID=75605d28-...` | the filesystem to mount, by its stable identifier |
| where | `/mnt/depot` | the mount point, which must exist |
| type | `xfs` | the filesystem type, which must match the disk |
| options | `defaults,nofail` | mount options, separated by commas |
| dump | `0` | legacy backup flag, disabled |
| pass | `0` | order of `fsck` at boot |

About the pass: `1` is reserved for the root filesystem, `2` suits the other
filesystems that accept an `fsck` at boot, and `0` disables the check. XFS
checks itself at mount time and not through `fsck` at boot, hence the `0` here.

The `nofail` option is the safeguard: if the disk is missing at boot, the system
keeps booting instead of stopping in rescue mode. It is recommended on anything
that is not the system disk.

> **Back up before editing.** A faulty line in `/etc/fstab` can prevent the
> machine from booting. Make it a reflex to run
> `sudo cp -a /etc/fstab /etc/fstab.bak` before the first change: you will then
> have a way back from a rescue shell.

### Checking without rebooting: the vital reflex

Rebooting to find out whether a line is correct is the worst of tests: if it is
faulty, you learn it at the moment you no longer have a machine. Two commands
answer while the system is up.

**`mount -a`** mounts everything `fstab` declares and prints nothing when all is
well:

```bash
sudo mount -a
findmnt /mnt/depot
```

```text
TARGET     SOURCE    FSTYPE OPTIONS
/mnt/depot /dev/vdb1 xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

**`findmnt --verify`** mounts nothing: it reads `/etc/fstab` again and reports
what would go wrong at boot.

```bash
sudo findmnt --verify
```

```text
Success, no errors or warnings detected
```

Run right after the edit, it starts by reminding you of a step forgotten nine
times out of ten:

```text
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload

0 parse errors, 0 errors, 1 warning
```

systemd builds one `.mount` unit per `fstab` entry, at boot only. As long as you
have not reloaded, it works on the old version of the file. The comment at the
top of `/etc/fstab`, on AlmaLinux, already says so:

```text
# After editing this file, run 'systemctl daemon-reload' to update systemd
# units generated from this file.
```

Hence the sequence to remember after any change:

```bash
sudo systemctl daemon-reload
sudo findmnt --verify
sudo mount -a
```

Once the entry is mounted, systemd manages it as a unit in its own right:

```bash
systemctl list-units --type=mount | grep depot
```

```text
  mnt-depot.mount               loaded active mounted /mnt/depot
```

Finally, `findmnt --fstab` shows what the file **declares**, to be compared with
what is **actually** mounted:

```bash
findmnt --fstab /mnt/depot
```

```text
TARGET     SOURCE                                    FSTYPE OPTIONS
/mnt/depot UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f xfs    defaults,nofail
```

### What `mount -a` does not see

The two commands do not cover the same ground, and that is the reason to run
both. Three cases where `mount -a` answers that all is well while the line is
faulty.

**First case: the type does not match the disk.** The line announces `vfat`
while the partition is XFS, but it is already mounted. `mount -a` does not touch
an active mount point, so it says nothing:

```bash
sudo mount -a           # return code 0, no output
sudo findmnt --verify
```

```text
/mnt/depot
   [W] vfat does not match with on-disk xfs

0 parse errors, 0 errors, 1 warning
```

`findmnt --verify` compares the declared type with the signature actually
present on the disk. At boot, on a cold machine, the mount will fail:

```bash
sudo umount /mnt/depot
sudo mount -a
```

```text
mount: /mnt/depot: wrong fs type, bad option, bad superblock on /dev/vdb1, missing codepage or helper program, or other error.
       dmesg(1) may have more information after failed mount system call.
```

**Second case: a UUID that does not exist, with `nofail`.** The line points at
an identifier that exists on no disk. `nofail` does exactly its job, that is,
not blocking, and `mount -a` stays quiet:

```bash
sudo mount -a           # return code 0, no output
findmnt /mnt/depot      # return code 1, nothing is mounted
sudo findmnt --verify
```

```text
/mnt/depot
   [E] unreachable on boot required source: UUID=00000000-0000-0000-0000-000000000000

0 parse errors, 1 error, 0 warnings
```

This is the nastiest trap: the service starts, but the directory is empty.
Without `nofail`, the same line reports itself immediately:

```bash
sudo mount -a
```

```text
mount: /mnt/depot: can't find UUID=00000000-0000-0000-0000-000000000000.
```

**Third case: an incomplete line.** Here, the UUID and the mount point, with no
type and no options. Both tools reject it, but the important word is `ignored`:
the line has no effect, and the mount will never happen.

```text
findmnt: /etc/fstab: parse error at line 15 -- ignored

1 parse error, 0 errors, 0 warnings
```

Learn to read the summary of `findmnt --verify`: `parse errors` for syntax,
`errors` for what will prevent the mount, `warnings` for what deserves a second
look. Only `Success, no errors or warnings detected` allows a calm reboot.

### Why a UUID rather than a `/dev/vdX`

The usual argument is that a device name "can change". Here it is demonstrated,
without rebooting, with two image files attached as disks. Each carries a marker
that tells which one you mounted:

```bash
sudo truncate -s 400M /var/tmp/disk-a.img /var/tmp/disk-b.img
sudo mkfs.xfs -L ALPHA /var/tmp/disk-a.img
sudo mkfs.xfs -L BETA  /var/tmp/disk-b.img
sudo losetup -f --show /var/tmp/disk-a.img      # -> /dev/loop0
sudo losetup -f --show /var/tmp/disk-b.img      # -> /dev/loop1
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="ALPHA" UUID="a68aa8af-90a1-439c-8fe2-4d9eb0b0f312" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="BETA" UUID="00446362-527b-478c-9edd-06950d7a51bb" BLOCK_SIZE="512" TYPE="xfs"
```

In that order, `/dev/loop0` is ALPHA. Detach everything, then attach again in
the reverse order, exactly what a kernel does when it enumerates the disks in a
different order:

```bash
sudo losetup -d /dev/loop0 /dev/loop1
sudo losetup -f --show /var/tmp/disk-b.img      # -> /dev/loop0
sudo losetup -f --show /var/tmp/disk-a.img      # -> /dev/loop1
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="BETA" UUID="00446362-527b-478c-9edd-06950d7a51bb" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="ALPHA" UUID="a68aa8af-90a1-439c-8fe2-4d9eb0b0f312" BLOCK_SIZE="512" TYPE="xfs"
```

**`/dev/loop0` now designates the other filesystem.** The UUIDs, on the other
hand, have not moved by a single character: they are attached to the content,
not to the enumeration rank. The kernel also maintains a directory of aliases
that follows the UUIDs:

```bash
ls -l /dev/disk/by-uuid/
```

```text
lrwxrwxrwx. 1 root root 11 Jul 22 14:43 00446362-527b-478c-9edd-06950d7a51bb -> ../../loop0
lrwxrwxrwx. 1 root root 11 Jul 22 14:43 a68aa8af-90a1-439c-8fe2-4d9eb0b0f312 -> ../../loop1
```

The links were rebuilt to point at the new names. An `/etc/fstab` line written
by UUID therefore keeps finding its filesystem, while a line written by name
mounts the wrong disk, silently and without the slightest error. The
demonstration fits in two mounts of the same path, before and after the swap:

| Command | Before the swap | After the swap |
|---|---|---|
| `sudo mount /dev/loop0 /mnt/test` | `data from disk ALPHA` | `data from disk BETA` |
| `sudo mount UUID=a68aa8af-... /mnt/test` | `data from disk ALPHA` | `data from disk ALPHA` |

A mount by name changed content without warning. On a production machine, that
means backups written on the data disk, or the other way round.

### The UUID changes at every format

A UUID is stable over time, but it is **created by `mkfs`**. Reformatting builds
a new one:

```bash
sudo blkid -s UUID -o value /dev/loop1
sudo mkfs.xfs -f -L ALPHA /dev/loop1
sudo blkid -s UUID -o value /dev/loop1
```

```text
a68aa8af-90a1-439c-8fe2-4d9eb0b0f312
02aaf5ac-e778-4d2d-a99f-27942d85c63d
```

The `ALPHA` label survived, because it was given to `mkfs` again; the
identifier, though, is new. Any `/etc/fstab` line written with the old UUID now
points nowhere:

```bash
sudo mount UUID=a68aa8af-90a1-439c-8fe2-4d9eb0b0f312 /mnt/test
```

```text
mount: /mnt/test: can't find UUID=a68aa8af-90a1-439c-8fe2-4d9eb0b0f312.
```

Hence the order of operations, which is not negotiable: **format first, read the
UUID next, write the line last.** A UUID noted before a format is a stale UUID.

### Checking that the line points at the right disk

The final check fits in two commands: what `fstab` declares, and the UUID of the
filesystem actually mounted. The two must be identical.

```bash
grep depot /etc/fstab
sudo blkid -s UUID -o value $(findmnt -no SOURCE /mnt/depot)
```

```text
UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f  /mnt/depot  xfs  defaults,nofail  0 0
75605d28-9cd5-4ed4-aac4-a74fbbad926f
```

`findmnt -no SOURCE` returns the device actually mounted, `blkid` extracts its
UUID: if the value differs from the one in `fstab`, the current mount comes from
somewhere else and will not happen again at boot.

### Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `umount: target is busy` | a process has its current directory or an open file in the mount | `sudo lsof <point>` or `sudo fuser -vm <point>`, leave or stop the process |
| `mount: ... wrong fs type, bad option, bad superblock` | the declared type does not match the filesystem on the disk | read `TYPE=` in `blkid` again and fix the third field |
| `mount: ... can't find UUID=...` | wrong UUID, or disk reformatted since the line was written | read `sudo blkid -s UUID -o value <device>` again |
| `mount: ... mount point does not exist` | the target directory was not created | `sudo mkdir -p <point>` |
| `parse error at line N -- ignored` | incomplete line, a field is missing | six fields, separated by spaces |
| `[W] ... does not match with on-disk ...` | declared type wrong, but the filesystem is already mounted so `mount -a` stays quiet | fix the type before the next boot |
| `mount -a` says nothing and yet nothing is mounted | `nofail` on a line whose source cannot be found | `sudo findmnt --verify`, which prints `[E] unreachable` |
| `findmnt --verify` warns that systemd uses the old version | `fstab` changed without a reload | `sudo systemctl daemon-reload` |
| The mount disappears after a reboot | no entry in `/etc/fstab` | add the line, then `daemon-reload`, `findmnt --verify`, `mount -a` |

### Undoing everything and starting over

```bash
sudo umount /mnt/depot
sudo cp -a /etc/fstab.bak /etc/fstab     # or remove the line by hand
sudo systemctl daemon-reload
sudo findmnt --verify
sudo rmdir /mnt/depot
```

A final `sudo findmnt --verify` returning `Success, no errors or warnings
detected` is the only acceptable proof that no faulty line is left behind you.
