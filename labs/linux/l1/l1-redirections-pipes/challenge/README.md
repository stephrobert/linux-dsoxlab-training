# Challenge — l1-redirections-pipes

## Mission

From `journal.log` (in `challenge/work/`), produce four files with the right
redirection operators.

## Goal (files to produce)

1. `total.txt` — the **line count** of `journal.log`.
2. `erreurs.txt` — only the lines containing **`ERROR`**.
3. `stderr.txt` — the **error message** of a failing command (read a missing
   file).
4. `tout.txt` — the standard output **and** the error of a command, **merged**.

## Constraints

- No editor: only redirections (`>`, `2>`, `2>&1`) and pipes (`|`).
- Validation reads the **actual content** of the files, not the command you typed.

## Validation

```bash
dsoxlab check l1-redirections-pipes
```
