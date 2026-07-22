# Drill — users, groups and delegation

**5 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS.

## What a drill is

A drill is not a lab. There is no course here, and that is deliberate: you are in
exam conditions. You are given a task list, a stopwatch and a machine, and you
have to recall on your own gestures you have already practised.

The difference with a lab comes down to three points:

- **no hint is available**, not even in exchange for points;
- **time counts**: 20 minutes for five tasks is the pace of the exam, not that of
  learning;
- **the tasks are independent**. If one resists, move on to the next and come
  back to it: an untouched task costs less than a stopwatch run down on the
  first one.

The passing score is set at **70 points out of 100**.

## What you need to know before attempting it

This drill revises five subjects. If one of them is not familiar to you, play the
matching lab **first**: there you will find the course, the hints and the right to
make mistakes that the drill will not give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| Creating an account with imposed attributes, deleting it cleanly | `l2-user-lifecycle` |
| Password ageing and account expiry | `l2-password-policy` |
| Shared directory, set-GID bit, collective permissions | `l2-collaborative-setgid` |
| Delegating sudo as narrowly as possible, without giving all rights | `l2-sudo-delegation` |
| Reading and setting Unix permissions | `l1-permissions-ugo` |

## Getting into exam conditions

Start the stopwatch before opening the task list, not after. Twenty minutes go by
quickly, and the first exam reflex is to **read the five tasks first** to spot
those that can be handled with a single command.

Two habits that earn points, on this drill as in the exam:

- **check each task right after doing it**, with the command that reads the state
  of the system and not your memory (`id`, `getent`, `chage -l`, `ls -ld`,
  `sudo -l -U`). A task you believe finished and which is not costs the same
  price as a task never started;
- **do not lock yourself out**. This drill touches accounts and `sudo`: keep a
  second session open before changing anything in the authentication, and
  validate any `sudoers` change with `visudo -c` before closing that session.

## Afterwards

The marking does not only say how many points you got: it says **which task**
failed and **what the system contained** at the moment of the check. Read it
again before replaying.

A drill is meant to be replayed. The second attempt serves to measure what you
retained from your mistakes, not to memorise answers: the exact values matter less
than the gestures, which transpose to any wording.
