# Challenge — l1-links-hard-sym

## Mission

From `original.txt` (in `challenge/work/`), create two types of links.

## Goal

1. `copie-dure.txt` — **hard link** to `original.txt` (same inode).
2. `raccourci.txt` — **symbolic link** to `original.txt`.
3. `data/` (directory) + `lien-data` — **symbolic link** to `data/`.

## Constraints

- `ln` for the hard link, `ln -s` for the symbolic one. No `cp`.
- Validation reads the **inode**, the **link count** and the real **target**
  (`readlink`): a copy fails the test.

## Validation

```bash
dsoxlab check l1-links-hard-sym
```
