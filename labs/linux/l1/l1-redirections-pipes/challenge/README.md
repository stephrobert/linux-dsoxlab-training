# Challenge — l1-redirections-pipes

## Mission

From `journal.log` (in `challenge/work/`), produce four files with the right
redirection operators.

## Goal (files to produce)

1. `total.txt` — the **line count** of `journal.log`.
2. `erreurs.txt` — only the lines containing **`ERROR`**.
3. `stderr.txt` — the **error message** of a failing command. Make it read the
   missing file **`inexistant.txt`**.
4. `tout.txt` — the standard output **and** the error of a single command,
   **merged**. List `journal.log`, which exists, and `inexistant.txt`, which
   does not: `tout.txt` must then contain both names.

The name `inexistant.txt` matters: validation looks for it inside the error
message, because the system's own message changes with the machine's language.
The commands themselves remain your choice.

## Constraints

- No editor: only redirections (`>`, `2>`, `2>&1`) and pipes (`|`).
- Validation reads the **actual content** of the files, not the command you typed.

## Validation

```bash
dsoxlab check l1-redirections-pipes
```
