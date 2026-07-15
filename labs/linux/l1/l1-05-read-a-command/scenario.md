# Lab l1-05 — Read and decode a command

| | |
|---|---|
| **Level** | L1 — Fundamentals (B0) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 20 min |
| **Reference** | [Terminal Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/terminal/) |

---

## What you will learn

- Identify the three parts of every Linux command: command, options, arguments
- Distinguish short options (`-l`) from long options (`--long`)
- Understand what exit codes `0` and non-zero mean
- Spot and fix common command syntax errors
- Use `echo $?` to read the exit code of the last command

---

## Anatomy of a command

Every Linux command follows the same structure:

```
COMMAND  [OPTIONS]  [ARGUMENTS]
```

| Part | Role | Example |
|------|------|---------|
| Command | The program to run | `ls`, `grep`, `find` |
| Options | Modify behaviour | `-l`, `-a`, `--recursive` |
| Arguments | What to act on | `/etc`, `file.txt`, `"pattern"` |

### Example 1 — `ls -la /etc`

```
ls      -la      /etc
│        │        └── argument: directory to list
│        └─────────── options: -l (long) + -a (all, including hidden)
└──────────────────── command: list directory contents
```

### Example 2 — `grep -r "error" /var/log`

```
grep    -r       "error"   /var/log
│        │          │          └── argument: directory to search in
│        │          └──────────── argument: pattern to search for
│        └─────────────────────── option: -r (recursive)
└──────────────────────────────── command: search text in files
```

### Example 3 — `find /var -name "*.log" -mtime -7`

```
find    /var     -name "*.log"   -mtime -7
│        │           │               └── option+value: modified in last 7 days
│        │           └───────────────── option+value: filename pattern
│        └───────────────────────────── argument: directory to search
└────────────────────────────────────── command
```

---

## Exercise 1 — Decompose these commands

For each command below, identify: **COMMAND**, **OPTIONS**, **ARGUMENTS**.

```bash
cp -r /home/bob/docs/ /backup/
cat -n /etc/passwd
find /tmp -type f -name "*.tmp"
tar -czf archive.tar.gz /var/log/
chmod 755 /usr/local/bin/myscript.sh
```

---

## Exercise 2 — Exit codes

Every command returns an **exit code** when it finishes:

- `0` = success
- Any other value = error (the meaning depends on the command)

Test it:

```bash
ls /etc          # succeeds
echo $?          # prints 0

ls /does-not-exist   # fails
echo $?              # prints non-zero (e.g. 2)
```

Always check `$?` right after a command — it is overwritten by the next command.

---

## Exercise 3 — Find and fix broken commands

The following commands are incorrect. Run them, read the error message, then fix them.

```bash
# 1 — List the /etc directory in long format, showing hidden files
ls -la /etc/       # correct — run it to see the expected output
ls -la /et         # broken — what's wrong?

# 2 — Count lines in /etc/passwd
wc -l /etc/passwd   # correct
wc /etc/paswd       # broken — what's wrong?

# 3 — Display the last 5 lines of /etc/os-release
tail -n 5 /etc/os-release    # correct
tail -n5 /etc/os-releases    # broken — what's wrong?
```

---

## Fill in the template

```bash
cat challenge/work/analyse.txt
nano challenge/work/analyse.txt
```

Then validate:

```bash
dsoxlab check l1-05-read-a-command
```
