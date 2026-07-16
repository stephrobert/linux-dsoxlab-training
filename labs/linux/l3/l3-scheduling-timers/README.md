# Lab — recurring scheduling with a systemd timer

> Prepare: `dsoxlab provision` then `dsoxlab run l3-scheduling-timers`

## Recap

[**systemd timers on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/)

A `.timer` unit triggers a `.service` on a schedule. The service is usually
`Type=oneshot`; the timer's `[Timer]` has `OnCalendar=` and its `[Install]` has
`WantedBy=timers.target`. `systemctl daemon-reload` picks up new unit files;
`enable --now` starts it and makes it persistent. `systemctl list-timers` shows
the next run.

## Objectives

- `labbackup.service` and `labbackup.timer` exist under `/etc/systemd/system/`;
- the timer has an `OnCalendar=` schedule;
- `labbackup.timer` is enabled and active.

## Validate

```bash
dsoxlab check l3-scheduling-timers
```
