# Context — two ways to point at a file

You have `original.txt`. A **hard link** is a second name for the very same file
(same inode, same data); delete the original and the data survives. A **symbolic
link** is a small pointer that stores a path; if the target moves, it dangles.
Learn to make both, and a symlink to a directory too.

Your mission — in the work directory:

1. `copie-dure.txt` — a **hard link** to `original.txt` (same inode).
2. `raccourci.txt` — a **symbolic link** to `original.txt`.
3. `data/` — a directory, and `lien-data` — a **symbolic link** to it.

The point: `ln target name` makes a hard link, `ln -s target name` makes a
symbolic one. `ls -li` shows the inode and the link count that prove which is
which.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/
