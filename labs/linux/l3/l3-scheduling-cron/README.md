# Lab — schedule a job with cron

> Prepare: `dsoxlab provision` then `dsoxlab run l3-scheduling-cron`

## Recap

[**cron on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/)

A cron line has five time fields — `minute hour day-of-month month day-of-week` —
then the command (system files in `/etc/cron.d/` and `/etc/crontab` add a user
field before the command). `30 2 * * *` is 02:30 daily. `crontab -e/-l` manages a
user's table; `/etc/cron.d/` holds system jobs. The `crond` service must run.

## Objectives

- `/usr/local/bin/report.sh` scheduled **daily at 02:30** (`30 2 * * *`);
- via any real cron mechanism.

## Validate

```bash
dsoxlab check l3-scheduling-cron
```
