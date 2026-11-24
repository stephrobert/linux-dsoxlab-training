# Find what you need in a project tree

## The situation

You received `projet.tar.gz`, a small project directory. Without opening files
one by one, use **`find`** to locate exactly what matters: the logs, the big
files, and the ones with private permissions.

The point: `find` walks a whole tree, recursively, and can filter on more than
the name. What remains is knowing which criterion to ask for on each question,
and how to express it.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/files-and-text/find-files/

## What is asked

### Mission

Extract `projet.tar.gz` and locate files with `find`.

### Goal (files to produce in the work dir)

1. `logs.txt` — every `*.log` path under `projet/`.
2. `gros.txt` — regular files larger than 1000 bytes.
3. `prives.txt` — regular files with permissions exactly `600`.

### Constraints

- Extract with `tar xpzf projet.tar.gz` (the `p` keeps the permissions).
- Use `find` (a subshell/editor won't help). `-type f` restricts to files.
- Validation reads the file contents and recomputes each list from the real
  `projet/` tree, so order doesn't matter but the set of paths must be exact.

### Validation

```bash
dsoxlab check l1-find-files
```
