# Lab — Build a software RAID 1 with mdadm

## Reminder

[**Software RAID with mdadm**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/)

RAID 1 mirrors data across several disks: the array survives the loss of one
disk. A spare can rebuild automatically. The array must be declared in
`mdadm.conf` (and the initramfs) to reassemble at boot.

## The course

The examples below build a mirror named `/dev/md10` on the partitions of a
demonstration disk, mounted on `/srv/miroir-demo`: the challenge will ask you for
another array, on other devices and another mount point. The point is to learn
the method, not to copy a line. Every output below was produced on an AlmaLinux
10.2 VM (`mdadm` 4.4).

### Where the machine stands

Three questions before starting: is the tool there, does an array already exist,
and which disks are free.

```bash
rpm -q mdadm            # on AlmaLinux 10, the package is not installed by default
cat /proc/mdstat        # the list of the kernel's arrays
lsblk                   # which disks carry no mount point
```

```text
package mdadm is not installed

Personalities :
unused devices: <none>

vdb    252:16   0    2G  0 disk
```

An empty `Personalities :` and `unused devices: <none>` mean that no array is
assembled, and that the kernel has not even loaded a RAID module yet. Install the
tool with `sudo dnf install -y mdadm`: the package enables the `mdmonitor`
monitoring service along the way.

> **Never work blind on a disk.** Check with `lsblk` that the one you are aiming
> at carries no mount point. Here, `/dev/vda` is the system disk (it carries `/`,
> `/boot` and `/boot/efi`): do not touch it.

### Preparing the devices

A RAID array needs at least **two devices of the same size**, whole disks or
partitions. The demonstration disk is cut into four 500 MiB partitions: two for
the mirror, one spare, one to play the replacement disk.

```bash
sudo parted -s /dev/vdb mklabel gpt
sudo parted -s /dev/vdb mkpart mir1 1MiB 500MiB
sudo parted -s /dev/vdb set 1 raid on
# … same for mir2 (501-1000), mir3 (1001-1500), mir4 (1501-2000)
sudo partprobe /dev/vdb
```

```text
Number  Start   End     Size   File system  Name  Flags
 1      1049kB  524MB   523MB               mir1  raid
 2      525MB   1049MB  523MB               mir2  raid
 3      1050MB  1573MB  523MB               mir3  raid
 4      1574MB  2097MB  523MB               mir4  raid
```

The `raid` flag is a partition table label: it documents the use and prevents
another tool from claiming the partition. It creates no array by itself.

### Creating the mirror and following the synchronisation

The spare is an inactive device that takes over **automatically** at the first
failure: that is what turns redundancy into resilience without intervention.

```bash
sudo mdadm --create /dev/md10 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdb2 \
  --spare-devices=1 /dev/vdb3
```

On AlmaLinux 10, `mdadm` 4.4 asks **two questions** before creating:

```text
To optimalize recovery speed, it is recommended to enable write-indent bitmap,
do you want to enable it now? [y/N]?
mdadm: Note: this array has metadata at the start and
    may not be suitable as a boot device.  …
Continue creating array [y/N]? mdadm: Defaulting to version 1.2 metadata
mdadm: array /dev/md10 started.
```

Answering `y` to both is fine. If you script it, `--bitmap=internal` removes the
first question and `--run` the second:

```bash
sudo mdadm --create /dev/md10 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdb2 \
  --spare-devices=1 /dev/vdb3 --bitmap=internal --run
```

The initial synchronisation is followed in `/proc/mdstat`:

```text
md10 : active raid1 vdb3[2](S) vdb2[1] vdb1[0]
      509952 blocks super 1.2 [2/2] [UU]
      [===============>.....]  resync = 78.5% (401280/509952) finish=0.0min speed=200640K/sec
      bitmap: 1/1 pages [4KB], 65536KB chunk
```

Three things to read on those lines:

- **`(S)`** marks the spare: `vdb3` is there, but carries no data.
- **`[2/2] [UU]`** gives the state of the active disks, `U` for up, `_` for
  missing.
- The `resync` line is not a failure: it is the first copy, and the array is
  already usable during that time.

`mdadm --detail` gives the full view, the one that counts for a check:

```text
        Raid Level : raid1
      Raid Devices : 2
             State : clean
    Active Devices : 2
   Working Devices : 3
    Failed Devices : 0
     Spare Devices : 1
[...]
       0     252       17        0      active sync   /dev/vdb1
       1     252       18        1      active sync   /dev/vdb2
       2     252       19        -      spare   /dev/vdb3
```

`Working Devices : 3` for `Raid Devices : 2`: the two active members plus the
spare.

### Formatting and mounting

An `mdadm` array behaves like an ordinary disk: it is formatted and mounted the
same way.

```bash
sudo mkfs.xfs /dev/md10
sudo mkdir -p /srv/miroir-demo
sudo mount /dev/md10 /srv/miroir-demo
findmnt -n /srv/miroir-demo
```

```text
/srv/miroir-demo /dev/md10 xfs rw,relatime,seclabel,attr2,inode64,…
```

For a persistent mount, you go through the **UUID of the filesystem**, not
through `/dev/md10`: the device name can change (the next section shows why), the
UUID cannot.

```bash
sudo blkid /dev/md10
```

```text
/dev/md10: UUID="25cb208f-60cd-4d59-8ad0-6fa3e7756e11" BLOCK_SIZE="512" TYPE="xfs"
```

```text title="/etc/fstab"
UUID=25cb208f-60cd-4d59-8ad0-6fa3e7756e11 /srv/miroir-demo xfs defaults,nofail 0 0
```

The **`nofail`** option prevents a degraded array from blocking the boot. Test
the line without rebooting, with `sudo mount -a`: if the command goes through
without an error, the syntax is right.

### Making the array persistent: the trap that costs points

An array created in memory is **not reassembled identically** after a reboot as
long as it is not declared in the configuration and included in the
**initramfs**. On RHEL and AlmaLinux, `/etc/mdadm.conf` does **not exist by
default**: you have to create it.

```bash
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf
sudo dracut --force
```

```text
ARRAY /dev/md10 metadata=1.2 spares=1 UUID=b80196f2:943633e5:33dc2b1f:19baf30b
```

The line identifies the array by **UUID**, so independently of the order of the
disks. On Debian and Ubuntu, the file is `/etc/mdadm/mdadm.conf` and the
initramfs is regenerated with `sudo update-initramfs -u`.

Why the `dracut` matters: before, the initramfs contained **nothing** of
`mdadm`; after, it carries the `mdraid` module and the binary.

```bash
sudo lsinitrd /boot/initramfs-$(uname -r).img | grep -c mdadm    # 0 before, non-zero after
```

The name the array takes back depends, for its part, on `/etc/mdadm.conf`. The
following demonstration establishes it without rebooting, by stopping the array
then forcing a new detection of the disks:

```bash
sudo umount /srv/miroir-demo && sudo mdadm --stop /dev/md10
sudo mv /etc/mdadm.conf /root/mdadm.conf.save        # the conf is moved aside
sudo udevadm trigger --subsystem-match=block --action=add && sudo udevadm settle
cat /proc/mdstat
```

```text
md127 : active (auto-read-only) raid1 vdb3[2] vdb4[3](S) vdb2[1]
      509952 blocks super 1.2 [2/2] [UU]
```

The array came back, but under the name **`/dev/md127`**. Nothing is lost, except
that every `/etc/fstab` line or every script that talked about `/dev/md10` now
aims at a nonexistent device. Put the configuration back in place and redo the
same test:

```bash
sudo mdadm --stop /dev/md127 && sudo cp /root/mdadm.conf.save /etc/mdadm.conf
sudo udevadm trigger --subsystem-match=block --action=add && sudo udevadm settle
cat /proc/mdstat
```

```text
md10 : active raid1 vdb3[2] vdb4[3](S) vdb2[1]
      509952 blocks super 1.2 [2/2] [UU]
```

> **What is not proven here: the behaviour at boot.** The machine was not
> rebooted; what precedes is a hot reassembly. The rule from the guide stands
> whole: `mdadm.conf` **plus** a regenerated initramfs, otherwise the array may
> not come back up as expected.

### Simulating a failure and rebuilding

The gesture expected in an exam holds in three words: **mark**, **remove**,
**add**. The failure is simulated with `--fail`.

```bash
sudo mdadm /dev/md10 --fail /dev/vdb1
cat /proc/mdstat
```

```text
md10 : active raid1 vdb3[2] vdb2[1] vdb1[0](F)
      509952 blocks super 1.2 [2/1] [_U]
      [>....................]  recovery =  0.8% (4096/509952) finish=2.0min speed=4096K/sec
```

`(F)` marks the failed disk, `[2/1] [_U]` says that only one active member out of
two remains, and the `recovery` line shows the spare rebuilding. `mdadm --detail`
says it in so many words:

```text
             State : clean, degraded, recovering
    Active Devices : 1
    Failed Devices : 1
    Rebuild Status : 14% complete
[...]
       2     252       19        0      spare rebuilding   /dev/vdb3
```

Throughout the rebuild, the filesystem stays mounted and readable: that is the
whole point of the mirror. Once it is over, the array goes back to `[UU]`, the
spare having become an active member and `vdb1` staying listed as `faulty`.

Then remove the failed disk, and add its replacement, which becomes the new
spare:

```bash
sudo mdadm /dev/md10 --remove /dev/vdb1
sudo mdadm /dev/md10 --add /dev/vdb4
cat /proc/mdstat
```

```text
mdadm: hot removed /dev/vdb1 from /dev/md10
mdadm: added /dev/vdb4
md10 : active raid1 vdb4[3](S) vdb3[2] vdb2[1]
      509952 blocks super 1.2 [2/2] [UU]
```

> **On a small array, everything goes too fast to be observed.** Those 500 MiB
> rebuild in a few seconds. Follow it with `watch -n1 cat /proc/mdstat`, or
> deliberately throttle the throughput long enough to watch:
> `echo 2000 | sudo tee /proc/sys/dev/raid/speed_limit_max` (default value
> `200000`, to be set back afterwards).

A RAID without monitoring is not resilient: a failure that goes unnoticed ends in
total loss at the second disk. The `mdmonitor` service is `enabled` as soon as
the package is installed; declare the notification address at the top of
`mdadm.conf` with a `MAILADDR root@localhost` line. For a script, `mdadm --detail
--test /dev/md10` returns 0 when the array is healthy.

### Dismantling cleanly, and troubleshooting

An array abandoned without being dismantled leaves a **RAID superblock** on every
member, which will make it reappear later. The complete cleanup, in order:

```bash
sudo umount /srv/miroir-demo
sudo mdadm --stop /dev/md10
sudo mdadm --zero-superblock /dev/vdb2 /dev/vdb3 /dev/vdb4
sudo wipefs -a /dev/vdb1 /dev/vdb2 /dev/vdb3 /dev/vdb4
cat /proc/mdstat        # must come back to "unused devices: <none>"
```

Without the `--zero-superblock`, the trace stays visible and blocks reuse:

```text
$ sudo mdadm --examine /dev/vdb1
     Array UUID : b80196f2:943633e5:33dc2b1f:19baf30b
     Raid Level : raid1

$ sudo mdadm --create /dev/md20 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdb2
mdadm: /dev/vdb1 appears to be part of a raid array:
       level=raid1 devices=2 ctime=Wed Jul 22 14:57:18 2026
```

Do not forget to remove the `ARRAY` line from `/etc/mdadm.conf` and to run `sudo
dracut --force` again: a configuration that describes a vanished array is a trap
for the next boot.

| Symptom | Likely cause | Fix |
|---|---|---|
| `mdadm --create` stays stuck on `Continue creating array [y/N]?` | the command is waiting for a confirmation | answer `y`, or add `--run` (and `--bitmap=internal` for the first question) |
| `mkfs.xfs: appears to contain an existing filesystem` | signature left by a previous use of the disk | `sudo wipefs -a /dev/mdX` before the `mkfs` |
| The array comes back as `/dev/md127` | no `ARRAY` line in `/etc/mdadm.conf` | `mdadm --detail --scan >> /etc/mdadm.conf` then `dracut --force` |
| `/proc/mdstat` displays `[_U]` | a member has failed, rebuild in progress or impossible | `mdadm --detail` then `--remove` and `--add` |
| `appears to be part of a raid array` | leftover RAID superblock | `sudo mdadm --zero-superblock /dev/vdbX` |
| Array missing or renamed after a reboot | `mdadm.conf` or initramfs out of date | regenerate the conf, then `dracut --force` (or `update-initramfs -u`) |
