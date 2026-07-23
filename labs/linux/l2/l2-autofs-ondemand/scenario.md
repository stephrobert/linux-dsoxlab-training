# Context — mount only when needed

Some filesystems shouldn't stay mounted all the time — a rarely-used disk, a
network share. **autofs** mounts them **on access** and unmounts them after an
idle timeout, saving resources and avoiding stale mounts. Here the spare disk
holds an XFS filesystem; wire it up so that touching `/autofs/data` mounts it.

The point: autofs mounts nothing until the path is actually used, and unmounts on
its own once nobody needs it. It still has to be told what to mount, and under
which path.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/
