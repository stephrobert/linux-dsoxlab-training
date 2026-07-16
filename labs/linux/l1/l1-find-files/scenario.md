# Context — find what you need in a project tree

You received `projet.tar.gz`, a small project directory. Without opening files one
by one, use **`find`** to locate exactly what matters: the logs, the big files,
and the ones with private permissions. `find` walks a whole tree and filters on
name, size, type, permissions and more.

Your mission — in the work directory:

1. **Extract** the archive, preserving permissions: `tar xpzf projet.tar.gz`.
2. Produce `logs.txt` — the paths of all **`*.log`** files under `projet/`
   (`find projet -name '*.log'`).
3. Produce `gros.txt` — the **regular files larger than 1000 bytes**
   (`find projet -type f -size +1000c`).
4. Produce `prives.txt` — the **regular files with permissions exactly `600`**
   (`find projet -type f -perm 600`).

The point: `-name` matches a glob, `-size +Nc` compares the size in bytes, `-perm`
matches the mode, and `-type f` restricts to regular files. `find` recurses by
default, so it sees files nested in subdirectories.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/
