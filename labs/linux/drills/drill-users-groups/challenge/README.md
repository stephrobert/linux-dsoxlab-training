# The account lifecycle, against the clock

## The situation

Creating a user is trivial. Creating **the right** user, with the right UID, the
right groups, an aging policy that actually applies, a delegation that grants
exactly what is needed and nothing more, and closing an account so that it is
truly closed: that is the job.

This drill is a **stopwatch**: 5 tasks, 20 minutes, no hints. The same skills
serve RHCSA and LFCS, because account management, password aging and `sudo`
delegation behave identically on RHEL and Debian.

Read the subject: `dsoxlab challenge drill-users-groups`.

## Drill — users, groups and delegation

**Format**: 5 tasks, 100 points, 20 minutes. **No hints.**

```bash
dsoxlab check drill-users-groups                  # AlmaLinux (default)
dsoxlab check drill-users-groups --target ubuntu  # Ubuntu
```

---

### Task 1 — An account to spec (20 pts)

Create **`deploy`**: UID **`4200`**, login shell **`/bin/bash`**, member of the
supplementary group **`ops`**.

### Task 2 — Password aging (20 pts)

On the **`intern`** account: password must expire after **30 days** at most,
with a **7-day warning**, and the **account** itself must expire on
**2027-01-01**.

### Task 3 — Collaborative directory (20 pts)

**`/srv/ops`** must belong to group **`ops`** in mode **`2770`**: files created
inside inherit the group, and *others* get nothing.

### Task 4 — Delegate sudo, narrowly (20 pts)

Members of **`ops`** must be able to run **`/usr/local/bin/ops-report.sh`** as
root **without a password** — and nothing more.

### Task 5 — A departing employee (20 pts)

**`former`** is leaving. Lock the account: its password must be **locked**, and
its shell must **forbid login**. A locked password alone is not enough — an SSH
key would still get in.

---

## Validate

```bash
dsoxlab check drill-users-groups
```
