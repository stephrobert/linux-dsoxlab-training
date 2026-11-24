# Package files with tar

## The situation

You have three files — `rapport.txt`, `config.yaml`, `notes.txt` — and you must
turn them into archives, inspect them, and pull a single file back out without
unpacking everything. This is the daily bread of backups and transfers.

The point: `tar` only bundles, and compression is a job it hands off to an
external compressor, gzip or bzip2 depending on what you ask for. Creating,
listing, extracting, choosing the destination and pulling out a single member are
all uses of the same tool.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/files-and-text/archive-compress/

## What is asked

### Mission

From `rapport.txt`, `config.yaml`, `notes.txt` (in `challenge/work/`), produce
four artifacts with `tar`.

### Goal (files to produce)

1. `docs.tar.gz` — **gzip** archive of the three files.
2. `liste.txt` — the archive **listing**.
3. `extrait/rapport.txt` — **only** `rapport.txt`, extracted into `extrait/`.
4. `docs.tar.bz2` — **bzip2** archive of the three files.

### Constraints

- Only `tar` (and `mkdir` for the extraction directory): no graphical archiver.
- Validation **actually opens the archives** and checks their members and the
  compression — typing the right command without producing the right file fails.

### Validation

```bash
dsoxlab check l1-tar-archives
```
