# Context — mount only when needed

Some filesystems shouldn't stay mounted all the time — a rarely-used disk, a
network share. **autofs** mounts them **on access** and unmounts them after an
idle timeout, saving resources and avoiding stale mounts. Here the spare disk
holds an XFS filesystem; wire it up so that touching `/autofs/data` mounts it.

Your mission, on the VM:

1. In a **master map** (`/etc/auto.master.d/lab.autofs`), attach `/autofs` to a
   mount map (`/etc/auto.lab`).
2. In the **mount map** (`/etc/auto.lab`), declare the key `data` as an XFS mount
   of the spare partition (its path is in `/root/autofs-disk.env`).
3. Enable and start **autofs**.
4. Access `/autofs/data` — it must mount automatically and expose `marker.txt`.

The point: autofs never mounts until the key is accessed; the master map says
*where*, the mount map says *what*, and `--timeout` controls auto-unmount.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/
