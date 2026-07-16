# Drill — essential commands

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
