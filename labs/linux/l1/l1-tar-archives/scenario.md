# Context — package files with tar

You have three files — `rapport.txt`, `config.yaml`, `notes.txt` — and you must
turn them into archives, inspect them, and pull a single file back out without
unpacking everything. This is the daily bread of backups and transfers.

The point: `tar` only bundles, and compression is a job it hands off to an
external compressor, gzip or bzip2 depending on what you ask for. Creating,
listing, extracting, choosing the destination and pulling out a single member are
all uses of the same tool.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/
