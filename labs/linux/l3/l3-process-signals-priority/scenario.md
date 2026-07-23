# Context — make the batch job get out of the way

A background worker (`labworker.service`) runs flat out at normal priority and
makes the box feel sluggish for everyone else. Give it a **nice value of 10** so
the scheduler lets interactive work go first — and make that stick across
restarts.

The point: a process's priority is set when it starts, and can be corrected on
the fly on a process already running. But a systemd-managed service starts over
from its definition on every restart: an on-the-fly correction does not survive
it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/
