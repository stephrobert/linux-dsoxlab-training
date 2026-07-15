# Context — sort a noisy log with the shell alone

You have `journal.log`, a small application log. Without any editor, using only
redirections and pipes, you must extract a few facts into separate files: how
many lines it has, which lines are errors, what a failing command prints on
stderr, and what a command's full output (stdout + stderr) looks like when
merged.

Your mission — produce, in the work directory:

1. `total.txt` — the line count of `journal.log`.
2. `erreurs.txt` — only the `ERROR` lines.
3. `stderr.txt` — the error message of a command that fails (e.g. reading a
   missing file).
4. `tout.txt` — the standard output **and** the standard error of a command,
   merged into one file.

The trap: `>` only captures stdout. An error goes to stderr and slips past it
unless you use `2>` or `2>&1`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/
