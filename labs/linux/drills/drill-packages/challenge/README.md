# The same job, two tools

## The situation

RHCSA and LFCS ask the same thing of you: install, freeze, query, remove. Only
the tool changes with the distribution family. That is exactly why this drill
exists **once**, and why its subject never names the command: an administrator
knows the objective, then reaches for the tool their distribution provides.

This drill is a **stopwatch**: 5 tasks, 20 minutes, no hints.

Read the subject: `dsoxlab challenge drill-packages`.

## Drill — package management

**Format**: 5 tasks, 100 points, 20 minutes. **No hints.**

The subject **does not name the tool**: use the one your distribution provides.
The objective is the same for RHCSA and LFCS.

```bash
dsoxlab check drill-packages                  # AlmaLinux — dnf
dsoxlab check drill-packages --target ubuntu  # Ubuntu — apt
```

---

### Task 1 — Install (20 pts)

The package **`tree`** must be installed.

### Task 2 — Freeze it (20 pts)

**`tree`** must be **frozen**: no upgrade may move it, even a full system
upgrade.

### Task 3 — Who owns this file? (20 pts)

Find which **package provides `/usr/bin/ssh`**, and write its **name alone** to
**`/root/owner.txt`**.

### Task 4 — What did it install? (20 pts)

Write to **`/root/tree-files.txt`** the list of files installed by the **`tree`**
package.

### Task 5 — Remove (20 pts)

The package **`nano`** must no longer be installed.

---

## Validate

```bash
dsoxlab check drill-packages
```
