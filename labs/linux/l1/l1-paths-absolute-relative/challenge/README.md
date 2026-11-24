# Pointing at a file without getting it wrong

## The situation

Every command that touches a file must first know where it is. There are two ways
to tell it: one starts from the root and holds from anywhere, the other starts
from where you stand and changes meaning as soon as you move. Confusing them
means writing to the wrong place, or finding nothing at all.

This lab has you practise both notations on the same file copy, then tests you on
navigation problems to be worked out in your head, without running a single
shell.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/navigate-filesystem/absolute-relative-paths/

## Absolute and relative paths

### Mission

Three tasks:

1. Copy `source.txt` to `backup/absolute/source.txt` using an **absolute path**.
2. Copy `source.txt` to `backup/relative/source.txt` using a **relative path**.
3. Solve the 5 path puzzles in `puzzles.txt`.

### Constraints

- Both copies must exist.
- Puzzle answers must be relative paths (no leading `/`).
- No placeholder left in `puzzles.txt`.


### Validation

```bash
dsoxlab check l1-paths-absolute-relative
```
