# Lab — recurring scheduling with a systemd timer

## Reminder

[**systemd timers on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/)

A `.timer` unit triggers a `.service` on a schedule. The service is often
`Type=oneshot`; the `[Timer]` has `OnCalendar=` and its `[Install]` has
`WantedBy=timers.target`. `systemctl daemon-reload` picks up new units;
`enable --now` starts it and makes it persistent. `systemctl list-timers` shows
the next run.

## The course

The examples below build a timer named `releve-charge`, which writes the system
load into `/var/tmp/releve-charge.log`: the challenge will ask you for another
unit name, another job and another schedule. The point is to learn the method and
to know how to prove that the timer runs, not to copy a line. Every output comes
from an **AlmaLinux 10** VM running **systemd 257**.

### Check the schedule before writing the unit

`systemd-analyze calendar` takes an `OnCalendar=` expression, normalises it and
computes the **next occurrence**. It is the first move, even before creating a
unit file.

```bash
systemd-analyze calendar 'Mon..Fri *-*-* 08:00'
```

```text
  Original form: Mon..Fri *-*-* 08:00
Normalized form: Mon..Fri *-*-* 08:00:00
    Next elapse: Thu 2026-07-23 08:00:00 UTC
       From now: 16h left
```

The `--iterations=3` option adds the following occurrences, which checks the
**rhythm** and not only the first trigger. A few useful expressions, all run
through the tool:

| Expression | Normalized form | Meaning |
|---|---|---|
| `daily` | `*-*-* 00:00:00` | every day at midnight |
| `hourly` | `*-*-* *:00:00` | at the start of every hour |
| `Sat *-*-* 22:00:00` | identical | every Saturday at 22:00 |
| `*:*:0/30` | `*-*-* *:*:00/30` | every 30 seconds |

**The time zone is not a detail**: `Next elapse` is expressed in the machine's
zone, not in yours. `timedatectl` answers here `Time zone: UTC (UTC, +0000)`: an
`OnCalendar=*-*-* 03:00:00` therefore fires at 03:00 UTC, that is 05:00 in French
summer time. The guide, written on a machine in `CEST`, shows an extra `(in
UTC):` line in the output of `systemd-analyze calendar`: it does **not** appear
here, precisely because local time is already UTC. If the machine's zone does not
suit you, `OnCalendar` accepts an explicit one at the end of the expression, and
the computation follows:

```text
$ systemd-analyze calendar '*-*-* 03:00:00 Europe/Paris'
Normalized form: *-*-* 03:00:00 Europe/Paris
    Next elapse: Thu 2026-07-23 01:00:00 UTC
```

Finally, the tool **refuses** what it does not understand, and that is its whole
point. The classic trap is to write cron syntax in an `OnCalendar`:

```text
$ systemd-analyze calendar '*/15 * * * *'
Failed to parse calendar specification '*/15 * * * *': Invalid argument
```

The exit code is then `1`. Same refusal for a weekday written in French
(`Lun *-*-* 06:00:00`) or an impossible time (`*-*-* 25:00:00`).

### The `.service` + `.timer` pair

Two files in `/etc/systemd/system/`. First the **work to be done**, a `oneshot`
service: it starts, does its task, ends.

```ini
# /etc/systemd/system/releve-charge.service
[Unit]
Description=Releve de la charge systeme

[Service]
Type=oneshot
ExecStart=/usr/local/bin/releve-charge.sh
```

The script, in `0755`:

```bash
#!/usr/bin/bash
set -euo pipefail
printf "%s charge=%s\n" "$(date -Is)" "$(cut -d' ' -f1-3 /proc/loadavg)" >> /var/tmp/releve-charge.log
echo "releve ajoute a /var/tmp/releve-charge.log"
```

Then the **schedule**, in a unit with the same base name:

```ini
# /etc/systemd/system/releve-charge.timer
[Unit]
Description=Declenche le releve de charge toutes les 30 secondes

[Timer]
OnCalendar=*:*:0/30

[Install]
WantedBy=timers.target
```

`releve-charge.timer` triggers `releve-charge.service` by plain **naming
convention**: nothing else links them. To break that convention, you need a
`Unit=` directive in the `[Timer]` section.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now releve-charge.timer
```

```text
Created symlink '/etc/systemd/system/timers.target.wants/releve-charge.timer' → '/etc/systemd/system/releve-charge.timer'.
```

It is the **timer** you enable, never the service. The service has no `[Install]`
section, so there is nothing to enable:

```text
$ systemctl is-enabled releve-charge.service releve-charge.timer
static
enabled
```

`static` means "loadable, but not enableable". Trying
`systemctl enable releve-charge.service` returns a long warning
(`The unit files have no installation config...`) without doing anything. That is
not a configuration flaw: it is the normal behaviour of a service driven by a
timer.

### See it fire

A declared timer has proved nothing. `systemctl list-timers` gives the next and
the last run:

```text
$ systemctl list-timers releve-charge.timer
NEXT                        LEFT LAST                        PASSED UNIT                ACTIVATES
Wed 2026-07-22 15:14:00 UTC  18s Wed 2026-07-22 15:13:34 UTC 7s ago releve-charge.timer releve-charge.service
```

> Without an argument, `systemctl list-timers` only shows **active** timers. Add
> `--all` to also see those that are loaded but inactive: that is where you find
> a timer that refuses to start.

The **service**'s journal shows every trigger. `-o short-precise` displays
milliseconds, which will be useful in the next section:

```text
$ journalctl -u releve-charge.service --since '-3min' -o short-precise
Jul 22 15:12:32.142488 atelier systemd[1]: Starting releve-charge.service...
Jul 22 15:12:32.154136 atelier releve-charge.sh[20009]: releve ajoute a /var/tmp/releve-charge.log
Jul 22 15:12:32.155840 atelier systemd[1]: Finished releve-charge.service...
[...]
Jul 22 15:13:34.504436 atelier systemd[1]: Starting releve-charge.service...
Jul 22 15:13:34.513676 atelier releve-charge.sh[20030]: releve ajoute a /var/tmp/releve-charge.log
```

The script's `echo` lands in the journal without anything being redirected: a
service's standard output goes to journald. That is what cron does not do. And
the result produced, the only proof that really counts:

```text
2026-07-22T15:12:32+00:00 charge=0.00 0.00 0.00
2026-07-22T15:13:06+00:00 charge=0.00 0.00 0.00
2026-07-22T15:13:34+00:00 charge=0.00 0.00 0.00
```

### What cron cannot do

**`AccuracySec`, or why the timer starts late.** Read the timestamps above again:
the schedule asked for 15:12:30, 15:13:00 and 15:13:30, the service started at
15:12:32, 15:13:06 and 15:13:34. Between 2 and 6 seconds late, never the same.
That is not a clock drift, it is a setting:

```text
$ systemctl show releve-charge.timer -p AccuracyUSec -p RandomizedDelayUSec -p Persistent
AccuracyUSec=1min
RandomizedDelayUSec=0
Persistent=no
```

By default, systemd gives itself **one minute** of latitude to group wake-ups and
save the processor. By adding `AccuracySec=1s` to the `[Timer]`, then
`daemon-reload` and `restart`, the triggers fall back on the second (15:14:00.226,
15:14:30.226, 15:15:00.226). That is what throws people off when coming from
cron, which starts on the exact minute.

**`RandomizedDelaySec`, to spread the triggers out.** With
`RandomizedDelaySec=5s` on the same timer, three runs scheduled at 15:16:30,
15:17:00 and 15:17:30 started at 15:16:31.2, 15:17:02.0 and 15:17:34.2: a random
offset, different every time. On a fleet of machines that all wake up at 03:00,
this is what keeps the backup server from collapsing.

**`Persistent=true`, to catch up a missed occurrence.** The mechanism relies on a
timestamp file under `/var/lib/systemd/timers/`, created as soon as the timer
starts:

```text
$ sudo ls -l /var/lib/systemd/timers/
-rw-r--r--. 1 root root 0 Jul 22 13:50 stamp-logrotate.timer
-rw-r--r--. 1 root root 0 Jul 22 15:16 stamp-releve-charge.timer
```

The file is **0 bytes**: the date of the last trigger is carried by its `mtime`,
not by its content. When the timer starts, systemd compares that date to the
schedule; if an occurrence is missing, it fires immediately. You can observe it
without rebooting the machine, by moving the timestamp back. With a timer in
`OnCalendar=daily` and `Persistent=true`:

```bash
sudo systemctl stop releve-charge.timer
sudo touch -d '2 days ago' /var/lib/systemd/timers/stamp-releve-charge.timer
sudo systemctl start releve-charge.timer      # it is 15:20:31
```

```text
Jul 22 15:20:31.118653 atelier systemd[1]: Starting releve-charge.service...
Jul 22 15:20:31.124488 atelier systemd[1]: Finished releve-charge.service...
```

The service starts **at the very moment of the `start`**, while the next planned
occurrence is midnight. Without `Persistent=true`, the same manipulation fires
nothing and the timestamp is not even read back: its `mtime` stays two days
behind, and the service quietly waits for midnight.

> The catch-up **at machine startup** was not observed here, for lack of being
> able to reboot the workshop VM. What is verified is the mechanism: the
> timestamp on disk, its comparison to the schedule when the timer is activated,
> and the immediate trigger that follows. At boot, systemd applies that same
> logic.

### When the service fails

Let us break the script so that it writes into a directory that does not exist.
Unexpected result:

```text
     Active: inactive (dead) since Wed 2026-07-22 15:18:31 UTC
    Process: 20373 ExecStart=/usr/local/bin/releve-charge.sh (code=exited, status=0/SUCCESS)

Jul 22 15:18:31 atelier releve-charge.sh[20373]: /usr/local/bin/releve-charge.sh: line 2: /srv/archives/releve-charge.log: No such file or directory
Jul 22 15:18:31 atelier systemd[1]: Finished releve-charge.service...
```

**`SUCCESS`, although nothing was written.** systemd only judges the process exit
code, and a shell script returns that of its **last** command: here the `echo`,
which succeeded. With `set -euo pipefail` at the top of the script, the first
failing command stops everything and the verdict changes:

```text
× releve-charge.service - Releve de la charge systeme
     Active: failed (Result: exit-code) since Wed 2026-07-22 15:19:33 UTC
    Process: 20423 ExecStart=/usr/local/bin/releve-charge.sh (code=exited, status=1/FAILURE)
```

The unit stays marked as failed until you tell it otherwise, and therefore ends
up in an inventory you can consult:

```text
$ systemctl list-units --failed
● releve-charge.service loaded failed failed Releve de la charge systeme
```

That is the whole difference with cron, which posts an email nobody reads. Once
the cause is fixed, `sudo systemctl reset-failed releve-charge.service` clears
the mark.

**An invalid schedule, on the other hand, does not behave the way theory says.**
On systemd 257, a faulty `OnCalendar` is not silent: `enable --now` fails and the
timer refuses to start.

```text
Failed to start essai-syntaxe.timer: Unit essai-syntaxe.timer has a bad unit file setting.
     Loaded: bad-setting (Reason: Unit essai-syntaxe.timer has a bad unit file setting.)
    Trigger: n/a
```

The silence comes back, however, as soon as **at least one** valid schedule
remains: the faulty line is ignored, the timer starts normally, and only
`systemd-analyze verify` reports it.

```text
$ systemd-analyze verify essai-syntaxe.timer
/etc/systemd/system/essai-syntaxe.timer:6: Failed to parse calendar specification, ignoring: Lun *-*-* 06:00:00
```

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| The timer does not appear in `list-timers` | it is not active; look for it with `--all` |
| `Loaded: bad-setting` | the timer's only `OnCalendar` is invalid, systemd refuses the unit |
| The timer runs but a schedule seems ignored | one faulty `OnCalendar` line among others: `systemd-analyze verify` |
| The unit does not exist after creating the file | `systemctl daemon-reload` forgotten |
| The service starts a few seconds late | `AccuracySec` (one minute by default) or `RandomizedDelaySec` |
| The service starts at an unexpected time | the machine's zone: `timedatectl`, or an explicit zone in `OnCalendar` |
| `status=0/SUCCESS` although the job failed | the script hides the error; add `set -euo pipefail` |
| `Active: failed` | read `journalctl -u <name>.service`, fix, then `systemctl reset-failed` |
| Nothing is caught up after a machine shutdown | `Persistent=true` missing from the `[Timer]` |
| `systemctl enable <name>.service` protests | normal: the service is `static`, you enable the **timer** |

To test the job without waiting for the scheduled time, `sudo systemctl start
releve-charge.service` starts the service directly, without going through the
timer.

### Undoing everything

A forgotten timer keeps firing. Complete removal takes four moves, in this order:

```bash
sudo systemctl disable --now releve-charge.timer
sudo rm -f /etc/systemd/system/releve-charge.timer /etc/systemd/system/releve-charge.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

`disable --now` stops the timer **and** removes the symbolic link in
`timers.target.wants/`, which an `rm` alone would not do. Two checks remain, and
they really must be done: `systemctl list-timers --all` and
`systemctl list-units --failed`. The `stamp-<name>.timer` file under
`/var/lib/systemd/timers/` survives the deletion of the unit: it gets in nobody's
way, but you may as well remove it to start from a clean state.
