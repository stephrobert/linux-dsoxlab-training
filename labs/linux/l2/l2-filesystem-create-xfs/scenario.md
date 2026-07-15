# Context — put a real filesystem on a partition

A blank partition is waiting. A partition is just reserved space until it holds a
**filesystem**. Your job is to format it as **XFS** (the RHEL default, great for
large files and scaling), give it a **label** so it is easy to identify, and
mount it.

Your mission, on the VM:

1. Format the prepared partition as **XFS** with the label **`DATA`**
   (`mkfs.xfs -L DATA <part>`).
2. Create the mount point `/srv/xfs`.
3. **Mount** the filesystem there.

The point: `mkfs.xfs` creates the filesystem and `-L` stamps a label; `blkid`
shows the type and label; a label lets you mount by `LABEL=` instead of a fragile
device name. `lsblk -f` shows the result.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/
