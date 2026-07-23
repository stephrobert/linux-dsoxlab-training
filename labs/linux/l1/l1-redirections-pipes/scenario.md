# Context — sort a noisy log with the shell alone

You have `journal.log`, a small application log. Without any editor, using only
redirections and pipes, you must extract a few facts into separate files: how
many lines it has, which lines are errors, what a failing command prints on
stderr, and what a command's full output (stdout + stderr) looks like when
merged.

The trap: an ordinary redirection only captures stdout. An error travels on
another channel and slips past it. Aiming at that second channel and merging it
into the first are two distinct moves.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/
