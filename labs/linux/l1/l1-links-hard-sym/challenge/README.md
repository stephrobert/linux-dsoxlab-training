# Two ways to point at a file

## The situation

You have `original.txt`. A **hard link** is a second name for the very same file
(same inode, same data): delete the original and the data survives. A **symbolic
link** is a small pointer that stores a path; if the target moves, it dangles.
Learn to make both, and a symlink to a directory too.

The point: both are created with the same tool, and once in place nothing tells
them apart in an ordinary listing. So you will also need to know what to ask the
system in order to prove which is which.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/navigate-filesystem/hard-symbolic-links/

## What is asked

### Mission

From `original.txt` (in `challenge/work/`), create two types of links.

### Goal

1. `copie-dure.txt` — **hard link** to `original.txt` (same inode).
2. `raccourci.txt` — **symbolic link** to `original.txt`.
3. `data/` (directory) + `lien-data` — **symbolic link** to `data/`.

### Constraints

- `ln` for the hard link, `ln -s` for the symbolic one. No `cp`.
- Validation reads the **inode**, the **link count** and the real **target**
  (`readlink`): a copy fails the test.

### Validation

```bash
dsoxlab check l1-links-hard-sym
```
