# Lab — GPT partitioning with parted

## Reminder

[**Partitions on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/)

A brand-new disk has no partition table: you must start by laying one down.
`parted -s <disk> mklabel gpt` writes a GPT table, `mkpart` cuts a partition in
it between two offsets. GPT lifts the limits of the old MBR. After editing, the
kernel must re-read the table (`partprobe <disk>`) for the devices `<disk>1`,
`<disk>2` to appear; `lsblk` shows them.

## The course

The examples below cut demonstration partitions named `demo1` and `demo2`: the
challenge will ask you for different ones, different sizes, at different
offsets. Learn the method, it transposes; do not copy the numbers.

All the output on this page was produced on an **AlmaLinux 10** VM (`parted`
3.6, `util-linux` 2.40.2), on a 2 GiB spare disk.

### Spotting the disk, and not getting the letter wrong

This is the only gesture in this lab that does not forgive. Before any
destructive command, look at which disk carries the system:

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS
```

```text
NAME    SIZE TYPE MOUNTPOINTS
vda      10G disk
├─vda1    1M part
├─vda2  200M part /boot/efi
├─vda3    1G part /boot
└─vda4  8.8G part /
vdb       2G disk
```

`vda` carries `/`, `/boot` and `/boot/efi`: leave it alone. `vdb` has no
partition and no mount point, it is the spare disk. On your VM the letter may
differ: **check, do not assume**, and name the target explicitly in every
command.

A blank disk is recognised by two outputs. `blkid` returns nothing and exits
with an error, `parted` announces that it does not recognise a label:

```bash
sudo blkid /dev/vdb          # no output, exit code 2
sudo parted -s /dev/vdb print
```

```text
Error: /dev/vdb: unrecognised disk label
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 2147MB
Sector size (logical/physical): 512B/512B
Partition Table: unknown
```

The **`Partition Table:`** line is the one to watch throughout this lab:
`unknown`, then `msdos` or `gpt`.

### MBR or GPT: the two limits, demonstrated

The guide sums the choice up like this:

| Characteristic | MBR (`msdos`) | GPT |
|---|---|---|
| Primary partitions | **4** maximum | **128** in common use |
| Disk size handled | **2 TiB** | far beyond |
| Firmware | legacy BIOS | **UEFI** (and BIOS) |
| Backup table | no | **yes** |

These two limits are not theoretical, you can touch them. In `msdos`, the fifth
primary partition is refused:

```bash
sudo parted -s /dev/vdb mklabel msdos
sudo parted -s /dev/vdb mkpart primary 1MiB   101MiB
sudo parted -s /dev/vdb mkpart primary 101MiB 201MiB
sudo parted -s /dev/vdb mkpart primary 201MiB 301MiB
sudo parted -s /dev/vdb mkpart primary 301MiB 401MiB
sudo parted -s /dev/vdb mkpart primary 401MiB 501MiB    # the fifth
```

```text
Error: Can't create any more partitions.
```

The 2 TiB limit shows up on a 3 TiB sparse file (it takes up nothing on the
disk as long as you do not write to it) exposed as a block device:

```bash
sudo truncate -s 3T /var/tmp/gros.img     # "du" returns 0: nothing allocated
LOOP=$(sudo losetup --find --show /var/tmp/gros.img)
sudo parted -s $LOOP mklabel msdos
sudo parted -s $LOOP mkpart primary 1MiB 100%
```

```text
Error: partition length of 6442448896 sectors exceeds the
msdos-partition-table-imposed maximum of 4294967295
```

The message gives the exact figure: 4,294,967,295 sectors of 512 bytes, that is
exactly 2 TiB. The same disk in GPT accepts the whole partition:

```bash
sudo parted -s $LOOP mklabel gpt
sudo parted -s $LOOP mkpart data 1MiB 100%
sudo parted -s $LOOP print
```

```text
Partition Table: gpt

Number  Start   End     Size    File system  Name  Flags
 1      1049kB  3299GB  3299GB               data
```

Do not leave the test setup lying around: `sudo losetup -d $LOOP` then
`sudo rm -f /var/tmp/gros.img`.

### Laying the table down: `mklabel` erases everything, without a word

Back to the spare disk, which at this stage carried four `msdos` partitions.
One single command, no warning, no question:

```bash
sudo parted -s /dev/vdb mklabel gpt      # exit code 0
sudo parted -s /dev/vdb print
```

```text
Partition Table: gpt

Number  Start  End  Size  File system  Name  Flags
```

The four partitions are gone. `mklabel` does not convert a table, it writes a
brand-new one over it: **everything described in it is lost**.

> The `-s` (script) mode suppresses confirmations, which is what makes it usable
> in a playbook. It does not say "yes" to everything for all that: on an
> operation `parted` deems dangerous, it answers "no" and gives up (see the
> troubleshooting below). On `mklabel`, there is simply no question asked.

### Cutting with `mkpart`

`mkpart` takes a name, optionally a filesystem type (a mere hint, no formatting
takes place), then the start and end boundaries:

```bash
sudo parted -s /dev/vdb mkpart demo1 1MiB 257MiB     # 256 MiB
sudo parted -s /dev/vdb mkpart demo2 257MiB 897MiB   # 640 MiB
```

The size of a partition is the **difference** between the two boundaries, not
the second boundary: `1MiB 257MiB` gives 256 MiB, and the next one starts
exactly where the previous one stops so as not to leave a gap. The first offset
is `1MiB` and not `0`: this 1 MiB alignment is the convention that guarantees
good performance, and `parted` applies it automatically.

`parted print` displays in decimal megabytes, `lsblk` in rounded binary units:
268 MB and 256 MiB designate the same thing.

```bash
sudo parted -s /dev/vdb print
```

```text
Number  Start   End    Size   File system  Name   Flags
 1      1049kB  269MB  268MB               demo1
 2      269MB   941MB  671MB               demo2
```

The empty **File system** column is normal: the partitions exist, they are not
formatted. That is the next step, with `mkfs.ext4` or `mkfs.xfs`.

### The kernel, `/dev`, `partprobe` and `udevadm settle`

Three views coexist, and they do not update together. Just after the two
`mkpart` above:

```bash
ls -l /dev/vdb*                 # brw-rw----. 1 root disk 252, 16 /dev/vdb
grep vdb /proc/partitions
```

```text
 252       16    2097152 vdb
 252       17     262144 vdb1
 252       18     655360 vdb2
```

The kernel already knows the partitions (`/proc/partitions`, and `lsblk` which
reads sysfs), but the files `/dev/vdb1` and `/dev/vdb2` do not exist yet: it is
**udev** that creates them, asynchronously. Any command targeting that path
(`mkfs`, `pvcreate`, `mount`) fails as long as it does not exist.

The window is short and irregular. The same `mkpart` immediately followed by a
`test -e`, run three times in a row, gave:

```text
run 1: node ABSENT immediatement
run 2: node present immediatement
run 3: node present immediatement
```

Hence the reflex, in a script as well as by hand, before moving on to a `mkfs`
or a `pvcreate`:

```bash
sudo partprobe /dev/vdb        # ask the kernel to re-read the table
sudo udevadm settle            # wait for udev to finish populating /dev
```

The two do not do the same thing: `partprobe` addresses the **kernel**,
`udevadm settle` waits for **udev**. It is the second one that solves the
problem above; the first is useful when the kernel itself has not picked up the
new table.

### The partition type: `parted` flag or `sgdisk` code

The type says what the partition is intended for (LVM, RAID, swap, EFI). It
changes nothing in the content, but `pvcreate`, `mdadm` and the installers rely
on it. Two routes lead to the same byte on the disk. Through `parted`, it is a
flag:

```bash
sudo parted -s /dev/vdb set 1 lvm on
```

Through `sgdisk`, it is a four-hex-digit code (`8300` Linux filesystem, `8e00`
LVM, `fd00` RAID, `ef00` EFI):

```bash
sudo sgdisk -t 2:8e00 /dev/vdb
```

`sgdisk -p` shows the result of both, in the `Code` column:

```text
Number  Start (sector)    End (sector)  Size       Code  Name
   1            2048          526335   256.0 MiB   8E00  demo1
   2          526336         1837055   640.0 MiB   8E00  demo2
```

And `parted print` displays the same state as an `lvm` flag on both partitions.
The four-digit code is a `sgdisk` shorthand; what is actually written in the
table is a 128-bit GUID, which `sgdisk -i` reveals:

```bash
sudo sgdisk -i 1 /dev/vdb
```

```text
Partition GUID code: E6D6D379-F507-44C2-A23C-238F2A3DF928 (Linux LVM)
Partition unique GUID: 8679E621-F137-4C28-87D7-31EB3BC8B89B
First sector: 2048 (at 1024.0 KiB)
Partition size: 524288 sectors (256.0 MiB)
Partition name: 'demo1'
```

Two different GUIDs: the one of the **type** is the same on every LVM partition
in the world, the one of the partition is unique and serves as the `PARTUUID`
in `/etc/fstab`.

> `sgdisk` and `gdisk` are **not installed** on AlmaLinux 10, and the `gdisk`
> package is not in the base repositories: it comes from EPEL
> (`sudo dnf install epel-release && sudo dnf install gdisk`). `parted` and
> `fdisk`, on the other hand, are there by default. Do not count on `sgdisk` on
> a machine you do not control.

### Backing up the table, troubleshooting, making the disk bare

A GPT table fits in a few tens of kilobytes and is backed up with one command.
That is more useful than a long speech about caution:

```bash
sudo sgdisk --backup=/root/vdb-gpt.bak /dev/vdb   # 17920 bytes here
sudo sgdisk --zap-all /dev/vdb                    # everything is destroyed
sudo sgdisk --load-backup=/root/vdb-gpt.bak /dev/vdb
sudo partprobe /dev/vdb && sudo udevadm settle
```

After restoring, `parted print` finds the partitions, their names and their
flags identical. Careful: it is the **table** that is backed up, not the data;
on the other hand, restoring the table is enough to get back data that became
invisible after a bad `mklabel`.

GPT further carries a **backup copy** at the end of the disk. By overwriting
the primary header (sectors 1 to 33) and re-reading, `sgdisk` switches over on
its own:

```text
Caution: invalid main GPT header, but valid backup; regenerating main header
from backup!
Main header: ERROR
Backup header: OK
```

This is the redundancy announced in the MBR/GPT table, seen for real. `sgdisk
--verify /dev/vdb` diagnoses, and a `--load-backup` repairs ("No problems
found").

| Symptom | Likely cause |
|---|---|
| `Error: unrecognised disk label` | no table on the disk: start with `mklabel` |
| `Error: Can't create any more partitions.` | `msdos` table and 4 primary partitions: redo the table in `gpt` |
| `/dev/<disk>N` not found right after `mkpart` | udev has not finished populating `/dev`: `sudo udevadm settle` |
| `Warning: Partition /dev/... is being used.` and exit code 1 | a partition of the disk is mounted; `parted -s` refuses and gives up. Unmount first |
| A brand-new partition shows an `FSTYPE` you did not create | signature of an old filesystem, left in place; `wipefs -a` on the partition |

That last case deserves a word: `wipefs -a` on the **disk** only erases the
signatures located at the beginning of the disk. An XFS or ext4 signature
buried further away survives, and resurfaces as soon as a new partition covers
its position. To make a disk really bare, you therefore need both passes,
partitions first:

```bash
for p in /dev/vdb[0-9]*; do sudo wipefs -a "$p"; done
sudo wipefs -a /dev/vdb
```

```text
/dev/vdb2: 4 bytes were erased at offset 0x00000000 (xfs): 58 46 53 42
/dev/vdb: 8 bytes were erased at offset 0x00000200 (gpt): 45 46 49 20 50 41 52 54
/dev/vdb: 8 bytes were erased at offset 0x7ffffe00 (gpt): 45 46 49 20 50 41 52 54
/dev/vdb: 2 bytes were erased at offset 0x000001fe (PMBR): 55 aa
/dev/vdb: calling ioctl to re-read partition table: Success
```

`wipefs` does remove **both** GPT copies (start and end of disk) as well as the
protective MBR. The proof of the return to zero:

```bash
sudo lsblk -f /dev/vdb
```

```text
NAME FSTYPE FSVER LABEL UUID FSAVAIL FSUSE% MOUNTPOINTS
vdb
```

No partition left, no signature left: the disk is ready to be repartitioned.
