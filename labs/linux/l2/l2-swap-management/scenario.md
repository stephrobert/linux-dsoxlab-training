# Context — Add swap to a memory-tight server

You are the admin on **alma-rhcsa-1.lab**. A batch job occasionally spikes
memory and the kernel OOM killer has already terminated it twice. Until the
job is fixed, you need a **safety valve**: a small swap area that absorbs the
peaks, without letting the box swap aggressively.

Your mission:

1. Add a **256 MiB swap file**, secured (`0600`) and active.
2. Make it **survive a reboot** through `/etc/fstab`.
3. Tune **`vm.swappiness = 10`** so swap is used only as a last resort.

The full method is in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/
