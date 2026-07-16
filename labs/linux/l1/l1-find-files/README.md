# Lab — locate files with find

> Prepare: `dsoxlab run l1-find-files` (copies `projet.tar.gz` into the work dir)

## Recap

[**find on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/)

`find <path> <predicates>` walks a tree and filters: `-name '*.log'` (glob),
`-size +1000c` (bytes; `k`/`M` for KiB/MiB), `-perm 600` (exact mode),
`-type f` (regular files). It recurses by default. `tar xpzf` extracts while
preserving the stored permissions.

## Objectives (files to produce in the work dir)

- `logs.txt` — all `*.log` paths under `projet/`;
- `gros.txt` — regular files larger than 1000 bytes;
- `prives.txt` — regular files with permissions exactly `600`.

## Validate

```bash
dsoxlab check l1-find-files
```
