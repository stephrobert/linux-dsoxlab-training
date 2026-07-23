# Context — put a real filesystem on a partition

A blank partition is waiting. A partition is just reserved space until it holds a
**filesystem**. Your job is to format it as **XFS** (the RHEL default, great for
large files and scaling), give it a **label** so it is easy to identify, and
mount it.

The point: a label is a tag carried by the filesystem itself. It lets you refer
to that filesystem by a stable name instead of a fragile device name that can
change from one boot to the next.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/
