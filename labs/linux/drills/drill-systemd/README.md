# Drill — systemd, timers and scheduling

**5 tasks, 100 points, 25 minutes. No hints.** Shared between RHCSA and LFCS:
systemd behaves identically on AlmaLinux and on Ubuntu, so you pick whichever
target suits you.

## What a drill is

A drill is not a lab. There is no course here, and that is deliberate: you are
in exam conditions. You are given a statement, a timer and a machine, and you
must recall on your own the steps you have already practised.

The difference with a lab comes down to three points:

- **no hint is available**, not even for points;
- **time counts**: 25 minutes for five tasks is the exam pace, not the learning
  pace;
- **the tasks are independent**. If one resists, move on to the next and come
  back to it: an untouched task costs less than a timer burnt on the first one.

The pass mark is set at **70 points out of 100**.

## What you need to know before attempting it

The thread of this drill is the gap between the file you write and the state
systemd keeps. If one of the subjects below is not familiar, play the matching
lab **first**: there you will find the course, the hints and the right to be
wrong that the drill will not give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| Write a service unit, load it, enable it and start it | `l3-service-create-unit` |
| Restart policy, and reading why a service goes down | `l3-service-diagnose` |
| `OnCalendar` timer, and the timer plus service pair | `l3-scheduling-timers` |
| A user's cron table and the five-field syntax | `l3-scheduling-cron` |
| Finding a past run in the journal | `l3-journald-persist` |
| Default boot target, and the symbolic link it really is | `l3-boot-target` |

A single subject of the drill has no lab anywhere: **permanently masking a
service**. Revise it in the guide before starting, keeping in mind the
difference between disabling and masking.

## Getting into exam conditions

Start the timer before opening the statement, not after. Twenty-five minutes go
fast, and the first exam reflex is to **read the five tasks first** to spot
those that take a single command.

Three habits specific to systemd:

- **check with `systemctl show`, not by re-reading your file**. Re-reading what
  you have just written proves nothing: systemd only reads the disk on reload,
  and it applies overrides on top that your file does not show. `systemctl cat`
  shows the effective unit, overrides included, and `systemctl show -p
  <Property>` gives the value systemd really keeps. That is the value being
  marked;
- **`enabled` and `active` are two distinct states**. A service can run without
  being enabled at boot, or the other way round. Always check both, with
  `systemctl is-enabled` and `systemctl is-active`, before considering a task
  finished. For a timer, `systemctl list-timers` adds the next due time, which
  also tells you whether your calendar expression is understood correctly;
- **forgetting to reload the daemon skews everything else**. A new or modified
  file that has not been taken into account gives inconsistent messages, and
  you will lose more time suspecting your syntax than typing the command.
  `systemd-analyze verify` on your unit also catches section and directive
  mistakes.

For the scheduling part, remember that the name of the cron service is not the
same everywhere: it is the user's table that matters, and it is read back with
`crontab -l -u <user>`, never by opening a file by hand.

## Afterwards

The correction does not only say how many points you got: it says **which
task** failed and **what the system contained** at check time. Read it before
replaying.

A drill can be replayed. The second attempt is there to measure what you have
retained from your mistakes, not to memorise answers: the exact values matter
less than the actions, which transpose to any statement.
