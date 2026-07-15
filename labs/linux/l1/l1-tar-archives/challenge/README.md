# Challenge — l1-tar-archives

## Mission

From `rapport.txt`, `config.yaml`, `notes.txt` (in `challenge/work/`), produce
four artifacts with `tar`.

## Goal (files to produce)

1. `docs.tar.gz` — **gzip** archive of the three files.
2. `liste.txt` — the archive **listing**.
3. `extrait/rapport.txt` — **only** `rapport.txt`, extracted into `extrait/`.
4. `docs.tar.bz2` — **bzip2** archive of the three files.

## Constraints

- Only `tar` (and `mkdir` for the extraction directory): no graphical archiver.
- Validation **actually opens the archives** and checks their members and the
  compression — typing the right command without producing the right file fails.

## Validation

```bash
dsoxlab check l1-tar-archives
```
