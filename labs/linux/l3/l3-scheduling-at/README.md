# Lab — one-shot scheduling with at

## Reminder

[**at on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/)

`at` queues a command to run **once** at a later time, handled by `atd`. Feed the
command on stdin: `echo 'cmd' | at <time>`. `atq` lists pending jobs, `at -c <n>`
prints a job's script, `atrm <n>` removes it. Unlike cron, it does not repeat.

## The course

The examples below work in `/tmp/atelier-at` and schedule timestamps or an
`uptime`: the challenge will ask you for another command and another path. The
point is to learn the method, not to copy a line. All the output shown comes
from a fresh AlmaLinux 10, in the UTC time zone.

### The prerequisite everyone forgets: the package, then the service

On a minimal AlmaLinux image, `at` is not there:

```bash
rpm -q at
# package at is not installed
systemctl is-active atd
# inactive
systemctl is-enabled atd
# not-found
```

`not-found` does not mean "disabled": the unit does not exist, because the
package that provides it is absent. Without the binary, the command fails
before there is even any talk of a time (`at: command not found`). So you
install it, and you look at what the installation did exactly:

```bash
sudo dnf -y install at
```

```text
Installing       : at-3.2.5-14.el10_1.x86_64                              1/1
Running scriptlet: at-3.2.5-14.el10_1.x86_64                              1/1
Created symlink '/etc/systemd/system/multi-user.target.wants/atd.service' → '/usr/lib/systemd/system/atd.service'.
```

The package **enabled** `atd` at boot, but did **not** start it:

```bash
systemctl status atd --no-pager
```

```text
○ atd.service - Deferred execution scheduler
     Loaded: loaded (/usr/lib/systemd/system/atd.service; enabled; preset: enabled)
     Active: inactive (dead)
```

`enabled` and `inactive (dead)` at the same time: this is exactly the situation
that loses points, because you read `enabled` and move on. You need both, hence
the `--now`:

```bash
sudo systemctl enable --now atd
systemctl is-active atd
# active
```

The opposite trap exists too. With `atd` stopped, `at` **still accepts** the
job, it only warns that it has nobody to wake up:

```bash
sudo systemctl stop atd
echo '/bin/true' | at now + 2 minutes
```

```text
job 13 at Wed Jul 22 15:51:00 2026
Can't open /run/atd.pid to signal atd. No atd running?
```

The job does appear in `atq`, and yet it will never start as long as the
service is stopped. A non-empty queue therefore proves nothing on its own:
always check the service.

### Queue a command, and watch it leave

That is what really distinguishes `at` from cron: you can watch the job
disappear.

```bash
mkdir -p /tmp/atelier-at
cd /tmp/atelier-at
atq                                   # empty queue: no output
echo 'date -Is >> /tmp/atelier-at/veille.log' | at now + 1 minute
```

```text
warning: commands will be executed using /bin/sh
job 1 at Wed Jul 22 15:47:00 2026
```

The `commands will be executed using /bin/sh` warning is normal: there is
nothing to fix. The number `1` is the job identifier, it is the one you will
give to `at -c` and to `atrm`.

```bash
atq
# 1	Wed Jul 22 15:47:00 2026 a ansible
```

Three pieces of information: the identifier, the scheduled time, then the queue
letter (`a`) and the owner. One minute later:

```bash
cat /tmp/atelier-at/veille.log
# 2026-07-22T15:47:00+00:00
atq
# (nothing left)
at -c 1
# Cannot find jobid 1
```

The job ran **on the scheduled second**, then was removed from the queue. An
`at` job is consumed by its execution: there is nothing to clean up, and
nothing will repeat. That is the whole difference with a crontab entry, which
stays in place until you remove it.

The `atd` journal keeps a trace of it:

```bash
sudo journalctl -u atd --since '10 min ago' --no-pager
```

```text
Jul 22 15:45:55 systemd[1]: Started atd.service - Deferred execution scheduler.
Jul 22 15:47:00 atd[1787]: Starting job 1 (a0000101c5e1b3) for user 'ansible' (1001)
```

This is the first place to look when a job "did nothing": if the `Starting job`
line is absent, the job was not started; if it is there, the problem is in the
command.

### What a job really contains: `at -c`

`at -c <number>` displays the complete script that `atd` will execute. A
surprise on first reading: the command you typed is right at the bottom,
preceded by some thirty lines. Here are its beginning and its end:

```text
#!/bin/sh
# atrun uid=1001 gid=1001
# mail ansible 0
umask 22
SHELL=/bin/bash; export SHELL
PWD=/tmp/atelier-at; export PWD
LOGNAME=ansible; export LOGNAME
HOME=/home/ansible; export HOME
[...]
cd /tmp/atelier\-at || {
	 echo 'Execution directory inaccessible' >&2
	 exit 1
}
${SHELL:-/bin/sh} << 'marcinDELIMITER52285d1c'
date -Is >> /tmp/atelier-at/veille.log
marcinDELIMITER52285d1c
```

The script is 34 lines long for a one-line command. Above all, remember the
`cd` in second-to-last position: `at` recorded the **current directory** of the
submission and moves back into it before executing. If that directory has
disappeared in the meantime, the job stops on `Execution directory
inaccessible` without running your command.

It is also `at -c` that lets you prove that a queued job really schedules what
you think, without waiting for its time.

### The environment is frozen at submission, not at execution

All those `VAR=...; export VAR` lines at the top of the script are a copy of
your environment **at the moment you typed the command**. They are not read
again later. The demonstration fits in four lines:

```bash
export ETIQUETTE=avant-soumission
echo 'echo $ETIQUETTE > /tmp/atelier-at/etiquette.txt' | at now + 1 minute
export ETIQUETTE=change-apres-coup
```

One minute later, the session says `change-apres-coup`, and the file written by
the job says:

```bash
cat /tmp/atelier-at/etiquette.txt
# avant-soumission
```

A homemade variable is therefore passed on, which `at -c 12` confirms at the
top of the script (`ETIQUETTE=avant-soumission; export ETIQUETTE`), next to the
`PWD=/tmp/atelier-at` already seen. A practical consequence, valid both ways:

- what your session sees, the job will see (variables, `PATH`, `HOME`, current
  directory);
- what your session does **not** see at the moment of the `at`, the job will
  never see, even if you define it thirty seconds later.

A job submitted from a particular environment (an enriched `PATH`, a `source`
of an environment file) will therefore not be reproducible elsewhere. Hence the
reflex from the guide: **absolute paths** in the scheduled command, and a
script tested separately rather than a complicated one-liner typed live.

### Writing the time: what goes through, what traps you

The accepted formats are measured, not guessed. All the lines below were
submitted on a **Wednesday 22 July at 15:46**:

| What you type | What `at` answers |
|---|---|
| `now + 5 minutes` | `job 2 at Wed Jul 22 15:51:00 2026` |
| `teatime` | `job 3 at Wed Jul 22 16:00:00 2026` |
| `midnight` | `job 4 at Thu Jul 23 00:00:00 2026` |
| `9:00` | `job 5 at Thu Jul 23 09:00:00 2026` |
| `10:30 tomorrow` | `job 6 at Thu Jul 23 10:30:00 2026` |
| `10:30 08152026` | `job 8 at Sat Aug 15 10:30:00 2026` |

**`teatime` is 16:00**, and `midnight` moves to the next day. These keywords are
handy in an exam, but read carefully the date `at` returns to you: that is what
counts, not your intuition.

**A time already past today is postponed to tomorrow, without a word.** It was
15:46, `at 9:00` answered `Thu Jul 23 09:00:00`. The job is accepted, it leaves
the next day. Nobody warns you: if you wanted this morning, you missed it and
you will only know afterwards. Always check the returned date.

**An instant really in the past, on the other hand, is refused**:

```bash
echo '/bin/true' | at now - 1 hour
# at: refusing to create job destined in the past
```

As for dates, the short four-digit format does not do what you think:

```bash
echo '/bin/true' | at 0815
# job 7 at Thu Jul 23 08:15:00 2026
```

`0815` was not read as 15 August but as **08:15**. The compact day/month format
requires the year:

```bash
echo '/bin/true' | at 10:30 0815
# syntax error. Last token seen: 0815
# Garbled time
```

`Garbled time` is the generic refusal message, preceded by a line that tells
where the parsing failed. Another example with an impossible time:

```bash
echo '/bin/true' | at 25:00
# Problem in hours specification. Last token seen: 25:00
# Garbled time
```

These two refusals return exit code `1` and **create no job**.
The following three forms, on the other hand, all designate the same instant:
`10:30 08152026`, `10:30 Aug 15` and `10:30 15.08.2026`.

Finally, `at -f <file>` schedules the content of a script instead of reading
standard input, which the guide recommends as soon as the command goes beyond
one line:

```bash
printf '%s\n' '/usr/bin/uptime >> /tmp/atelier-at/uptime.log' > /tmp/atelier-at/tache.sh
at -f /tmp/atelier-at/tache.sh now + 5 minutes   # job 14 at Wed Jul 22 15:54:00 2026
```

### Inspect the queue and cancel: `atq` and `atrm`

`atq` and `at -l` are the same command, `atrm` and `at -r` too. The queue is
**per user**: everyone sees only their own jobs, `root` sees them all. After
submitting a job with `sudo`:

```bash
atq | tail -2
# 13	Wed Jul 22 15:51:00 2026 a ansible
# 14	Wed Jul 22 15:54:00 2026 a ansible

sudo atq | tail -2
# 14	Wed Jul 22 15:54:00 2026 a ansible
# 15	Wed Jul 22 16:19:00 2026 a root
```

Job `15`, submitted as root, is invisible from the ordinary account. If you are
looking for a job you cannot find, first ask yourself under which account it
was created.

Deletion takes one or more numbers (`atrm 4`). To empty your whole queue in one
go, you take the first column:

```bash
for j in $(atq | cut -f1); do atrm "$j"; done
atq                  # no output: the queue is empty
```

Careful, the loop above only empties **your** queue. The jobs of `root` require
`sudo atq` and `sudo atrm`.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `at: command not found` | package absent | `rpm -q at`, then `sudo dnf -y install at` |
| `systemctl is-enabled atd` answers `not-found` | the unit does not exist, the package is missing | install `at` |
| `Can't open /run/atd.pid to signal atd` | `atd` is stopped (the job is queued all the same) | `sudo systemctl enable --now atd` |
| `atd` `enabled` but job never started | enabled at boot, not started | `systemctl is-active atd` |
| `Garbled time` | time format not recognised | read the `Last token seen:` of the previous line |
| `at: refusing to create job destined in the past` | instant earlier than now | aim at the future |
| Job started one day too late | time already past today, postponed silently | reread the date returned by `at` |
| `Cannot find jobid <n>` | job already executed or deleted | `atq`; an `at` job does not survive its execution |
| `Execution directory inaccessible` | the current directory of the submission has disappeared | `at -c <n>` to see the recorded `cd` |
| Job executed but no visible output | the output leaves by email, not into a terminal | redirect into a file |
| `You do not have permission` | `at.allow` / `at.deny` policy | `sudo cat /etc/at.allow /etc/at.deny` |

The second-to-last point deserves a measurement. A job that writes on standard
output sees that text sent by email to its owner; on a machine without a
transport agent, it is simply lost. After
`echo 'echo bonjour-depuis-la-tache' | at now + 1 minute`, the journal gives:

```text
Jul 22 15:50:00 atd[2067]: Starting job 16 (a0001001c5e1b6) for user 'ansible' (1001)
Jul 22 15:50:00 atd[2070]: Exec failed for mail command: No such file or directory
```

The job did run, its output no longer exists anywhere. Hence the good practice
from the guide: log explicitly, for example
`>> /tmp/atelier-at/tache.log 2>&1`, rather than counting on the email.

To undo everything and start again from scratch:

```bash
for j in $(atq | cut -f1); do atrm "$j"; done
sudo sh -c 'for j in $(atq | cut -f1); do atrm "$j"; done'
rm -rf /tmp/atelier-at
```
