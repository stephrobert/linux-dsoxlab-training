# Drill — firewall

**5 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS:
the subject names no tool, you use the one from your distribution (`firewalld` on
AlmaLinux, `ufw` on Ubuntu). Your rules are checked **after a firewall reload**.

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

This drill does not measure your knowledge of a tool, but your grasp of a
distinction: what is active now against what is written on the disk. If that
split is not familiar to you, play the matching lab **first**: there you will
find the course, the hints and the right to make mistakes that the drill will not
give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| Zones, temporary rule against permanent rule, reload | `l4-firewall-persist` |
| Opening a named service or a numbered port, and reading the gap between the two lists | `l4-firewall-persist` |
| Knowing whether a port really listens, and who filters it | `l4-network-troubleshoot` |

On the Ubuntu side, `ufw` is the subject of the `lfcs-firewall-ufw` lab. Careful:
its README does not yet contain a course on the spot, it points to the online
guide. The reasoning, however, is that of `l4-firewall-persist`.

## Getting into exam conditions

Start the stopwatch before opening the task list, not after. Twenty minutes go by
quickly, and the first exam reflex is to **read the five tasks first** to spot
those that can be handled with a single command.

Three precautions specific to the firewall, in the order in which they matter:

- **do not cut off your own session**. You are working over SSH: losing access
  means losing the drill. Open a **second session** before enabling anything, and
  make sure SSH is allowed **before** turning the firewall on, never after;
- **reload, then check**. A rule that does not survive the reload is worth
  nothing, and that is exactly what the check measures. Get into the habit of
  reloading yourself, then re-reading the complete state of the firewall
  (`firewall-cmd --list-all` or `ufw status verbose`): the list shown after the
  reload is the only one that counts;
- **do not confuse the three possible behaviours**. A port can be allowed, simply
  not allowed, or explicitly denied. Those three cases are not read in the same
  place in the tool's output: read the line, do not infer.

One last reflex: when a port is not in the zone you think it is, it is not the
rule that is wrong, it is the zone. Check which zone your interface is attached to
before suspecting the syntax.

## Afterwards

The marking does not only say how many points you got: it says **which task**
failed and **what the system contained** at the moment of the check. Read it
again before replaying.

A drill is meant to be replayed. The second attempt serves to measure what you
retained from your mistakes, not to memorise answers: the exact values matter less
than the gestures, which transpose to any wording.
