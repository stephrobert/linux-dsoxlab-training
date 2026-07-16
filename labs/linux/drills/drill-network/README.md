# Drill — static networking

> Prepare: `dsoxlab provision` then `dsoxlab run drill-network`

**4 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS —
the subject names no tool. Everything on `lab0`, **never** the management
interface. Checked **after a network reload**.

```bash
dsoxlab challenge drill-network        # the subject
dsoxlab check drill-network            # score it (AlmaLinux — nmcli)
dsoxlab check drill-network -t ubuntu  # score it (Ubuntu — netplan)
```
