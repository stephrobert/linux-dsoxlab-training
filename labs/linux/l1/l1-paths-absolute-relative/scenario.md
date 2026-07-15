# Lab l1-09 — Absolute and relative paths

| | |
|---|---|
| **Level** | L1 — Fundamentals (B1) — **Checkpoint** |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 25 min |
| **Reference** | [Système de fichiers Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/filesystem/) |

---

## What you will learn

- Distinguish absolute paths from relative paths visually
- Copy a file using an absolute path
- Copy a file using a relative path from a different directory
- Compute the result of `..` navigation mentally
- Solve path puzzles without running a shell

---

## Key concepts

### Absolute path

Starts with `/`. Always correct regardless of where you are.

```
/home/bob/docs/report.txt
/etc/nginx/nginx.conf
```

### Relative path

Starts from the **current directory**. Depends on where you are.

```
docs/report.txt      (relative to /home/bob/ if you are there)
../bob/docs/         (go up one level, then down)
./script.sh         (current directory explicitly)
```

### Special components

| Component | Meaning |
|-----------|---------|
| `.` | Current directory |
| `..` | Parent directory |
| `~` | Home directory |
| `-` (for `cd`) | Previous directory |

---

## Exercise 1 — Absolute vs relative

Given:
- You are in `/home/bob/projects/web/`
- You want to access `/home/bob/projects/docs/notes.txt`

Absolute path: `/home/bob/projects/docs/notes.txt`
Relative path: `../docs/notes.txt`

---

## Exercise 2 — Copy with absolute path

```bash
cd challenge/work
# Copy source.txt to backup/absolute/source.txt using an absolute path
# The absolute path of work/ is: $(pwd)
cp "$(pwd)/source.txt" "$(pwd)/backup/absolute/source.txt"
```

---

## Exercise 3 — Copy with relative path

```bash
# Still in challenge/work/
cp source.txt backup/relative/source.txt
```

---

## Exercise 4 — Path puzzles

Open `puzzles.txt` and solve the 5 navigation puzzles.
Each puzzle gives you a starting directory and a target: write the relative path.

```bash
cat challenge/work/puzzles.txt
nano challenge/work/puzzles.txt
dsoxlab check l1-paths-absolute-relative
```
