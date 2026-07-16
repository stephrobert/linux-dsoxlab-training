# Drill — AppArmor

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
