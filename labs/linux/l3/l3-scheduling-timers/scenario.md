# Context — recurring work, the systemd way

A maintenance job should run regularly. On a systemd host the modern approach is a
**timer unit**: a `.timer` that triggers a `.service`, with logging, dependencies
and `systemctl` management — and it comes back after a reboot.

Your mission, on the VM:

1. Create **`/etc/systemd/system/labbackup.service`** — a `oneshot` service whose
   `ExecStart` runs `touch /run/labbackup.stamp`.
2. Create **`/etc/systemd/system/labbackup.timer`** — a `[Timer]` with an
   `OnCalendar=` schedule (e.g. `*:0/10` every ten minutes), and an `[Install]`
   section `WantedBy=timers.target`.
3. `systemctl daemon-reload`, then **enable and start** it:
   `systemctl enable --now labbackup.timer`.

The point: a timer drives a service on a schedule (`OnCalendar`), `systemctl
list-timers` shows the next run, and being **enabled** is what makes it survive a
reboot — cron's replacement in the systemd world.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/
