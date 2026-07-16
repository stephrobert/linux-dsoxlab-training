# Drill — package management

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
