# Drill — systemd, timers and scheduling

**Format**: 5 tasks, 100 points, 25 minutes. **No hints.**

```bash
dsoxlab check drill-systemd                  # AlmaLinux (default)
dsoxlab check drill-systemd --target ubuntu  # Ubuntu
```

---

### Task 1 — A service that survives (20 pts)

Create **`labapi.service`**, running `/usr/local/bin/labapi.sh`. It must be
**enabled**, **running**, and **restart automatically on failure**.

### Task 2 — A weekly timer (20 pts)

Create **`labclean.timer`**, triggering **`labclean.service`** every **Monday at
04:00**. `labclean.service` must run `/usr/local/bin/labclean.sh`. The timer must
be enabled and active.

### Task 3 — A cron job (20 pts)

For the user **`opsuser`**, schedule `/usr/local/bin/labclean.sh` via **cron**,
**every 15 minutes**.

### Task 4 — The right boot target (20 pts)

This server boots into **`graphical.target`** — on a headless machine. Make it
boot into **`multi-user.target`** by default.

### Task 5 — Never again (20 pts)

**`labdanger.service`** must never start, not even by hand or by dependency.
Disabling it is not enough.

---

## Validate

```bash
dsoxlab check drill-systemd
```
