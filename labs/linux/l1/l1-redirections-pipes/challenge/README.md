# Sort a noisy log with the shell alone

## The situation

You have `journal.log`, a small application log. Without any editor, using only
redirections and pipes, you must extract a few facts into separate files: how
many lines it has, which lines are errors, what a failing command prints on
stderr, and what a command's full output (stdout + stderr) looks like when
merged.

The trap: an ordinary redirection only captures stdout. An error travels on
another channel and slips past it. Aiming at that second channel and merging it
into the first are two distinct moves.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/files-and-text/redirections-pipes/

## What is asked

### Mission

From `journal.log` (in `challenge/work/`), produce four files with the right
redirection operators.

### Goal (files to produce)

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

### Constraints

- No editor: only redirections (`>`, `2>`, `2>&1`) and pipes (`|`).
- Validation reads the **actual content** of the files, not the command you typed.

### Validation

```bash
dsoxlab check l1-redirections-pipes
```
