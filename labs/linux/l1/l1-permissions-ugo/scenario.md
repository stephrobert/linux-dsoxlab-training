# Context — give each file the right permissions

Everything in your work directory is world-readable (`0644`), which is wrong for
half of it. A secret must stay private, a script must be runnable, a team note
should be readable by the group only, and you need a private directory. Fix the
permission bits: no more, no less than needed.

The point: a mode can be set in two ways, one numeric and one symbolic, and it
always reads as three triads: owner, group and others. Least privilege means
granting exactly what is required, and nothing more.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/
