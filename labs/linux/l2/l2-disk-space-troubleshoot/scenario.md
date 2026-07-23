# Context — the disk is full

An alert fires: writes to `/srv/data` fail, "No space left on device". A
filesystem there is nearly full. Your job is the everyday ops reflex: find what
is eating the space and reclaim it — **without** deleting the data that matters.

The point: measuring how full a filesystem is and attributing that usage to the
directories causing it are two different moves. A classic gotcha (RHCSA): when
the two measurements disagree, a process is still holding a deleted-but-open
file, and the space only comes back when it lets go. Here, rest assured, the
culprit really is a file sitting on disk.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/
