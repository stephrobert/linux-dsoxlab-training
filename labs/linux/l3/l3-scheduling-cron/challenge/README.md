# Challenge — l3-scheduling-cron

## Mission

Schedule `/usr/local/bin/report.sh` to run every day at 02:30.

## Goal (expected state)

1. A cron entry launches `report.sh`.
2. The schedule is **daily at 02:30** (`30 2 * * *`).

## Constraints

- Any valid cron mechanism (`/etc/cron.d/`, `/etc/crontab`,
  `crontab -e`). Validation reads the **actual schedule**, not the command.

## Validation

```bash
dsoxlab check l3-scheduling-cron
```
