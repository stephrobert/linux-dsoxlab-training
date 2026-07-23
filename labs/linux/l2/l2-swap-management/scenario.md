# Context — Add swap to a memory-tight server

You are the admin on **alma-rhcsa-1.lab**. A batch job occasionally spikes
memory and the kernel OOM killer has already terminated it twice. Until the
job is fixed, you need a **safety valve**: a small swap area that absorbs the
peaks, without letting the box swap aggressively.

Two requirements go together: that valve must still be there on the next boot,
and the kernel must only fall back to it as a last resort.

The full method is in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/
