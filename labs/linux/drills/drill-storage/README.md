# Drill — partitions, LVM and swap

**5 tasks, 100 points, 25 minutes. No hints.** Shared between RHCSA and LFCS:
`parted`, LVM, XFS and swap behave identically on AlmaLinux and on Ubuntu. The
extra disk `/dev/vdb` is attached and blank.

## What a drill is

A drill is not a lab. There is no course here, and that is deliberate: you are
in exam conditions. You are given a statement, a stopwatch and a machine, and
you must find on your own the moves you have already practised.

The difference with a lab comes down to three points:

- **no hint is available**, not even in exchange for points;
- **time counts**: 25 minutes for five tasks is the pace of the exam, not that
  of learning;
- **the tasks follow on from each other**. That is the particularity of
  storage: the chain goes from the partition to the mount, and a missing link
  makes everything that comes after worthless. If a link resists, repair it
  before moving on.

The pass mark is set at **70 points out of 100**.

## What you need to know before attempting it

This is the topic where candidates lose the most points, because the chain is
long and no shortcut exists. If one of the links below is not familiar to you,
play the corresponding lab **first**: there you will find the course, the hints
and the right to make mistakes that the drill will not give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| GPT partition table and splitting a disk | `l2-partition-gpt` |
| Physical volume, volume group, logical volume | `l2-lvm-extend-persist` |
| Extending a volume and making the filesystem follow | `l2-lvm-extend-persist` |
| Creating and labelling an XFS filesystem | `l2-filesystem-create-xfs` |
| Mounting by UUID persistently | `l2-fstab-persist-uuid` |
| Creating, activating and making swap persistent | `l2-swap-management` |
| Reading the space really available, and what eats it | `l2-disk-space-troubleshoot` |

## Getting into exam conditions

Start the stopwatch before opening the statement, not after. Twenty-five
minutes go by fast, and the first exam reflex is to **read the five tasks
first** to see how they chain together.

Three precautions specific to storage, and the first one prevails over all:

- **never get the wrong disk**. Run `lsblk -f` before every destructive command
  and read the whole output: the target disk must be the one the statement
  designates, and it must carry nothing mounted. A partition table overwritten
  on the wrong disk cannot be recovered in twenty-five minutes;
- **check link by link**, with the tool of each layer rather than with your
  memory: `lsblk` for the partitions, `pvs`, `vgs` and `lvs` for LVM, `blkid`
  for the UUID and the filesystem type, `findmnt` for what is really mounted,
  `swapon --show` for swap. Each of these five tools says something the others
  do not;
- **test `/etc/fstab` before you leave**. A faulty entry has no visible effect
  right away and blocks the boot later. Once you have written your lines,
  unmount and run `mount -a` again: if the command goes through silently, the
  persistence holds.

A classic and costly trap: enlarging a logical volume does not enlarge the
filesystem it carries. As long as `df -h` does not display the new size, the
space does not exist for the users, and the task is worth zero.

## Afterwards

The correction does not only tell you how many points you scored: it tells you
**which task** failed and **what the system contained** at the moment of the
check. Read it again before replaying.

A drill can be replayed. The second attempt serves to measure what you retained
from your mistakes, not to memorise answers: the exact values matter less than
the moves, which transpose to any statement.
