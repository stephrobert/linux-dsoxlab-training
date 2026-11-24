# Run a job on a schedule

## The situation

A reporting script (`/usr/local/bin/report.sh`) must run **every day at 02:30**,
unattended. Nobody is going to launch it by hand — that is what **cron** is for.

The point: a cron line describes *when* first, through several time fields, then
*what*. Its exact shape is not the same depending on whether it lives in a user's
crontab or in a system file.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/scheduling/cron/

## What is asked

### Mission

Schedule `/usr/local/bin/report.sh` to run every day at 02:30.

### Goal (expected state)

1. A cron entry launches `report.sh`.
2. The schedule is **daily at 02:30** (`30 2 * * *`).

### Constraints

- Any valid cron mechanism (`/etc/cron.d/`, `/etc/crontab`,
  `crontab -e`). Validation reads the **actual schedule**, not the command.

### Validation

```bash
dsoxlab check l3-scheduling-cron
```
