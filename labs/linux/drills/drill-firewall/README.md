# Drill — firewall

> Prepare: `dsoxlab provision` then `dsoxlab run drill-firewall`

**5 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS —
the subject names no tool. Rules are checked **after a reload**.

```bash
dsoxlab challenge drill-firewall        # the subject
dsoxlab check drill-firewall            # score it (AlmaLinux — firewalld)
dsoxlab check drill-firewall -t ubuntu  # score it (Ubuntu — ufw)
```
