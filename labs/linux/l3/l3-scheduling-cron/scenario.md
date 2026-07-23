# Context — run a job on a schedule

A reporting script (`/usr/local/bin/report.sh`) must run **every day at 02:30**,
unattended. Nobody is going to launch it by hand — that is what **cron** is for.

The point: a cron line describes *when* first, through several time fields, then
*what*. Its exact shape is not the same depending on whether it lives in a user's
crontab or in a system file.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/
