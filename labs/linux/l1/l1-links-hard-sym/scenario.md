# Context — two ways to point at a file

You have `original.txt`. A **hard link** is a second name for the very same file
(same inode, same data): delete the original and the data survives. A **symbolic
link** is a small pointer that stores a path; if the target moves, it dangles.
Learn to make both, and a symlink to a directory too.

The point: both are created with the same tool, and once in place nothing tells
them apart in an ordinary listing. So you will also need to know what to ask the
system in order to prove which is which.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/
