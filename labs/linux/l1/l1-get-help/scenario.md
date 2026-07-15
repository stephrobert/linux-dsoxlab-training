# Lab l1-06 — Get help from the command line

| | |
|---|---|
| **Level** | L1 — Fundamentals (B0) — **Checkpoint** |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 20 min |
| **Reference** | [Terminal Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/terminal/) |

---

## What you will learn

- Navigate a `man` page to find a specific option
- Use `--help` for a quick option summary
- Search for commands by keyword with `apropos`
- Read the SYNOPSIS section to understand option syntax
- Find the right option without using a search engine

---

## The three help tools

| Tool | Best for |
|------|---------|
| `man <command>` | Full reference — all options, examples, exit codes |
| `<command> --help` | Quick summary — usually fits on screen |
| `apropos <keyword>` | When you don't know the command name |
| `whatis <command>` | One-line description of a command |

---

## Exercise 1 — Read a man page

```bash
man ls
```

Inside `man`:
- Arrow keys or `j`/`k` scroll line by line
- `Space` scrolls down one page, `b` scrolls back
- `/word` searches forward, `n` jumps to next match
- `q` quits

Look at the **SYNOPSIS** section. Options in `[]` are optional. `...` means repeatable.

Find the option that shows file sizes in human-readable format (KB, MB, GB).

```bash
man ls | grep -A1 "human"
```

---

## Exercise 2 — Use --help

```bash
cp --help
```

`--help` prints a compact summary. Use `| grep` to filter:

```bash
cp --help | grep -i recursive
```

Find the option that copies a directory recursively.

---

## Exercise 3 — Search with apropos

When you know what you want to do but not the command:

```bash
apropos "copy files"
apropos "disk space"
apropos "show running processes"
```

Each result shows `command (section) — description`.
Sections: 1 = user commands, 5 = config files, 8 = admin commands.

```bash
apropos tail
man 1 tail
```

---

## Exercise 4 — Find the right option

Use `man`, `--help`, or `apropos` to answer the three questions in `aide.txt`.

Do **not** search the web. Use only the built-in help tools.

```bash
cat challenge/work/aide.txt    # read the questions
nano challenge/work/aide.txt   # fill in your answers
```

Then validate:

```bash
dsoxlab check l1-get-help
```
