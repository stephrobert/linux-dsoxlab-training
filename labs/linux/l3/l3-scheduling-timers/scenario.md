# Context — recurring work, the systemd way

A maintenance job should run regularly. On a systemd host the modern approach is a
**timer unit**: a `.timer` that triggers a `.service`, with logging, dependencies
and `systemctl` management — and it comes back after a reboot.

The point: the work to do and the moment it fires are described in two separate
units, the second one carrying the schedule. And like any systemd unit, a timer
only comes back after a reboot if it was enabled to do so.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/
