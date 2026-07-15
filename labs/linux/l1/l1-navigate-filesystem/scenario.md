# Lab l1-08 — Navigate the filesystem

| | |
|---|---|
| **Level** | L1 — Fundamentals (B1) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 30 min |
| **Reference** | [Système de fichiers Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/filesystem/) |

---

## What you will learn

- Navigate directories with `cd`, `pwd`, and `ls`
- Create a directory tree with `mkdir -p`
- Copy files with `cp` and directories with `cp -r`
- Move and rename files with `mv`
- Delete files and directories with `rm` and `rm -r`
- Check the exact structure you built with `tree` or `find`

---

## Command reference

| Command | What it does |
|---------|--------------|
| `pwd` | Print current directory |
| `cd <dir>` | Change directory |
| `cd ..` | Go up one level |
| `cd -` | Go back to previous directory |
| `ls -la` | List files with details and hidden files |
| `mkdir dir` | Create a directory |
| `mkdir -p a/b/c` | Create nested directories at once |
| `cp file dest` | Copy a file |
| `cp -r dir dest` | Copy a directory recursively |
| `mv src dest` | Move or rename |
| `rm file` | Delete a file |
| `rm -r dir` | Delete a directory and its contents |
| `rmdir dir` | Delete an empty directory |
| `tree` | Show directory tree (if installed) |
| `find . -type f` | List all files recursively |

---

## Target structure

Your goal: build this structure inside `challenge/work/projet/`:

```
projet/
├── src/
│   ├── app.py
│   └── utils.py
├── tests/
│   └── test_app.py
├── docs/
│   └── README.txt
└── config/
    └── settings.conf
```

---

## Exercise 1 — Create the directories

```bash
cd challenge/work
mkdir -p projet/src projet/tests projet/docs projet/config
```

Verify:

```bash
ls projet/
```

---

## Exercise 2 — Create placeholder files

```bash
touch projet/src/app.py projet/src/utils.py
touch projet/tests/test_app.py
touch projet/docs/README.txt
touch projet/config/settings.conf
```

---

## Exercise 3 — Rename and move

```bash
# Rename a file
mv projet/docs/README.txt projet/docs/README.txt.bak

# Restore it
mv projet/docs/README.txt.bak projet/docs/README.txt
```

---

## Exercise 4 — Copy a directory

```bash
cp -r projet/src projet/src_backup
ls projet/
# Don't forget to clean up the backup:
rm -r projet/src_backup
```

---

## Validate

```bash
dsoxlab check l1-navigate-filesystem
```
