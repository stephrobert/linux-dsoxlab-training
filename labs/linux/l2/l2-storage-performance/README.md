# Lab — tune a mount with noatime

## Reminder

[**Disk performance on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/)

Mount options change how a filesystem behaves. `noatime` disables access-time
updates, a common win for read-heavy workloads or ones with many small files.
Put it in `/etc/fstab` (4th field) for persistence, and `mount -o remount <mnt>`
to apply it live. `findmnt <mnt>` shows the active options.

## The course

The examples below are about a demonstration XFS filesystem mounted on
`/mnt/perf` (2 GiB `/dev/vdb` disk), with its own options. The challenge will
ask you for something else, elsewhere: what matters here is the method, not the
line to copy.

Every output in this course was taken on an AlmaLinux 10 machine (kernel 6.12,
948 MiB of RAM, virtio disks), itself a **guest of a shared hypervisor**. The
figures are real but **cannot be transposed**: the section "Measuring inside a
virtual machine" says why.

### Three quantities, never a "speed"

Talking about the "speed" of a disk as a single number is the first mistake.
Three different quantities describe a storage device, and a slow service almost
never suffers from all three at once.

| Metric | What it measures | When it matters |
|---|---|---|
| **Throughput** (MB/s) | volume transferred per second | large files, backups, video |
| **IOPS** | operations per second | databases, many small files |
| **Latency** (`await`, ms) | response time of one operation | perceived responsiveness, interactive applications |

A slow database is almost always an IOPS or latency problem, not a throughput
one. The type of disk changes the orders of magnitude: a hard drive tops out
around 100 to 200 IOPS, a SATA SSD reaches tens of thousands, an NVMe goes past
a million.

### The cache trap: the same read, two results

Linux keeps the blocks it reads and writes in memory (the page cache). A read
right after a write therefore measures the **RAM**, not the disk. The proof, on
a 200 MiB file:

```bash
sudo dd if=/dev/urandom of=/mnt/perf/demo.bin bs=1M count=200 status=none
sync
sudo dd if=/mnt/perf/demo.bin of=/dev/null bs=1M          # 1st read
sudo dd if=/mnt/perf/demo.bin of=/dev/null bs=1M          # 2nd read
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'      # drop the cache
sudo dd if=/mnt/perf/demo.bin of=/dev/null bs=1M          # 3rd read
```

Do not trust the reported throughput alone: count what the device actually
served. The kernel keeps those counters in `/sys/block/<dev>/stat`, whose 3rd
field is the number of **sectors read** (512 bytes) since boot:

```bash
awk '{print $3}' /sys/block/vdb/stat
```

By bracketing each `dd` with that read, you get:

| Read | Reported throughput | Served by `vdb` |
|---|---|---|
| 1st, warm cache | 11.3 GB/s | 0 MiB |
| 2nd, warm cache | 12.5 GB/s | 0 MiB |
| 3rd, after `drop_caches` | 6.2 GB/s | 200 MiB |

The first two measurements **did not touch the disk a single time**. The
throughput they report is that of a memory copy.

`drop_caches` is the lever that makes a read honest. It destroys nothing (it
only frees clean data, already written), but have it preceded by a `sync`, and
do not make it a habit on a production server: you are taking its cache away.

On the write side, three formulations measure three different things. Three
repetitions each, 512 MiB file:

```bash
F=/mnt/perf/testfile
dd if=/dev/zero of=$F bs=1M count=512               # no option
dd if=/dev/zero of=$F bs=1M count=512 conv=fsync    # final fsync
dd if=/dev/zero of=$F bs=1M count=512 oflag=direct  # no cache
```

```text
no option    : 2.8 GB/s | 752 MB/s | 1.1 GB/s
conv=fsync   : 758 MB/s | 1.0 GB/s | 901 MB/s
oflag=direct : 1.2 GB/s | 1.4 GB/s | 980 MB/s
```

- **With nothing**, `dd` returns as soon as the data is in the cache: the first
  attempt at 2.8 GB/s measures the speed at which the kernel accepts data,
  nothing else. That is the figure you must never quote.
- **`conv=fsync`** adds an `fsync()` at the end: the time includes flushing the
  cache. It is the measurement closest to what an application that writes then
  waits actually feels.
- **`oflag=direct`** bypasses the cache on every block (`O_DIRECT`). That is
  what `fio` does with `--direct=1`.

### Measuring inside a virtual machine: what `direct` does not bypass

`oflag=direct` bypasses the cache **of this machine**. It does not bypass the
one of the hypervisor, which also keeps the disk file in memory. `fio` in 4 kB
random read shows it without ambiguity:

```bash
sudo fio --name=randread --directory=/mnt/perf --rw=randread --bs=4k \
    --size=256M --runtime=15 --time_based --ioengine=libaio \
    --direct=1 --group_reporting
```

```text
read: IOPS=51.1k, BW=200MiB/s (209MB/s)(2995MiB/15001msec)
  lat (usec): min=12, max=3473, avg=19.28, stdev=14.48
```

51,100 IOPS with an average latency of **19 µs** and a queue depth of 1
(`iodepth=1` by default): no physical medium answers in 19 µs at that rate.
These figures describe the memory of the host, not a disk.

Three runs gave 51.1k, 54.1k and 54.2k IOPS (latencies 19.3 / 18.2 / 18.2 µs),
that is about 6 % between the extremes. **An isolated figure proves nothing.**
Repeat at least three times, state the order of magnitude and the spread, and
give the context. Here the host is shared with other virtual machines: the same
command run again tomorrow will give something else.

What a measurement made inside a VM allows you to claim: the **ratio** between
two configurations measured in the same session (with cache against without
cache, `atime` against `noatime`). What it does not allow: a characteristic of
the hardware.

> `fio` is not installed by default. On AlmaLinux 10, it comes from the
> **appstream** repository (`sudo dnf install fio`) and not from EPEL: check with
> `dnf info fio` before concluding. `dd` is enough for everything above.

### Observing the real load with iostat

`fio` **creates** a load, `iostat` (package `sysstat`) **observes** the one that
exists. Two traps fit in one sentence: the first sample is an average **since
boot** (to be ignored), and `-z` hides the inactive devices.

```bash
sudo dnf install sysstat
iostat -xz 3 2          # only the 2nd block is meaningful
```

Taken during a sustained write in 64 kiB blocks on `/mnt/perf`:

```text
Device      w/s      wkB/s  w_await  wareq-sz   f/s  f_await  aqu-sz  %util
vdb    10270.00  657135.33     0.08     63.99  4.67    95.00    1.28  83.20
```

The read columns, at zero during this test, are omitted here. What this line
says:

- **`w/s` = 10,270**: the real write IOPS.
- **`wkB/s` = 657,135**, that is about 640 MiB/s, consistent with `wareq-sz` =
  64 kiB, the block size asked of `dd`.
- **`w_await` = 0.08 ms**: the latency, the most telling indicator of a
  bottleneck.
- **`aqu-sz` = 1.28**: the average queue depth. A single sequential `dd` can
  hardly do better than 1.
- **`f/s`** and **`f_await`**: the flush requests, far slower (95 ms) than the
  writes themselves.

**`%util` = 83 % does not mean "saturated".** That column measures the fraction
of time during which at least one request is in flight. On a device able to
handle several in parallel (SSD, NVMe, virtio disk), it can reach 100 % while
the disk would accept ten times more. Here, a latency of 0.08 ms and a queue of
1.28 say the opposite of saturation. Trust `await` and `aqu-sz`. The `svctm`
column, which old guides still quote, disappeared from sysstat 12 because it was
misleading (the lab runs 12.7.6).

To find out **which process** generates the I/O, the guide suggests `iotop -oP`.
Careful: `iotop` is not in the base repositories of AlmaLinux 10 (`dnf info
iotop` returns nothing). `pidstat`, shipped with `sysstat`, does the essential
and requires root:

```bash
sudo pidstat -d 3 1
```

```text
15:14:38  UID   PID   kB_rd/s   kB_wr/s  kB_ccwr/s  iodelay  Command
15:14:38    0  37288      0.00  261273.09     0.00        0  sh
```

### Knowing the device before blaming it

```bash
lsblk -t -o NAME,PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,RA /dev/vdb
cat /sys/block/vdb/queue/scheduler
```

```text
NAME PHY-SEC LOG-SEC ROTA SCHED       RQ-SIZE   RA
vdb      512     512    1 mq-deadline     256 4096

none [mq-deadline] kyber bfq
```

- **`PHY-SEC` / `LOG-SEC`**: physical and logical sector sizes, 512 bytes both
  here. `RA` gives the readahead in kiB.
- **`SCHED`**: the active scheduler, in brackets in `/sys`. Here `mq-deadline`.
  `none` means that nothing is reordered and that the requests are passed on as
  they are: that is the usual setting when the sorting happens lower down, in
  the hypervisor or in the NVMe controller, because reordering twice only adds
  latency.
- **`ROTA` = 1** announces a rotating disk. That is wrong here: virtio does not
  know what is behind. **Never deduce the nature of the medium from a VM.**

`hdparm` gives an order of magnitude in raw read, without going through the
filesystem:

```bash
sudo hdparm -tT /dev/vdb
```

```text
 Timing cached reads:   31420 MB in  2.00 seconds = 15744.18 MB/sec
 Timing buffered disk reads: 2048 MB in  0.45 seconds =  4531.27 MB/sec
```

The first line measures the **memory**, that is explicitly its role. Only the
second one speaks about the device, and even then, with the reservations of the
previous section. Three runs gave 4531, 4605 and 4566 MB/s.

### Tuning after measuring: `atime`, `relatime`, `noatime`

Every read of a file updates its **access time** (atime), and therefore turns a
read into a write. For a long time now, Linux has mounted by default with
**`relatime`**, which only writes the atime if it is older than the modification
time, or more than 24 h old. Check it, do not assume it:

```bash
findmnt -no OPTIONS /mnt/perf
```

```text
rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

The semantics show in three moves, with `stat -c %x` printing the atime:

```text
after write   : 15:14:56.228
after 1 read  : 15:14:57.242   <- updated, because atime equalled mtime
after 2 reads : 15:14:57.242   <- unchanged
```

`relatime` therefore limits the damage without removing it: every first access
costs one write. That cost can be measured, again with the kernel counters (7th
field of `/sys/block/vdb/stat`: sectors **written**). Protocol: 3,000 fresh
small files, `sync`, `drop_caches`, then a full read.

```bash
sudo sh -c 'for i in $(seq 1 3000); do echo x > /mnt/perf/many/f$i; done'
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
awk '{print $7}' /sys/block/vdb/stat
sudo sh -c 'cat /mnt/perf/many/* > /dev/null'; sync
awk '{print $7}' /sys/block/vdb/stat
```

| Mount option | Sectors written during a pure read |
|---|---|
| `relatime` (default) | 4,533, that is about 2.2 MiB |
| `noatime` | 0 |

There is the gain, measured: on a read workload, `noatime` **completely**
removes the parasitic writes. On 3,000 files it is anecdotal; on a server that
reads millions of them per hour, it is a continuous stream of writes that
disappears.

Applying it live, without unmounting:

```bash
sudo mount -o remount,noatime /mnt/perf
findmnt -no OPTIONS /mnt/perf
```

```text
rw,noatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

This setting lives in memory: it disappears at reboot. For it to hold, you need
a line in `/etc/fstab`, whose **4th field** carries the options:

```text title="/etc/fstab"
UUID=12b52e83-a599-4e61-8cad-9de570f2a33c /mnt/perf xfs rw,noatime,nofail 0 0
```

The UUID is obtained with `sudo blkid -s UUID -o value /dev/vdb` and is worth
more than a device name, whose order can change at boot. Since a mistake in
`/etc/fstab` can block the boot, back it up and check:

```bash
sudo cp -a /etc/fstab /etc/fstab.bak   # before editing
sudo findmnt --verify                  # 0 parse errors, 0 errors expected
sudo systemctl daemon-reload           # systemd re-reads the new fstab
```

A `mount -o remount` **with no other option** re-reads the options from
`/etc/fstab`: that is the move that puts the active mount and the file back in
agreement.

```bash
sudo mount -o remount /mnt/perf
findmnt -no SOURCE,TARGET,OPTIONS /mnt/perf
```

```text
/dev/vdb /mnt/perf rw,noatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

After a real reboot of the machine, `findmnt` still shows `noatime`:
persistence is acquired, which no `remount` proves on its own.

> **Removing `noatime` is not symmetrical.** Checked on util-linux 2.40.2:
> `mount -o remount,relatime /mnt/perf` leaves `noatime` in place, whereas
> `mount -o remount,atime /mnt/perf` removes it and gives back `relatime`. It is
> the `atime` option that cancels `noatime`; `relatime` alone is not enough.
> Always check with `findmnt`, do not assume.

### Troubleshooting

| Symptom | Likely cause | Lead |
|---|---|---|
| Unrealistic `dd` throughput (several GB/s) | cache not bypassed | `oflag=direct` or `conv=fsync`, and `drop_caches` before a read |
| Two identical measurements give very different figures | single measurement, shared host, test too short | repeat at least 3 times, lengthen the duration (`--runtime=30 --time_based`) |
| `%util` at 100 % but the application feels fluid | false positive on a parallel device | look at `r_await` / `w_await` and `aqu-sz`, not `%util` |
| `iostat` prints curiously stable values | first sample, average since boot | ignore the first block, read from the second one |
| `findmnt` does not show the option added in `/etc/fstab` | fstab changed, mount unchanged | `sudo mount -o remount <mount-point>` |
| The option is active but disappears at reboot | set only by `mount -o remount,<option>` | write it in the 4th field of `/etc/fstab` |
| `iotop` not found | absent from the base repositories of AlmaLinux 10 | `sudo pidstat -d 3 1` |
