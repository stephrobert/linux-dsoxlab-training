# AppArmor, the other MAC

## The situation

Debian and Ubuntu do not use SELinux: they use **AppArmor**. Same goal, confining
a program to what it legitimately needs, but a different model. AppArmor binds a
profile to a **path**, where SELinux labels every object.

A profile can be loaded and protect nothing at all: there is a mode in which it
only takes notes. That illusion of protection is what this drill hunts.

**Stopwatch**: 4 tasks, 15 minutes, no hints. LFCS only; RHEL has SELinux,
drilled in `drill-selinux`.

Read the subject: `dsoxlab challenge drill-apparmor`.

## Drill — AppArmor

**Format**: 4 tasks, 100 points, 15 minutes. **No hints.**

Three profiles are currently in the wrong mode.

```bash
dsoxlab check drill-apparmor
```

---

### Task 1 — AppArmor is up (25 pts)

The **`apparmor`** service must be **enabled**, and profiles must be loaded.

### Task 2 — ping, under watch (25 pts)

The **`ping`** profile must be in **complain** mode: it logs violations without
blocking them.

### Task 3 — man, enforced (25 pts)

The **`man`** profile must be in **enforce** mode.

### Task 4 — tcpdump, enforced (25 pts)

The **`tcpdump`** profile must be in **enforce** mode.

---

## Validate

```bash
dsoxlab check drill-apparmor
```
