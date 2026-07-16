# Drill — firewall

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
