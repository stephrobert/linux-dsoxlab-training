# Lab — Redirections and pipes

> Prepare the workspace: `dsoxlab run l1-redirections-pipes`

## Reminder

[**Redirections and pipes on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/)

Every command has three streams: standard input (0), standard output (1) and
standard error (2). `>` sends stdout to a file (overwrite), `>>` appends, `2>`
sends stderr, `2>&1` merges stderr into stdout, and `|` feeds one command's
output into the next. Getting the operator wrong loses data silently.

## Objectives

From `journal.log`, produce four files:

- `total.txt` — the line count of `journal.log` (redirection).
- `erreurs.txt` — only the `ERROR` lines (pipe + redirection).
- `stderr.txt` — the error message of a failing command (`2>`).
- `tout.txt` — stdout **and** stderr of a command, merged (`2>&1`).

## Validate

```bash
dsoxlab check l1-redirections-pipes
```
