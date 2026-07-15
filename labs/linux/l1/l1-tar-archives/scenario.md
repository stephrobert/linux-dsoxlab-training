# Context — package files with tar

You have three files — `rapport.txt`, `config.yaml`, `notes.txt` — and you must
turn them into archives, inspect them, and pull a single file back out without
unpacking everything. This is the daily bread of backups and transfers.

Your mission — produce, in the work directory:

1. `docs.tar.gz` — a **gzip** tarball of the three files.
2. `liste.txt` — the **listing** of that archive's contents.
3. `extrait/rapport.txt` — **only** `rapport.txt`, extracted into an `extrait/`
   directory (selective extraction).
4. `docs.tar.bz2` — a **bzip2** tarball of the same three files.

The point: `tar` bundles, `z`/`j` pick the compressor (gzip/bzip2), `t` lists,
`x` extracts, and `-C` chooses where — and you can extract a single member by
naming it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/
