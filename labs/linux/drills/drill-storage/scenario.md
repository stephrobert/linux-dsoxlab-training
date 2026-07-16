# Context — storage, against the clock

Storage is where RHCSA and LFCS candidates lose the most points, for one reason:
the chain is long — partition, PV, VG, LV, filesystem, mount, fstab — and a
single missing link makes everything else worthless.

This drill is a **stopwatch**: 5 tasks, 25 minutes, no hints. The same skills
serve both certifications: `parted`, LVM, XFS and `mkswap` are identical on RHEL
and Debian.

Two traps that cost real points:

- a mount that works **now** but is absent from `/etc/fstab`, or written by
  device path instead of **UUID** — device names move;
- an **extended logical volume whose filesystem did not follow**: `lvextend`
  alone gives you nothing, the space stays unusable.

Read the subject: `dsoxlab challenge drill-storage`.
