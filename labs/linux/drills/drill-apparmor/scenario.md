# Context — AppArmor, the other MAC

Debian and Ubuntu do not use SELinux: they use **AppArmor**. Same goal, confining
a program to what it legitimately needs, but a different model. AppArmor binds a
profile to a **path**, where SELinux labels every object.

A profile can be loaded and protect nothing at all: there is a mode in which it
only takes notes. That illusion of protection is what this drill hunts.

**Stopwatch**: 4 tasks, 15 minutes, no hints. LFCS only; RHEL has SELinux,
drilled in `drill-selinux`.

Read the subject: `dsoxlab challenge drill-apparmor`.
