# Context — run something once, later

Cron repeats a job on a schedule. But sometimes you want a command to run
**once**, at a specific time, and never again — a maintenance action tonight, a
reminder in an hour. That's what **`at`** is for.

Your mission, on the VM:

1. Schedule the command **`touch /run/rapport.done`** to run **once, in the
   future** (for example `at now + 1 hour`, or a precise time like `at 23:00`).
   Pipe the command in: `echo 'touch /run/rapport.done' | at now + 1 hour`.
2. Confirm it is queued with **`atq`**, and inspect its content with
   **`at -c <jobnumber>`**.

The point: `at` reads the command from standard input and queues a **one-shot**
job handled by `atd`; `atq` lists pending jobs, `at -c` prints a job's script, and
`atrm` removes one. Unlike cron, it does not repeat.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/
