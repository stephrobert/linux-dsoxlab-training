# Context — access that ugo cannot express

`root` owns `/srv/projet` and `report.txt`. You must give **one specific user**
write access to the file and **one group** read access to the directory —
without changing the owner or the `ugo` bits, and without making them
world-readable. That is exactly what **POSIX ACLs** are for.

Your mission, on the VM:

1. Give user **`carol`** `rw` on `/srv/projet/report.txt` (`setfacl -m u:...`).
2. Give group **`auditors`** `rx` on `/srv/projet` (`setfacl -m g:...`).
3. Set a **default ACL** on `/srv/projet` so **new** files inherit `r` for
   `auditors` (`setfacl -m d:g:...`).

The point: an ACL adds named-user/named-group entries on top of `ugo`;
`getfacl` shows them; a `default:` entry is a template new files inherit. A `+`
in `ls -l` flags a file that carries ACLs.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/
