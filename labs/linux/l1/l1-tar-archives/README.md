# Lab — tar, gzip, bzip2

> Prepare the workspace: `dsoxlab run l1-tar-archives`

## Recap

[**Archives & compression on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/)

`tar` groups files into a single archive; the compression is a separate option:
`z` for gzip, `j` for bzip2. Common verbs: `c` create, `t` list, `x` extract.
`-f` names the file, `-C` sets the extraction directory, and naming a member
extracts only that one.

## Objectives

From `rapport.txt`, `config.yaml`, `notes.txt`, produce:

- `docs.tar.gz` — gzip tarball (`tar czf`).
- `liste.txt` — the archive listing (`tar tzf`).
- `extrait/rapport.txt` — only `rapport.txt`, extracted into `extrait/` (`tar xzf … -C`).
- `docs.tar.bz2` — bzip2 tarball (`tar cjf`).

## Validate

```bash
dsoxlab check l1-tar-archives
```
