# Context — the disk is full

An alert fires: writes to `/srv/data` fail, "No space left on device". A
filesystem there is nearly full. Your job is the everyday ops reflex: find what
is eating the space and reclaim it — **without** deleting the data that matters.

Your mission, on the VM:

1. Confirm which filesystem is full (`df -h`).
2. Find the biggest consumer under it (`du -h --max-depth=1 /srv/data`, then dig).
3. Remove the junk (a bloated cache) so `/srv/data` drops **below 50%** used.
4. Keep the legitimate file `/srv/data/app.log`.

The point: `df` shows filesystem usage, `du` attributes it to directories. A
classic gotcha (RHCSA): if `df` says full but `du` finds nothing, a process is
still holding a **deleted-but-open** file — `lsof +L1` reveals it, and freeing it
needs the process to release it. Here the culprit is on disk, so `du` will find
it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/
