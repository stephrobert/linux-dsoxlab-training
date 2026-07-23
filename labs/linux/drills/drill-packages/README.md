# Drill — package management

**5 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS: the
subject names no tool, you use the one of your distribution (`dnf` on AlmaLinux,
`apt` on Ubuntu). The goal is the same on both sides, only the command changes.

## What a drill is

A drill is not a lab. There is no course here, and that is deliberate: you are in
exam conditions. You are given a statement, a stopwatch and a machine, and you
have to find on your own moves you have already practised.

The difference with a lab comes down to three points:

- **no hint is available**, not even in exchange for points;
- **time counts**: 20 minutes for five tasks is the pace of the exam, not that of
  learning;
- **the tasks are independent**. If one resists, move to the next one and come
  back to it: an untreated task costs less than a stopwatch spent on the first
  one.

The pass mark is set at **70 points out of 100**.

## What you need to know before attempting it

Installing and removing is only half the subject: the other half consists of
**querying** the package database, which is precisely what nobody practises
spontaneously. If one of the topics below is not familiar to you, play the
matching lab **first**: you will find there the course, the hints and the right to
be wrong that the drill will not give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| Install, remove, and prove the state of a package | `l2-package-management` |
| Find which package provides a given file | `l2-package-management` |
| List what a package put on the disk | `l2-package-management` |
| Where packages come from: repositories, priorities, signature | `l2-repo-configure` |

On the Ubuntu side, `apt` and `dpkg` are the subject of the `lfcs-package-apt`
lab. Careful: its README does not yet contain a course on the spot, it points to
the online guide. Freezing a package against updates has no dedicated lab in
either family: that is the point to revise in the guide before you start.

## Getting into exam conditions

Start the stopwatch before opening the statement, not after. Twenty minutes go
fast, and the first exam reflex is to **read the five tasks first**, to spot those
that are handled in one command.

Three habits specific to this subject:

- **query, do not guess**. The package that provides a command does not
  necessarily carry the name of that command, and that name differs from one
  distribution to another. That is precisely why both families offer a
  query-by-file command: use it rather than reconstructing a name from memory;
- **when an output file is asked for, write exactly what is asked**. Raw output
  often contains a version, an architecture, a header or a summary line. Read the
  file you produced again before moving on: one line too many is worth zero, just
  like a wrong answer;
- **prove the state, not the action**. An install command that returns without an
  error proves nothing, in particular if the package was already there or if the
  transaction was cancelled. Always replay the query command afterwards, and for
  a frozen package, check that it does appear in the list of held packages rather
  than trusting the message displayed.

One reflex that saves time: when the syntax escapes you, `man` and `--help` are
allowed on exam day. Consulting them costs thirty seconds, a wrong command costs
five minutes.

## Afterwards

The correction does not only say how many points you got: it says **which task**
failed and **what the system contained** at the moment of the check. Read it
before replaying.

A drill is replayed. The second attempt serves to measure what you retained from
your mistakes, not to memorise answers: the exact values matter less than the
moves, which do transpose to any statement.
