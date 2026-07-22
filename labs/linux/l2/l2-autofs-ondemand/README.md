# Lab — on-demand mounts with autofs

## Reminder

[**autofs on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/)

autofs mounts a path only when it is accessed and unmounts it after an idle
`--timeout`. A **master map** (`/etc/auto.master` or a file in
`/etc/auto.master.d/`) maps a mount point to a **mount map**; the mount map lists
keys and how to mount them, in the form `key  -options  source`. `systemctl
restart autofs` reloads the maps.

## The course

The examples below work on `/mnt/autofs-demo`, a demonstration XFS image placed
in `/srv/autofs-demo`: the challenge will ask you for another mount point, other
map files and another source. The point is to learn the method, not to copy a
line.

Every output below was produced on the VM of this lab (AlmaLinux 10,
`autofs-5.1.9-13.el10.x86_64`).

### Where the machine stands

Before writing anything, look at what already exists:

```bash
rpm -q autofs                 # or: dpkg -l autofs on Debian/Ubuntu
systemctl is-active autofs
cat /etc/auto.master
ls -la /etc/auto.master.d/
```

On a fresh AlmaLinux, `/etc/auto.master` exists and **already contains two mount
points** shipped by the package, `/misc` and `/net`, plus the inclusion line
`+dir:/etc/auto.master.d` which loads every `*.autofs` file in that directory.
Do not mistake them for your configuration.

`automount -m` shows what autofs actually loaded, master and mount maps
together:

```bash
sudo automount -m
```

```text
Mount point: /misc

source(s):

  instance type(s): file
  map: /etc/auto.misc

  cd | -fstype=iso9660,ro,nosuid,nodev	:/dev/cdrom
```

This is the command to run first when a map "does not take": if your mount point
is not in there, autofs did not read it.

### Preparing a source to mount

For the demonstration, a file image formatted in XFS will act as a disk.
`mkfs.xfs` refuses images smaller than 300 MB, hence the 512 MiB.

```bash
sudo mkdir -p /srv/autofs-demo
sudo truncate -s 512M /srv/autofs-demo/archives.img
sudo mkfs.xfs -q /srv/autofs-demo/archives.img
ls -lh /srv/autofs-demo/
```

```text
total 65M
-rw-r--r--. 1 root root 512M Jul 22 13:00 archives.img
```

Note the gap between the announced size (`512M`) and the real occupation
(`total 65M`): `truncate` creates a sparse file, which only consumes what is
written into it.

A marker is dropped inside, by mounting the image once by hand, so that you have
something to check later that the automatic mount really serves that content:

```bash
sudo mkdir -p /mnt/autofs-demo-seed
sudo mount -o loop /srv/autofs-demo/archives.img /mnt/autofs-demo-seed
echo "inventaire 2026" | sudo tee /mnt/autofs-demo-seed/inventaire.txt
sudo umount /mnt/autofs-demo-seed && sudo rmdir /mnt/autofs-demo-seed
```

### The two maps

autofs needs two files, and the logical order is always the same.

1. The **master map** says *where*: it maps a parent mount point to a map file.
   You do not modify `/etc/auto.master`: you drop a `*.autofs` file in
   `/etc/auto.master.d/`, which is included automatically.

   ```text
   /parent-mount-point   /etc/map-file   [options]
   ```

2. The **mount map** says *what*: one line per mount, in the form
   `key  -options  source`. The key becomes the subdirectory created under the
   parent point. The source is a local device (`:/dev/…`), an image, or a
   network share (`server:/export`).

Let us write both:

```bash
echo '/mnt/autofs-demo  /etc/auto.autofs-demo  --timeout=30' \
  | sudo tee /etc/auto.master.d/autofs-demo.autofs
echo 'archives  -fstype=xfs,loop  :/srv/autofs-demo/archives.img' \
  | sudo tee /etc/auto.autofs-demo
sudo systemctl restart autofs
```

The `loop` option asks `mount` to attach the image to a loop device; it only
makes sense for a source that is a file. `--timeout=30` unmounts after 30
seconds of inactivity.

Look at what the restart changed in the mount table:

```bash
mount | grep autofs
```

Before:

```text
/etc/auto.misc on /misc type autofs (rw,relatime,fd=6,pgrp=38113,timeout=300,...,indirect,...)
-hosts on /net type autofs (rw,relatime,fd=9,pgrp=38113,timeout=300,...,indirect,...)
```

After:

```text
/etc/auto.misc on /misc type autofs (...)
-hosts on /net type autofs (...)
/etc/auto.autofs-demo on /mnt/autofs-demo type autofs (rw,relatime,fd=12,pgrp=38638,timeout=30,minproto=5,maxproto=5,indirect,pipe_ino=104355)
```

Three things to read in that line. The **type is `autofs`**, not `xfs`: none of
the content is mounted yet, it is the trigger that is in place. The
**`timeout=30`** confirms that the master map option was taken into account. And
the word **`indirect`** says that autofs manages a parent directory under which
it will create the keys.

The `/mnt/autofs-demo` directory was never created by hand: autofs is the one
that lays it down when it reads the master map.

### The trigger, and the trap of the empty directory

This is the point that throws everyone off. After the service restart, the
parent looks **empty**:

```bash
ls -la /mnt/autofs-demo
```

```text
total 0
drwxr-xr-x. 2 root root  0 Jul 22 13:01 .
drwxr-xr-x. 4 root root 43 Jul 22 13:01 ..
```

No trace of the `archives` key, and yet the map is correct. An `ls` of the
parent **triggers nothing**: the mount table does not move.

You have to name the key for the mount to happen:

```bash
ls -l /mnt/autofs-demo/archives
```

```text
total 4
-rw-r--r--. 1 root root 16 Jul 22 13:00 inventaire.txt
```

This time the table has changed:

```bash
mount | grep autofs-demo
```

```text
/etc/auto.autofs-demo on /mnt/autofs-demo type autofs (rw,relatime,...,timeout=30,...,indirect,...)
/srv/autofs-demo/archives.img on /mnt/autofs-demo/archives type xfs (rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota)
```

A **second line** appeared, of type `xfs` this time: the filesystem is mounted.
And the parent is no longer empty:

```text
drwxr-xr-x. 3 root root  0 Jul 22 13:01 .
drwxr-xr-x. 4 root root 43 Jul 22 13:01 ..
drwxr-xr-x. 2 root root 28 Jul 22 13:00 archives
```

`lsblk` shows the loop device attached along the way:

```text
loop2    7:2    0  512M  0 loop /mnt/autofs-demo/archives
```

> **`findmnt <path>` triggers the very mount it is supposed to observe.** On this
> VM, after the timeout expired, `findmnt /mnt/autofs-demo/archives` returns
> nothing (`rc=1`, so "not mounted"), but a `grep autofs-demo
> /proc/self/mounts` run **right after** shows the XFS mount present: merely
> naming the path woke autofs up, and `findmnt` read the table before the mount
> existed. Result: the first command says "nothing", the second says "mounted",
> and you believe there is an inconsistency. To observe the state **without**
> changing it, read the table without touching the path: `mount | grep …` or
> `grep … /proc/self/mounts`.

If that empty parent directory bothers you, the **`--ghost`** option in the
master map makes the keys appear as empty directories before any mount:

```bash
sudo sed -i 's|--timeout=30|--timeout=30 --ghost|' /etc/auto.master.d/autofs-demo.autofs
sudo systemctl restart autofs
ls -la /mnt/autofs-demo
```

```text
total 0
drwxr-xr-x. 5 root root   0 Jul 22 13:08 .
drwxr-xr-x. 9 root root 173 Jul 22 13:08 ..
drwxr-xr-x. 2 root root   0 Jul 22 13:08 archives
drwxr-xr-x. 2 root root   0 Jul 22 13:08 casse
drwxr-xr-x. 2 root root   0 Jul 22 13:08 nouvelle
```

That output was recorded later in the session, when the map already counted
three keys: `casse` and `nouvelle` show up in the following sections. The
essential point is elsewhere: the keys are visible, but **nothing is mounted**.
`grep autofs-demo/ /proc/self/mounts` still returns nothing as long as you do
not enter them. Those directories are decoys that make the map readable, not
mounts.

One last useful reflex: the parent of an indirect map **is not writable**, only
autofs creates entries there.

```bash
sudo mkdir /mnt/autofs-demo/essai
# mkdir: cannot create directory ‘/mnt/autofs-demo/essai’: Permission denied
```

A `Permission denied` as `root` on an autofs point is therefore not a permission
anomaly: it is normal behaviour.

### Automatic unmounting

Let the timeout pass without touching the path, then read the table without
naming it:

```bash
sleep 50
grep autofs-demo /proc/self/mounts
```

```text
/etc/auto.autofs-demo /mnt/autofs-demo autofs rw,relatime,fd=12,...,timeout=30,...,indirect,... 0 0
```

The `xfs` line is gone, the `autofs` one remains: the content was unmounted, the
trigger is still armed. A new access will mount it again.

Do not count on an unmount to the second. The daemon checks periodically, at a
rhythm visible in its verbose output:

```text
mounted indirect on /mnt/autofs-demo with timeout 30, freq 8 seconds
```

With `--timeout=30`, the check runs every 8 seconds: the mount therefore
disappears somewhere between 30 and 38 seconds after the last access.

### Reloading: `reload` rather than `restart`

The guide recommends `systemctl restart autofs` after every change. On this VM,
the observed behaviour is finer, and the nuance is worth the detour.

**A new key in the mount map requires no reload at all.** Add a line, then
access it immediately, without restarting anything:

```bash
echo 'nouvelle  -fstype=bind  :/srv/autofs-demo/coffres/2025' \
  | sudo tee -a /etc/auto.autofs-demo
ls /mnt/autofs-demo/nouvelle
# bilan.txt
```

The daemon rereads the map file on its own. Its verbose output announces it:
`re-reading map for /mnt/autofs-demo`.

**A new mount point in the master map, on the other hand, requires a reload.**
Let us add one, with its mount map, without reloading anything:

```bash
echo '/mnt/autofs-demo-tardif  /etc/auto.autofs-demo-tardif  --timeout=30' \
  | sudo tee -a /etc/auto.master.d/autofs-demo.autofs
echo 'k  -fstype=bind  :/srv/autofs-demo/coffres/2024' \
  | sudo tee /etc/auto.autofs-demo-tardif
ls /mnt/autofs-demo-tardif/k
# ls: cannot access '/mnt/autofs-demo-tardif/k': No such file or directory
```

And `systemctl reload autofs` is enough, which is preferable to `restart`:

```bash
sudo systemctl reload autofs
ls /mnt/autofs-demo-tardif/k
# bilan.txt
```

The difference between the two is concrete. With an active mount, `reload`
**keeps** it; `restart` **throws it away**:

```text
--- avant reload ---
/dev/loop3 /mnt/autofs-demo/archives xfs rw,seclabel,relatime,... 0 0
--- apres reload ---
/dev/loop3 /mnt/autofs-demo/archives xfs rw,seclabel,relatime,... 0 0
--- apres restart ---
(plus rien)
```

On a production machine where users are working inside autofs mounts, `reload`
avoids cutting their access from under their feet. `systemctl show -p CanReload
autofs` answers `CanReload=yes` on AlmaLinux 10.

### Wildcard map: one line for every key

Declaring one line per user or per year would be unmanageable. The `*` character
accepts any key, and `&` reuses its value in the source. The guide illustrates
this case with NFS home directories; here, lacking a server, the same mechanism
is shown with local `bind` mounts.

```bash
sudo mkdir -p /srv/autofs-demo/coffres/2024 /srv/autofs-demo/coffres/2025
echo "bilan 2024" | sudo tee /srv/autofs-demo/coffres/2024/bilan.txt
echo "bilan 2025" | sudo tee /srv/autofs-demo/coffres/2025/bilan.txt
echo '/mnt/autofs-demo-coffres  /etc/auto.autofs-demo-coffres  --timeout=30' \
  | sudo tee -a /etc/auto.master.d/autofs-demo.autofs
echo '*  -fstype=bind  :/srv/autofs-demo/coffres/&' \
  | sudo tee /etc/auto.autofs-demo-coffres
sudo systemctl restart autofs
```

The two keys mount separately, on demand, without either having been declared:

```bash
cat /mnt/autofs-demo-coffres/2025/bilan.txt   # bilan 2025
cat /mnt/autofs-demo-coffres/2024/bilan.txt   # bilan 2024
grep autofs-demo-coffres /proc/self/mounts
```

```text
/etc/auto.autofs-demo-coffres /mnt/autofs-demo-coffres autofs ...,indirect,... 0 0
/dev/vda4 /mnt/autofs-demo-coffres/2025 xfs rw,seclabel,relatime,... 0 0
/dev/vda4 /mnt/autofs-demo-coffres/2024 xfs rw,seclabel,relatime,... 0 0
```

Two details worth noting. The source displayed is `/dev/vda4`, the disk that
really carries the data: a `bind` does not create a new device, it re-exposes an
existing tree. And a key with no matching source fails cleanly:

```bash
ls /mnt/autofs-demo-coffres/1999
# ls: cannot access '/mnt/autofs-demo-coffres/1999': No such file or directory
```

### Direct map: an absolute path, with no common parent

When the mount points have no common parent directory, the master map uses the
`/-` symbol and it is the mount map that carries the absolute paths.

```bash
echo '/-  /etc/auto.autofs-demo-direct  --timeout=30' \
  | sudo tee -a /etc/auto.master.d/autofs-demo.autofs
echo '/mnt/autofs-demo-direct  -fstype=bind  :/srv/autofs-demo/coffres/2024' \
  | sudo tee /etc/auto.autofs-demo-direct
sudo systemctl restart autofs
cat /mnt/autofs-demo-direct/bilan.txt   # bilan 2024
```

The mount table tells the two families apart by the last word of the options:

```text
/etc/auto.autofs-demo        /mnt/autofs-demo        autofs ...,indirect,... 0 0
/etc/auto.autofs-demo-direct /mnt/autofs-demo-direct autofs ...,direct,...   0 0
```

`indirect` for a parent that manufactures its keys, `direct` for a path declared
in full. It is the fastest way to know which kind of map you really wrote.

### The NFS case

On-demand NFS mounting is the historical use of autofs, and the one expected in
RHCSA as well as in LFCS. The configuration is identical, only the **source**
changes: a `server:/export` path.

```bash
echo '/mnt/nfs  /etc/auto.documents  --timeout=120' \
  | sudo tee /etc/auto.master.d/documents.autofs
echo 'documents  -rw,soft  serveur-nfs.exemple:/srv/nfs/documents' \
  | sudo tee /etc/auto.documents
sudo systemctl restart autofs
```

The `soft` option prevents a process from staying blocked indefinitely if the
server disappears; keep it for non-critical data, and keep the `hard` default
for sensitive writes. The NFS client package is required (`nfs-utils` on RHEL
and derivatives, `nfs-common` on Debian and Ubuntu).

> **An NFS server on the local machine does not give you NFS.** If the source
> points at `localhost` or at the name of the machine itself, autofs makes a
> **local bind**: `findmnt` then displays an `xfs` type, the local disk, instead
> of `nfs4`. Really testing an NFS mount requires a **remote** server. This point
> comes from the guide and could not be verified on this VM, which is alone.

### Troubleshooting a mount that does not happen

When an access returns `No such file or directory` with no further explanation,
`journalctl -u autofs` will not help you: on this VM, a failed mount leaves **no
trace** in it, the journal only contains the start and the stop of the service.

The only method that gives the exact cause is the one from the guide: stop the
service and run the daemon **in the foreground, in verbose mode**, then trigger
the access **from another terminal**.

```bash
# terminal 1
sudo systemctl stop autofs
sudo automount -f -v

# terminal 2
ls /mnt/autofs-demo/archives
ls /mnt/autofs-demo/inexistante
```

Terminal 1 then tells you exactly what happens:

```text
mounted indirect on /mnt/autofs-demo with timeout 30, freq 8 seconds
attempting to mount entry /mnt/autofs-demo/archives
mounted /mnt/autofs-demo/archives
attempting to mount entry /mnt/autofs-demo/inexistante
key "inexistante" not found in map source(s).
failed to mount /mnt/autofs-demo/inexistante
```

A key absent from the map and a source that refuses to mount give two distinct
messages. With a nonexistent source:

```text
attempting to mount entry /mnt/autofs-demo/casse
mount(generic): failed to mount /srv/autofs-demo/absent.img (type xfs) on /mnt/autofs-demo/casse
failed to mount /mnt/autofs-demo/casse
```

On the user side, however, the two failures look exactly alike: `No such file or
directory`, with `rc=2`. Hence the value of verbose mode.

Always finish with a `Ctrl+C` on the daemon and a `sudo systemctl start autofs`,
otherwise no automatic mount works on the machine any more.

> **The daemon and the access must come from two different sessions.** Running
> `automount -f -v` in the background then doing the `ls` in the **same** script
> gave, on this VM, a `No such file or directory` on a perfectly valid key, and
> not a single line in the daemon log. The same key mounted without complaint as
> soon as the access came from a second connection. Two terminals, as the guide
> says.

| Symptom | Likely cause |
|---|---|
| The parent point is empty while the map is correct | normal behaviour: only accessing a **key** triggers the mount; add `--ghost` to see the keys |
| `key "…" not found in map source(s)` | the requested key does not exist in the mount map (typo, or missing wildcard) |
| `mount(generic): failed to mount …` | the source is wrong, or the `-fstype=` does not match the real filesystem |
| The mount point does not appear at all in `mount` | the master map was not reread: `systemctl reload autofs` |
| A new mount point stays unreachable | it was added to the **master** map: a reload is mandatory, unlike the keys of a mount map |
| `Permission denied` on a `mkdir` in the parent, even as root | normal: the parent of an indirect map is not writable |
| `findmnt` says "not mounted" then `mount` says "mounted" | `findmnt <path>` triggered the mount; observe through `mount` or `/proc/self/mounts` |
| Type `xfs` instead of `nfs4` on an NFS mount | the source points at the local machine: autofs made a bind |
| Nothing mounts anywhere after a troubleshooting session | `automount -f -v` stayed in the foreground and the service is stopped: `systemctl start autofs` |

### Undoing everything

Removing a mount map is not enough: as long as the master map declares the
point, autofs keeps it armed. So you remove in the reverse order of creation,
then reload.

```bash
sudo rm -f /etc/auto.master.d/autofs-demo.autofs
sudo rm -f /etc/auto.autofs-demo /etc/auto.autofs-demo-coffres \
           /etc/auto.autofs-demo-direct /etc/auto.autofs-demo-tardif
sudo systemctl restart autofs
mount | grep autofs-demo          # must return nothing
sudo rm -rf /srv/autofs-demo
```

The final `restart` is the one that counts, and it does more than you think.
After it, `/mnt` is **entirely empty**:

```text
total 0
drwxr-xr-x.  2 root root   6 Jul 22 13:13 .
dr-xr-xr-x. 20 root root 258 Jul 22 13:13 ..
```

No `rmdir` was needed: autofs removes the directories it had created, since it
created them itself. It also releases the loop devices, which `losetup -a`
confirms before removing the images.
