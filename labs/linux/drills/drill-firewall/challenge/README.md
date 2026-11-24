# The firewall, and the rule that vanishes

## The situation

Every RHCSA candidate has done it: open the port, test it, it works, move on, and
lose the points, because the rule was never made permanent. It lived in memory
and died at the first reload.

This drill is a **stopwatch**: 5 tasks, 20 minutes, no hints. The objective is
the same on both certifications; only the tool changes with the distribution, so
the subject does not name it.

One thing not to forget: you work over SSH. A firewall that closes on you costs
you the machine, and every remaining task with it.

Read the subject: `dsoxlab challenge drill-firewall`.

## Drill — firewall

**Format**: 5 tasks, 100 points, 20 minutes. **No hints.**

The subject **does not name the tool**: use your distribution's.

> **Careful**: you are working over SSH. Lose it and you lose the drill.

```bash
dsoxlab check drill-firewall                  # AlmaLinux — firewalld
dsoxlab check drill-firewall --target ubuntu  # Ubuntu — ufw
```

---

### Task 1 — Bring it up (20 pts)

The firewall must be **active**, and must still be there **after a reboot**.

### Task 2 — HTTP (20 pts)

Allow **`80/tcp`**.

### Task 3 — The application (20 pts)

Allow **`8443/tcp`**.

### Task 4 — Keep the door open (20 pts)

**SSH must remain allowed.**

### Task 5 — Telnet, never (20 pts)

**`23/tcp`** must be **explicitly rejected** — not merely "not allowed".

---

**Your rules are checked after a firewall reload.** A rule that does not survive
one does not count.

## Validate

```bash
dsoxlab check drill-firewall
```
