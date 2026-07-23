# Lab — reclaim a full filesystem

## Reminder

[**Disk space on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/)

`df -h` lists filesystems and their usage; `du -h --max-depth=1 <dir>` shows how
much each subdirectory holds, so you can walk down to the culprit. If `df` says
full but `du` disagrees, `lsof +L1` finds a deleted-but-open file held by a
process.

## The course

The examples below work on `/mnt/space-demo`, a small demonstration container
mounted over loopback: the challenge will deal with another mount point, other
files and other thresholds. The point is to learn the method, not to copy a
line. Every output shown was captured on the lab VM (AlmaLinux 10).

### The demonstration setup

Saturating a real filesystem is risky. So you build a disposable 64 MiB one, in
a plain file attached to a loop device:

```bash
sudo dd if=/dev/zero of=/root/space-demo.img bs=1M count=64 status=none
sudo losetup --find --show /root/space-demo.img    # prints the loop device assigned
sudo mkfs.ext4 -q -F -L space-demo /dev/loop1
sudo mkdir -p /mnt/space-demo
sudo mount /dev/loop1 /mnt/space-demo
```

`losetup --find --show` picks the first free `/dev/loopN` and prints it: use
**the value it gives you**, it is not necessarily `loop1`.

> **Why ext4 and not XFS here.** On this VM, `mkfs.xfs` refuses a container of
> that size: `Filesystem must be larger than 300MB.` XFS enforces a floor that
> 64 MiB does not clear. The diagnostic commands that follow (`df`, `du`, `lsof`)
> are identical whatever the filesystem; only the growing commands differ.

Then you put something to work on: three small reports, an archive, and a large
application log.

```bash
sudo mkdir -p /mnt/space-demo/{rapports,exports/2026-07,archives}
for i in 1 2 3; do
  sudo dd if=/dev/zero of=/mnt/space-demo/rapports/rapport-$i.pdf bs=1M count=1 status=none
done
sudo dd if=/dev/zero of=/mnt/space-demo/archives/2026-06.tar bs=1M count=8 status=none
sudo dd if=/dev/zero of=/mnt/space-demo/exports/2026-07/extraction.log bs=1M count=30 status=none
sudo sync
```

### See usage with df

`df` (*disk free*) sums up the usage of each mounted filesystem. `-h` makes the
sizes readable, `-T` adds the type, and excluding `tmpfs` and `devtmpfs` removes
the noise of the virtual filesystems:

```bash
df -hT -x tmpfs -x devtmpfs
```

```text
Filesystem     Type      Size  Used Avail Use% Mounted on
/dev/vda4      xfs        19G  1.9G   17G  10% /
efivarfs       efivarfs  256K   17K  235K   7% /sys/firmware/efi/efivars
/dev/vda3      xfs       960M  237M  724M  25% /boot
/dev/vda2      vfat      200M  9.1M  191M   5% /boot/efi
/dev/loop1     ext4       55M   42M  9.3M  82% /mnt/space-demo
```

The **`Use%`** column spots at a glance the volume close to saturation. It is
the first command to run when a "disk full" alert comes in. Here
`/mnt/space-demo` is at 82 %, everything else is quiet.

Note already two figures that do not add up: the container is 64 MiB but `Size`
announces 55M, and `Used` + `Avail` (42 + 9.3 = 51.3M) does not give `Size`
back. Nothing abnormal: the difference goes into the filesystem metadata on one
side, and into a **reserve** on the other. We come back to it below, because
that reserve explains puzzling "No space left on device" messages.

### The "full" disk that still has room: inodes

A filesystem can show free space and still refuse to write: it has exhausted its
**inodes**, the structures that describe each file. On ext4, their number is
**fixed at creation** and never moves. Millions of small files (application
sessions, caches, mail) can saturate them well before the space.

Let us build the case, with a second container deliberately poor in inodes
(`-N 512`):

```bash
sudo dd if=/dev/zero of=/root/space-demo-inodes.img bs=1M count=64 status=none
sudo losetup --find --show /root/space-demo-inodes.img
sudo mkfs.ext4 -q -F -N 512 -L space-demo-i /dev/loop2
sudo mkdir -p /mnt/space-demo-inodes
sudo mount /dev/loop2 /mnt/space-demo-inodes
df -i /mnt/space-demo-inodes
```

```text
Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/loop2        512    11   501    3% /mnt/space-demo-inodes
```

Then you create tiny files, one byte each, until it refuses:

```bash
sudo sh -c 'mkdir -p /mnt/space-demo-inodes/sessions
            for i in $(seq 1 2000); do echo x > /mnt/space-demo-inodes/sessions/sess-$i; done'
```

```text
sh: line 1: /mnt/space-demo-inodes/sessions/sess-501: No space left on device
```

The message blames a lack of space. `df -h` contradicts it:

```bash
df -h /mnt/space-demo-inodes
df -i /mnt/space-demo-inodes
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop2       59M  526K   54M   1% /mnt/space-demo-inodes

Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/loop2        512   512     0  100% /mnt/space-demo-inodes
```

**1 % of space used, 100 % of inodes.** That is the reflex to acquire: faced
with a "No space left on device" that `df -h` does not confirm, run `df -i`. The
output is no longer ambiguous, and the cure is to delete the small files
involved, or to recreate the filesystem with more inodes.

Two useful clarifications, verified on this VM:

```bash
df -i /            # root on XFS
df -i /boot/efi    # EFI partition on vfat
```

```text
Filesystem      Inodes IUsed   IFree IUse% Mounted on
/dev/vda4      9858032 34497 9823535    1% /

Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/vda2           0     0     0     - /boot/efi
```

The root is on **XFS**, which allocates its inodes dynamically: a shortage there
is far less likely than on ext4. And `vfat` has no notion of inode at all, hence
the zeros and the dash in `IUse%`: on that kind of filesystem, `df -i` will tell
you nothing.

### Locate what takes up the space with du

`df` says **how much**, `du` (*disk usage*) says **where**. The form to remember
lists a single level and sorts from smallest to largest:

```bash
sudo du -h --max-depth=1 /usr | sort -h
```

```text
0	/usr/games
0	/usr/src
4.0K	/usr/local
56K	/usr/include
7.0M	/usr/libexec
38M	/usr/sbin
62M	/usr/bin
171M	/usr/share
181M	/usr/lib64
312M	/usr/lib
769M	/usr
```

`sort -h` (*human-numeric*) understands the `K`, `M` and `G` suffixes and puts
the largest at the bottom, so just above your prompt. The last line is the total
of the directory queried. For that total alone, `du -sh` is enough:

```bash
sudo du -sh /usr/share
```

```text
171M	/usr/share
```

The `sudo` is not decorative. Without it, `du` runs into the directories it
cannot read and **underestimates the total**, reporting the refusals of course,
but on the error output that most people redirect to `/dev/null`:

```bash
du -sh /var 2>/dev/null       # 50M
sudo du -sh /var              # 71M
du -sh /var 2>&1 | grep -c 'Permission denied'   # 31
```

Twenty-one megabytes were missing, spread across 31 unreadable directories. A
diagnosis run without privileges can therefore clear the real culprit.

Let us apply the method to the saturated container. First level:

```bash
sudo du -h --max-depth=1 /mnt/space-demo | sort -h
```

```text
12K	/mnt/space-demo/lost+found
3.1M	/mnt/space-demo/rapports
8.1M	/mnt/space-demo/archives
31M	/mnt/space-demo/exports
42M	/mnt/space-demo
```

`exports` weighs 31M out of the 42M total. You go down into it:

```bash
sudo du -h --max-depth=1 /mnt/space-demo/exports | sort -h
ls -lh /mnt/space-demo/exports/2026-07/
```

```text
31M	/mnt/space-demo/exports
31M	/mnt/space-demo/exports/2026-07

total 31M
-rw-r--r--. 1 root root 31M Jul 22 13:03 extraction.log
```

Two `du` and one `ls` were enough. That is the whole method: **you do not
rummage, you descend**, following at each level the heaviest line.

> **`ncdu` does the same thing interactively.** The companion guide recommends it
> to go faster: sorted sizes, arrow-key navigation, deletion with the `d` key. It
> is **not installed** on this VM (`command -v ncdu` prints nothing and exits
> with code 1); install it with `sudo dnf install ncdu` on AlmaLinux,
> `sudo apt install ncdu` on Debian and Ubuntu.

### The trap of the deleted-but-still-open file

This is the symptom that throws people off, and the one exams like: you delete
the big file found by `du`, and `df` does not budge an inch.

Let us set a process writing into that log. The `exec >>` opens the file **only
once**, at startup, and keeps the descriptor:

```bash
sudo tee /root/space-demo-writer.sh >/dev/null <<'EOF'
#!/bin/sh
exec >> /mnt/space-demo/exports/2026-07/extraction.log
while true; do echo "space-demo ligne"; sleep 5; done
EOF
sudo chmod +x /root/space-demo-writer.sh
sudo setsid /root/space-demo-writer.sh </dev/null >/dev/null 2>&1 &
```

You delete the culprit, then you look:

```bash
sudo rm -f /mnt/space-demo/exports/2026-07/extraction.log
sync
df -h /mnt/space-demo
sudo du -sh /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   42M  9.3M  82% /mnt/space-demo

12M	/mnt/space-demo
```

**`df` says 42M, `du` says 12M.** Thirty megabytes vanished on the `du` side
without coming back on the `df` side. The reason fits in one sentence: `rm` does
not delete a file, it deletes a **name**. The blocks are only returned when
nobody holds the inode any more, and our process still holds it through its open
descriptor. The file has no name left, so `du`, which walks the tree, no longer
sees it; the filesystem still counts it.

`lsof +L1` lists exactly those files, the ones whose link count has dropped
below 1:

```bash
sudo lsof +L1
```

```text
COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NLINK NODE NAME
space-dem 39645 root    1w   REG    7,1 31457314     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
sleep     39783 root    1w   REG    7,1 31457314     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
```

Four columns carry all the information: `PID` names the process to deal with,
`SIZE/OFF` quantifies the space held (31,457,314 bytes, the missing 30 MiB),
`NLINK` is `0` because no name points to the inode any more, and the `(deleted)`
suffix confirms it.

Two details this output reveals and that you must have seen once:

- **The descriptor is inherited.** The loop's `sleep` shows up too, with the same
  inode number: a child receives a copy of its parent's descriptors. Killing the
  parent alone therefore does not always free the space right away.
- **Passing a mount point as an argument does not filter.** On this VM,
  `sudo lsof +L1 /mnt/space-demo` returns exactly the same list as
  `sudo lsof +L1`, entries from other filesystems included. To target, filter the
  output: `sudo lsof +L1 | grep /mnt/space-demo`.

The reference solution is to **restart the writing service cleanly**
(`sudo systemctl restart <service>`): it closes its old descriptor and reopens
one on a fresh file. Failing a service, you stop the process, aiming at the
`PID` read in `lsof`:

```bash
sudo kill 39645
sleep 7
df -h /mnt/space-demo
sudo du -sh /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   12M   40M  22% /mnt/space-demo

12M	/mnt/space-demo
```

The space is returned and the two commands reconcile: 12M on both sides, 82 %
back down to 22 %.

> **Kill by PID, not by pattern.** `pkill -f space-demo-writer` looks more
> convenient, but the pattern is compared to the **full** command line of every
> process. On this VM, it cut the SSH session it was launched from, because that
> command line also contained the pattern. The `PID` shown by `lsof` does not
> carry that risk.

#### Free the space without cutting the service

When restarting the service costs too much, there is a way out: empty the file
**through its descriptor**, via `/proc/<PID>/fd/<FD>`. The `FD` column of `lsof`
gives the number, here `1w`, so descriptor 1:

```bash
sudo sh -c ': > /proc/39645/fd/1'
df -h /mnt/space-demo
ps -o pid,comm,etime -p 39645
sudo lsof +L1 | grep extraction.log
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   12M   40M  22% /mnt/space-demo

    PID COMMAND             ELAPSED
  39645 space-demo-writ       00:23

space-dem 39645 root    1w   REG    7,1        0     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
sleep     39961 root    1w   REG    7,1        0     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
```

The space is freed, the process is **still running**, and `lsof` keeps listing
the deleted file but with `SIZE/OFF` at `0`: it no longer holds anything. This
manoeuvre buys time on a server under alert, but it does not exempt you from
dealing with the cause (missing log rotation, service to restart).

### The ext4 reserve: full for the user, not for root

Let us go back to the first container, down to 22 %, and let an ordinary user
fill it:

```bash
sudo mkdir -p /mnt/space-demo/bac-a-sable
sudo chmod 0777 /mnt/space-demo/bac-a-sable
sudo -u student dd if=/dev/zero of=/mnt/space-demo/bac-a-sable/space-demo-fill bs=1M count=100
df -h /mnt/space-demo
```

```text
dd: error writing '/mnt/space-demo/bac-a-sable/space-demo-fill': No space left on device
40+0 records in

Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   51M  3.0K 100% /mnt/space-demo
```

`Use%` is at 100 %, `Avail` at 3 KB. And yet root still writes:

```bash
sudo dd if=/dev/zero of=/mnt/space-demo/bac-a-sable/space-demo-root.bin bs=1M count=3 status=none
df -h /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   54M     0 100% /mnt/space-demo
```

Three more megabytes went through. `tune2fs` explains why:

```bash
sudo tune2fs -l /dev/loop1 | grep -Ei '^Block count|^Reserved block count|^Block size|^Reserved blocks uid'
```

```text
Block count:              65536
Reserved block count:     3276
Block size:               1024
Reserved blocks uid:      0 (user root)
```

3,276 blocks of 1 KB, about 3.2 MiB (5 % of the filesystem), are **reserved for
root**. The goal is to keep a saturated system manageable: system services and
logs still have somewhere to write when applications no longer do. Consequence
worth knowing: on an ext4 filesystem shown at 100 %, a `sudo` will sometimes
succeed where the application fails. That is not space recovered, it is the
reserve being eaten into.

### When cleaning up is not enough any more: growing

Sometimes there is nothing left to delete. You then have to widen the volume,
and the procedure depends on the layer underneath. On our ext4 loopback
container, growing is done **live**, with the filesystem mounted:

```bash
sudo rm -f /mnt/space-demo/bac-a-sable/space-demo-root.bin
df -h /mnt/space-demo
sudo truncate -s 128M /root/space-demo.img   # grow the container
sudo losetup -c /dev/loop1                   # the loop device re-reads its capacity
sudo resize2fs /dev/loop1                    # the filesystem takes the space
df -h /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   51M  3.0K 100% /mnt/space-demo

resize2fs 1.47.1 (20-May-2024)
Filesystem at /dev/loop1 is mounted on /mnt/space-demo; on-line resizing required
old_desc_blocks = 1, new_desc_blocks = 1
The filesystem on /dev/loop1 is now 131072 (1k) blocks long.

Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1      115M   51M   58M  47% /mnt/space-demo
```

The order must not be neglected: **the container first, the filesystem next**.
`resize2fs` without a size argument takes all the available space. Depending on
the layer, the move changes:

| Layer | Command to grow |
|---|---|
| LVM logical volume | `sudo lvextend -r -L +<size> <vg>/<lv>` (`-r` chains the filesystem resize) |
| ext4 partition | grow the partition, then `sudo resize2fs <partition>` |
| XFS partition | grow the partition, then `sudo xfs_growfs <mount-point>` |

One rule to remember from that table: **XFS never shrinks**, it only knows how
to grow. And to cap consumption upstream rather than run after it, disk quotas
are what you need to put in place.

### The systemd journals

They grow over time and are a frequent culprit of a `/var` swelling for no
apparent reason. Their size is read directly:

```bash
journalctl --disk-usage
```

```text
Archived and active journals take up 12.7M in the file system.
```

Two commands shrink them without breaking anything: `sudo journalctl
--vacuum-size=200M` keeps at most 200 MB, `sudo journalctl --vacuum-time=2weeks`
keeps at most two weeks.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| "No space left on device" while `df -h` shows room | inodes exhausted: check with `df -i` |
| `df` stays full after an `rm`, but `du` did go down | deleted file still open: `sudo lsof +L1`, then restart the service or kill the PID |
| `df` stays full even after killing the process | a child inherited the descriptor; read `lsof +L1` again and deal with the remaining PIDs |
| `du` returns a total smaller than reality | run without `sudo`: unreadable directories are ignored |
| The application writes "disk full" but `sudo` still writes | ext4 root reserve (5 % by default), visible with `sudo tune2fs -l` |
| `mkfs.xfs` refuses: `Filesystem must be larger than 300MB` | container too small for XFS; use ext4 or grow it |
| `resize2fs` does not see the new size | the loop device did not re-read its capacity: `sudo losetup -c /dev/loopN` |
| `/var` grows with no obvious file | systemd journals: `journalctl --disk-usage`, then `--vacuum-size` |
| An SSH session is cut during the cleanup | a `pkill -f` matched its own command line; kill by PID |

To tear everything down and start over:

```bash
sudo kill <PID-of-the-writer>             # read again in lsof +L1 if needed
sudo umount /mnt/space-demo /mnt/space-demo-inodes
sudo losetup -d /dev/loop1 /dev/loop2
sudo rm -f /root/space-demo.img /root/space-demo-inodes.img /root/space-demo-writer.sh
sudo rmdir /mnt/space-demo /mnt/space-demo-inodes
```

Check that nothing is left behind: `losetup -a` must no longer mention your
images, and `df -h` must no longer list your mount points.
