# Context — run a job on a schedule

A reporting script (`/usr/local/bin/report.sh`) must run **every day at 02:30**,
unattended. Nobody is going to launch it by hand — that is what **cron** is for.

Your mission, on the VM:

1. Schedule `/usr/local/bin/report.sh` to run **daily at 02:30**
   (minute `30`, hour `2`).
2. Use a real cron mechanism — a system entry in `/etc/cron.d/`, `/etc/crontab`,
   or a user crontab (`crontab -e`).

The point: a cron line is five time fields — `minute hour day-of-month month
day-of-week` — then (for system files) a user, then the command. `30 2 * * *`
means 02:30 every day. `crontab -l` and the files under `/etc/cron.d/` show what
is scheduled.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/
