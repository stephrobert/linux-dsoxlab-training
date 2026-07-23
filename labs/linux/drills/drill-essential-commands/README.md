# Drill — essential commands

**5 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS:
these commands behave identically on AlmaLinux and on Ubuntu, you choose
whichever target suits you.

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

This drill revises the basic toolbox, the one both certifications assume you have
acquired. If one of these subjects is not familiar to you, play the matching lab
**first**: there you will find the course, the hints and the right to make
mistakes that the drill will not give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| Searching for files on something other than their name | `l1-find-files` |
| Creating a compressed archive and checking its content | `l1-tar-archives` |
| Filtering lines with `grep` and regular expressions | `l1-grep-regex` |
| Cutting, sorting, counting: `cut`, `sort`, `uniq`, `awk` | `l1-text-processing` |
| Hard links and symbolic links, and what tells them apart | `l1-links-hard-sym` |
| Owner, group and permissions in octal notation | `l1-permissions-ugo` |
| Separating standard output from error output | `l1-redirections-pipes` |

## Getting into exam conditions

Start the stopwatch before opening the task list, not after. Twenty minutes go by
quickly, and the first exam reflex is to **read the five tasks first** to spot
those that can be handled with a single command.

Three habits that win points on this drill in particular:

- **build your commands step by step**. A processing chain written in one go is
  almost always wrong. First display the list of files or the lines kept, count
  them, and only then plug in the rest;
- **check the deliverable, not the command**. You are not marked on what you
  typed but on what the machine contains: list the content of an archive with
  `tar -tzf`, compare two inodes with `ls -li`, re-read owner and mode with
  `stat`, and open an output file with `cat -A` if a trailing space worries you;
- **beware of noise**. When a file must contain a single piece of information, a
  header, an empty line or an error message mixed into the stream makes it wrong.
  Always look at what is really written before moving on.

## Afterwards

The marking does not only say how many points you got: it says **which task**
failed and **what the system contained** at the moment of the check. Read it
again before replaying.

A drill is meant to be replayed. The second attempt serves to measure what you
retained from your mistakes, not to memorise answers: the exact values matter
less than the gestures, which transpose to any wording.
