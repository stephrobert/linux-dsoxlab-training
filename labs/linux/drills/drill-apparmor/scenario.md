# Context — AppArmor, the other MAC

Debian and Ubuntu do not use SELinux: they use **AppArmor**. Same goal —
confining a program to what it legitimately needs — but a different model.
AppArmor binds a profile to a **path**, where SELinux labels every object.

Two modes, and the whole difference is there:

- **complain**: the profile logs violations but blocks nothing. This is where
  you build a profile, or diagnose;
- **enforce**: the profile actually blocks. This is where you leave it.

A profile left in complain protects nothing — it only takes notes. That is the
mistake this drill hunts.

**Stopwatch**: 4 tasks, 15 minutes, no hints. LFCS only — RHEL has SELinux,
drilled in `drill-selinux`.

Read the subject: `dsoxlab challenge drill-apparmor`.
