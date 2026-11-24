# The commands you must not think about

## The situation

At the exam, the basic shell commands are not the subject: they are the **tools**
you use to answer the real questions. If you still hesitate on their syntax, you
burn minutes you do not have.

This drill is not a lesson, it is a **stopwatch**: 5 tasks, 20 minutes, no hints.
The same skills serve RHCSA and LFCS, because these commands are strictly
identical on RHEL and Debian. That is why this drill is played on the
distribution of your choice.

Read the subject: `dsoxlab challenge drill-essential-commands`.

## Drill — essential commands

**Format**: 5 tasks, 100 points, 20 minutes. **No hints.**

Playable on **either distribution** — these commands are identical on RHEL and
Debian:

```bash
dsoxlab check drill-essential-commands                  # AlmaLinux (default)
dsoxlab check drill-essential-commands --target ubuntu  # Ubuntu
```

---

### Task 1 — Archive by size (25 pts)

Under `/srv/drill/data/`, create **`/root/big.tar.gz`** (gzip tar) containing
every file **larger than 1 MiB**, and nothing else. The criterion is the
**size**, not the name.

### Task 2 — Who is the busiest? (20 pts)

`/srv/drill/access.csv` has the format `date,level,user,message`. Write to
**`/root/top-user.txt`** the **name alone** of the user with the most lines.

### Task 3 — Links (15 pts)

For `/srv/drill/access.csv`, create a **hard link** at `/root/access.hard` and a
**symbolic link** at `/root/access.soft`.

### Task 4 — Confidential report (20 pts)

`/srv/drill/report.txt` is currently `root:root` in `0644` — everyone can read
it. Make it belong to **`drilluser:drillers`** in **`0640`**.

### Task 5 — Split the streams (20 pts)

`/usr/local/bin/noisy.sh` writes to **both** stdout and stderr. Run it so that
its standard output lands in **`/root/out.log`** and its error output in
**`/root/err.log`** — each file holding only its own stream.

---

## Validate

```bash
dsoxlab check drill-essential-commands
```
