# Drill — AppArmor

**4 tasks, 100 points, 15 minutes. No hints.** This drill is **LFCS only**: it
is played on Ubuntu 24.04 only, there is no AlmaLinux target. On the RHEL side,
mandatory access control is called SELinux and is the subject of
`drill-selinux`.

## What a drill is

A drill is not a lab. There is no course here, and that is deliberate: you are
in exam conditions. You are given a brief, a stopwatch and a machine, and you
must find on your own the moves you have already practised.

The difference with a lab comes down to three points:

- **no hint is available**, not even in exchange for points;
- **time counts**: this is the shortest drill in the repository, 15 minutes for
  four tasks. A brief that takes too long to read already eats a fifth of the
  budget;
- **the tasks are independent**. If one resists, move to the next and come back
  to it: an untreated task costs less than a stopwatch drained on the first one.

The pass mark is set at **70 points out of 100**.

## What you need to know before attempting it

AppArmor is the topic least well covered by the labs in the repository: be
warned before starting the clock.

| What the drill exercises | Where it is covered |
|---|---|
| The reasoning of a mandatory access control: enforce mode versus complain mode, and reading a denial in the journal | `l4-selinux-diagnose-avc` (on the RHEL side: the tool differs, the logic does not) |
| Driving the AppArmor profiles themselves and reading their mode | `lfcs-apparmor` (a playable lab, but its README points to the guide: there is no course on site) |

In other words, the revision is done in the online guide, not in a lab. If you
have never read the output of `aa-status`, do it once **before** starting the
clock: fifteen minutes leave no time to discover a display format.

## Getting into exam conditions

Start the stopwatch before opening the brief, not after, and **read all four
tasks first**: they all deal with the same mechanism, and handling them out of
order costs nothing.

Three habits specific to AppArmor:

- **the source of truth is `aa-status`, not the content of `/etc/apparmor.d/`**.
  A profile can exist on disk without being loaded, be loaded in a mode
  different from the one its file states, or have been reloaded since. Never
  conclude from a file: read the loaded state;
- **note the exact name of a profile before manipulating it**. Profiles are not
  named uniformly: some carry a short name, others the full path of the binary.
  A command addressed to a name that does not exist fails silently or touches a
  profile other than the one intended. Start again from the output of
  `aa-status` rather than typing a name from memory;
- **"loaded" is not "enforced"**. Complain mode logs without blocking, enforce
  mode blocks. These are two separate counts in the tool's output: after each
  change, read it again and check that your profile has indeed changed column.

One last misleading point: the machine ships certain profiles in complain mode
by default, with no doing of yours. Note the starting state before touching
anything, so that you know what you actually changed.

## Afterwards

The correction does not only say how many points you got: it says **which
task** failed and **what the system contained** at the time of the check. Read
it again before replaying.

A drill is meant to be replayed. The second attempt serves to measure what you
have retained from your mistakes, not to memorise answers: the exact values
matter less than the moves, which do transpose to any brief.
