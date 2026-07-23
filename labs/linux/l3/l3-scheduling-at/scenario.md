# Context — run something once, later

Cron repeats a job on a schedule. But sometimes you want a command to run
**once**, at a specific time, and never again — a maintenance action tonight, a
reminder in an hour. That's what **`at`** is for.

The point: a one-shot job is put in a queue, then handed to a daemon that will
run it at the stated time and forget it. Unlike cron it does not repeat, and
nothing runs at all if that daemon is not running.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/
