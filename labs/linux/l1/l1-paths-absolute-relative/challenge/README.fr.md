# Challenge — l1-09 : Absolute and relative paths

## Mission

Three tasks:

1. Copy `source.txt` to `backup/absolute/source.txt` using an **absolute path**.
2. Copy `source.txt` to `backup/relative/source.txt` using a **relative path**.
3. Solve the 5 path puzzles in `puzzles.txt`.

## Constraints

- Both copies must exist.
- Puzzle answers must be relative paths (no leading `/`).
- No placeholder left in `puzzles.txt`.

## Hints

```bash
# Absolute copy (from challenge/work/):
cp $(pwd)/source.txt $(pwd)/backup/absolute/source.txt

# Relative copy (from challenge/work/):
cp source.txt backup/relative/source.txt
```

## Validation

```bash
dsoxlab check l1-paths-absolute-relative
```
