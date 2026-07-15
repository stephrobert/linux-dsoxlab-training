# Context — give each file the right permissions

Everything in your work directory is world-readable (`0644`), which is wrong for
half of it. A secret must stay private, a script must be runnable, a team note
should be readable by the group only, and you need a private directory. Fix the
permission bits — no more, no less than needed.

Your mission — in the work directory:

1. `secret.txt` → `0600` (only you can read/write it).
2. `deploy.sh` → `0750` (you and the group can run it, others cannot).
3. `notes.txt` → `0640` (the group reads it, others do not).
4. `prive/` → a directory in `0700` (only you can enter and list it).

The point: `chmod` sets bits in octal (`chmod 640 file`) or symbolically
(`chmod u+x file`), and each digit is the owner/group/other triad. Least
privilege means granting exactly what is required.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/
