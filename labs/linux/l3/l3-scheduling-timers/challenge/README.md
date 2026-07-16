# Challenge — l3-scheduling-timers

## Mission

Schedule a recurring job with a systemd timer (`labbackup`).

## Goal (expected state)

1. `/etc/systemd/system/labbackup.service` and `labbackup.timer` exist.
2. The timer has an `OnCalendar=` schedule.
3. `labbackup.timer` is enabled and active (`systemctl is-enabled/is-active`).

## Constraints

- Use a systemd timer (not cron/at). `daemon-reload` after creating the units.
- Validation reads the unit files and the timer's enabled/active state.

## Validation

```bash
dsoxlab check l3-scheduling-timers
```
