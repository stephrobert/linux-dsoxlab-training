# Recurring work, the systemd way

## The situation

A maintenance job should run regularly. On a systemd host the modern approach is a
**timer unit**: a `.timer` that triggers a `.service`, with logging, dependencies
and `systemctl` management — and it comes back after a reboot.

The point: the work to do and the moment it fires are described in two separate
units, the second one carrying the schedule. And like any systemd unit, a timer
only comes back after a reboot if it was enabled to do so.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/scheduling/timers/

## What is asked

### Mission

Schedule a recurring job with a systemd timer (`labbackup`).

### Goal (expected state)

1. `/etc/systemd/system/labbackup.service` and `labbackup.timer` exist.
2. The timer has an `OnCalendar=` schedule.
3. `labbackup.timer` is enabled and active (`systemctl is-enabled/is-active`).

### Constraints

- Use a systemd timer (not cron/at). `daemon-reload` after creating the units.
- Validation reads the unit files and the timer's enabled/active state.

### Validation

```bash
dsoxlab check l3-scheduling-timers
```
