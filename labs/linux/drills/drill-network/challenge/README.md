# Drill — static networking

**Format**: 4 tasks, 100 points, 20 minutes. **No hints.**

Everything happens on the **dedicated `lab0` interface** (dummy).

> **Never touch the management interface** — the one carrying your default
> route. Cut it and you lose the machine, and the drill with it.

The subject **does not name the tool**: use your distribution's.

```bash
dsoxlab check drill-network                  # AlmaLinux — nmcli
dsoxlab check drill-network --target ubuntu  # Ubuntu — netplan
```

---

### Task 1 — A static address (25 pts)

**`lab0`** must carry **`203.0.113.20/24`**.

### Task 2 — A static route (25 pts)

A route to **`192.0.2.0/24` via `203.0.113.1`**.

### Task 3 — MTU (25 pts)

**`lab0`** must carry an **MTU of 1400**.

### Task 4 — Local name (25 pts)

**`lab-net.lab`** must resolve to **`203.0.113.20`**, with no DNS server
involved.

---

**Everything is checked after a network reload.** What you typed by hand does not
survive one.

## Validate

```bash
dsoxlab check drill-network
```
