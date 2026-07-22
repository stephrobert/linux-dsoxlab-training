# Context — make the batch job get out of the way

A background worker (`labworker.service`) runs flat out at normal priority and
makes the box feel sluggish for everyone else. Give it a **nice value of 10** so
the scheduler lets interactive work go first — and make that stick across
restarts.

Your mission, on the VM:

1. Set the service's scheduling priority to **nice `10`** (higher nice = lower
   priority) via the unit — ideally a drop-in (`systemctl edit labworker`).
2. Reload and restart so the running process actually gets the new priority.

The point: `nice` sets a process's starting priority, `renice` changes a running
one, and signals (`kill -TERM`, `-HUP`, `-9`) control processes. For a service,
the durable way is `Nice=` in the unit. `ps -o ni -p <pid>` shows the live value.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/
