# Lab — XFS user quotas

## Reminder

[**Quotas on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/)

On XFS, quotas are enabled by a **mount option**, not by a service: `uquota`
(users) or `gquota` (groups). `xfs_quota -x -c "state -u" <mount>` shows two
distinct things — `Accounting` (measuring) and `Enforcement` (capping). Limits
are set with `xfs_quota -x -c "limit bsoft=… bhard=… <user>" <mount>` and read
back with `report -u -b`.

The mount option must be in `/etc/fstab`, otherwise the quotas are lost at the
next reboot.

## The course

The examples below cap a user `stagiaire` on two demonstration filesystems
mounted under `/mnt`, with thresholds of a few megabytes: the challenge will
deal with another medium, another account and other values. Learn the sequence,
do not copy a line. Every output comes from an **Ubuntu 24.04.4** VM, kernel
**6.8.0-134-generic**, the same image as the one used by the lab.

### Where the machine stands

Three questions before setting the first quota: does the kernel know how to
handle them, are the tools there, and for which filesystem.

```bash
sudo grep -E '^CONFIG_(QUOTA|QFMT_V2|XFS_QUOTA)=' /boot/config-$(uname -r)
```

```text
CONFIG_XFS_QUOTA=y
CONFIG_QUOTA=y
CONFIG_QFMT_V2=m
```

Read the suffixes, the whole course fits inside them. **`y`** means compiled
**into** the kernel, **`m`** provided as a separate **module**. XFS support is
built in; the quota file format that ext4 uses (`QFMT_V2`) is a module, so
something that may be missing. We will see that it is missing on this image.

On the user space side, `xfs_quota` is already there (package `xfsprogs`), but
the generic tools are missing: `dpkg -l quota` answers `un  quota  <none>`, that
is desired state *Unknown*, actual state *Not-installed*. A single package, with
no new dependency at all, brings them all. After
`sudo apt-get install -y quota`, the same command answers `ii  quota
4.06-1build6  amd64  disk quota management tools`, and you get `quotacheck`,
`quotaon`, `setquota`, `edquota`, `repquota` and `quota`.

### ext4: the full chain, and the missing module

On ext4, bringing quotas into service takes four steps: **mount option**, then
**accounting files**, then **activation**, and only then the limits. The
demonstration medium is an image file mounted through a loop device, which
avoids touching any real disk:

```bash
sudo truncate -s 512M /var/tmp/coffre-ext4.img
sudo mkfs.ext4 -q -L coffre /var/tmp/coffre-ext4.img && sudo mkdir -p /mnt/coffre
sudo cp -a /etc/fstab /root/fstab.avant-quota          # always
echo '/var/tmp/coffre-ext4.img /mnt/coffre ext4 loop,defaults,usrquota,grpquota,nofail 0 2' \
  | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a && findmnt /mnt/coffre
```

```text
TARGET      SOURCE     FSTYPE OPTIONS
/mnt/coffre /dev/loop0 ext4   rw,relatime,quota,usrquota,grpquota
```

Two habits to pick up right now: **back up `/etc/fstab` before editing it**, and
add **`nofail`** while you experiment, so a faulty line does not block boot.
Check with `sudo mount -a` then `findmnt --verify`: if both pass, the reboot
will pass too.

Mounting alone caps nothing. `quotacheck` walks the filesystem, accounts for
what is already there and creates the accounting files (`-c` creates them, `-u`
and `-g` handle users and groups, `-m` avoids a read-only remount during the
scan):

```bash
sudo quotacheck -cugm /mnt/coffre && ls -l /mnt/coffre
```

```text
-rw------- 1 root root  6144 Jul 22 18:08 aquota.group
-rw------- 1 root root  6144 Jul 22 18:08 aquota.user
[...]
```

That leaves `quotaon`, which asks the kernel to enforce. **And this is where the
Ubuntu image stops you**: as it comes out of cloud-init, the command fails.

```text
quotaon: Your kernel probably supports ext4 quota feature but you are using
external quota files. [...]
quotaon: Quota format not supported in kernel.
```

The diagnosis fits in one command, and it confirms the `=m` noted above:
`sudo modprobe quota_v2` answers `FATAL: Module quota_v2 not found in directory
/lib/modules/6.8.0-134-generic`. The module exists, but in the package
`linux-modules-extra-$(uname -r)`, which the Ubuntu cloud image does not
install. Once that package is in place, the same command goes through:

```bash
sudo apt-get install -y linux-modules-extra-$(uname -r)
sudo quotaon -v /mnt/coffre && sudo quotaon -p /mnt/coffre
```

```text
/dev/loop0 [/mnt/coffre]: group quotas turned on
/dev/loop0 [/mnt/coffre]: user quotas turned on
user quota on /mnt/coffre (/dev/loop0) is on
project quota on /mnt/coffre (/dev/loop0) is off
```

Remember the practical conclusion: **on this image, XFS does quotas without
installing anything other than `quota`, ext4 does not.** The guide does not
mention this point.

For persistence, `quotaon` does not have to be replayed by hand: the systemd
generator reads your `usrquota` options in `/etc/fstab` and wires up the right
unit, which `systemctl show mnt-coffre.mount -p Wants` confirms by answering
`Wants=systemd-quotacheck.service quotaon.service`.

### Setting and reading the limits

`setquota` takes the four caps at once, in the order **block soft, block hard,
inode soft, inode hard**, blocks being 1 KiB blocks and `0` meaning "no limit":

```bash
sudo setquota -u stagiaire 8192 10240 0 0 /mnt/coffre
sudo repquota -s /mnt/coffre
```

```text
*** Report for user quotas on device /dev/loop0
Block grace time: 7days; Inode grace time: 7days
                        Space limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
root      --     20K      0K      0K              2     0     0
stagiaire --      4K   8192K  10240K              1     0     0
```

8192 blocks of 1 KiB make 8 MiB as the soft limit, 10240 make 10 MiB as the hard
limit. `edquota -u stagiaire` presents exactly the same figures, but in an
editor, one line per filesystem, columns `blocks soft hard` then `inodes soft
hard`:

```text
  Filesystem                   blocks       soft       hard     inodes     soft     hard
  /dev/loop0                        4       8192      10240          1        0        0
```

`setquota` to script, `edquota` to adjust by hand: that is the only difference
between the two. On the reading side, `repquota` gives the administrator view of
a mount and `quota -us <user>` the view of an account across all its mounts.

### Soft, hard, grace: the three crossings

Let us write 9 MiB, so above the 8 MiB soft limit but below the 10 MiB hard one:

```bash
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre/stagiaire/rapport bs=1M count=9
sudo repquota -s /mnt/coffre | sed -n '7p'      # right away
sync ; sleep 2
sudo repquota -s /mnt/coffre | sed -n '7p'      # after the data is written
```

```text
stagiaire --      4K   8192K  10240K              2     0     0
stagiaire +-   9220K   8192K  10240K  7days       2     0     0
```

Two lessons in those two lines. First, accounting is **deferred**: as long as
the data stays in the write cache, `repquota` still shows 4 KiB (ext4 allocates
late), so `du` and `repquota` can disagree for a few seconds. Then, once the
count is up to date, the state column turns to **`+-`** (`+` = blocks over the
limit, `-` = inodes within bounds) and the `grace` column arms itself at
`7days`. The write itself was **not** refused: that is the whole difference
between soft and hard. Let us push to the hard limit:

```bash
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre/stagiaire/archive bs=1M count=5
```

```text
dd: error writing '/mnt/coffre/stagiaire/archive': Disk quota exceeded
1044480 bytes (1.0 MB, 1020 KiB) copied
```

`Disk quota exceeded` (`EDQUOT`): the kernel let the write through up to the
exact cap, then refused. `sudo quota -us stagiaire` then marks the value with an
asterisk, `10240K*`, which means "limit reached".

That leaves the trap: **the soft limit becomes blocking when the grace period
expires**. The delay is set per mount, in seconds, with `setquota -t` (or
`edquota -t`). Brought down to two minutes for the demonstration:

```bash
sudo setquota -t 120 604800 /mnt/coffre       # 120 s for blocks, 7 d for inodes
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre/stagiaire/rapport bs=1M count=9
sudo repquota -s /mnt/coffre | sed -n '7p'    # just after
sleep 130
sudo repquota -s /mnt/coffre | sed -n '7p'    # after expiry
```

```text
stagiaire +-   9220K   8192K  10240K  00:02       2     0     0
stagiaire +-   9220K   8192K  10240K   none       2     0     0
```

`none` does not mean "no overage" but "**no grace left**". At that moment, 9220
KiB used out of 10240 KiB allowed: there is apparently 1 MiB left, and yet a
512 KiB write copies **zero bytes** and returns
`dd: error writing '/mnt/coffre/stagiaire/note': Disk quota exceeded`. This is
the scenario that generates tickets: the user is below the hard limit, has
ignored the overage for a week, and the soft limit has closed in. The way out is
to clean up to get back under the soft threshold, which disarms the counter.

A word about the warning: nothing is displayed in the user's session when the
soft threshold is crossed. The message does exist, but it is delivered by the
`quota_nld` daemon (package `quota`), which is not started by default; without
it, the only signal is the `grace` column of `repquota`.

### Blocked with 452 MiB free: inode quotas

The last two arguments of `setquota` limit the **number of files**, not their
size. They get forgotten, and they produce the most puzzling refusal there is.
Unlimited blocks, five files soft, eight hard:

```bash
sudo setquota -u stagiaire 0 0 5 8 /mnt/coffre
sudo -u stagiaire bash -c 'for i in $(seq 1 10); do touch /mnt/coffre/stagiaire/f$i; done'
sudo repquota -s /mnt/coffre | sed -n '7p' ; df -h /mnt/coffre | tail -1
```

```text
touch: cannot touch '/mnt/coffre/stagiaire/f8': Disk quota exceeded
touch: cannot touch '/mnt/coffre/stagiaire/f9': Disk quota exceeded
touch: cannot touch '/mnt/coffre/stagiaire/f10': Disk quota exceeded
stagiaire -+      4K      0K      0K              8     5     8  7days
/dev/loop0      488M   44K  452M   1% /mnt/coffre
```

Seven files created, the eighth refused: the `stagiaire` directory itself counts
for one inode, hence the 8 in the report for 7 files. The disk is **1 %** full,
there are **452 MiB** left, and yet nothing gets written any more. Note the flag
inversion, **`-+`** instead of `+-`: the overage is on the inode side. Faced
with an incomprehensible `Disk quota exceeded`, run `quota -us` first, and read
the right-hand half of the table.

### XFS: same need, different mechanism

Everything above is specific to ext4. XFS keeps its accounting **internally**:
no `quotacheck`, no `quotaon`, no `aquota.*` file. Quotas are enabled **at mount
time** only, and that is where the trap lies. Mount without a quota option, then
try to add it on the fly:

```bash
sudo mount -o loop /var/tmp/coffre-xfs.img /mnt/coffre-xfs
sudo xfs_quota -x -c 'state -u' /mnt/coffre-xfs ; echo "rc=$?"
sudo mount -o remount,uquota /mnt/coffre-xfs ; echo "rc=$?"
findmnt -no OPTIONS /mnt/coffre-xfs
```

```text
rc=0
rc=0
rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

Two things to see. `state -u` **shows nothing at all** and exits 0 when no quota
is active: an empty output is the symptom, not an error. And the remount
**succeeds** (`rc=0`) without changing anything: the options stay `noquota`,
without the slightest message. Only a full unmount works:

```bash
sudo umount /mnt/coffre-xfs
sudo mount -o loop,uquota /var/tmp/coffre-xfs.img /mnt/coffre-xfs
findmnt -no OPTIONS /mnt/coffre-xfs
sudo xfs_quota -x -c 'state -u' /mnt/coffre-xfs | head -3
```

```text
rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,usrquota
User quota state on /mnt/coffre-xfs (/dev/loop1)
  Accounting: ON
  Enforcement: ON
```

A detail that matters: you wrote `uquota`, `findmnt` shows **`usrquota`**; the
kernel normalises the name, both mean the same thing. `Accounting` (measuring)
and `Enforcement` (capping) are two distinct states: the first alone would count
without refusing anything. Management then goes through `xfs_quota` in expert
mode (`-x`), with readable suffixes rather than 1 KiB blocks:

```bash
sudo xfs_quota -x -c 'limit -u bsoft=12m bhard=15m stagiaire' /mnt/coffre-xfs
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre-xfs/stagiaire/archive bs=1M count=13
sync ; sudo xfs_quota -x -c 'report -u -b' /mnt/coffre-xfs | tail -2
```

```text
User ID          Used       Soft       Hard    Warn/Grace
stagiaire       13312      12288      15360     00  [7 days]
```

The grace counter arms itself as on ext4, and `repquota -s` can read this mount
too. `quotacheck`, on the other hand, refuses flatly, with a message that
usefully reminds you that you are no longer on ext4: `Cannot find filesystem to
check or filesystem not mounted with quota option.`

Finally, the quota option is declared in `/etc/fstab` exactly as above, in the
fourth field. Without it, the next boot will mount in `noquota` and your limits,
still recorded but never enforced, will protect nothing any more.

### Troubleshooting and going back to the initial state

| Symptom | Likely cause | Fix |
|---|---|---|
| `quotaon: Quota format not supported in kernel` | `quota_v2` module missing (Ubuntu cloud image) | `sudo apt-get install linux-modules-extra-$(uname -r)` |
| `quotacheck: Cannot find filesystem to check` | Quota options missing from the mount, or XFS filesystem | `findmnt <mount>`; on XFS, switch to `xfs_quota` |
| `xfs_quota -x -c 'state -u'` answers nothing | No quota active on this mount | Unmount, remount with `uquota` |
| XFS quotas stay inactive after `mount -o remount` | XFS reads these options only at the initial mount | `umount` then `mount` |
| `Disk quota exceeded` with free space available | **Inode** quota reached, or grace expired on the soft threshold | `quota -us <user>` and read the right-hand columns |
| `repquota` disagrees with `du` | Write not yet flushed from the cache | `sync`, then read again |

To undo everything, in this order: turn quotas off, unmount, restore
`/etc/fstab` from the copy taken **before** the edit, then check.

```bash
sudo quotaoff /mnt/coffre
sudo umount /mnt/coffre /mnt/coffre-xfs
sudo cp -a /root/fstab.avant-quota /etc/fstab && sudo systemctl daemon-reload
findmnt --verify | tail -1        # 0 parse errors, 0 errors
```

One last habit: deleting a user does not delete their quotas, which stay
attached to the UID and which a future account may inherit. On ext4, reset the
counters with `sudo setquota -u <user> 0 0 0 0 <mount>` **before** the `userdel`.
