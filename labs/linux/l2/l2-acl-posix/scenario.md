# Context — access that ugo cannot express

`root` owns `/srv/projet` and `report.txt`. You must give **one specific user**
write access to the file and **one group** read access to the directory —
without changing the owner or the `ugo` bits, and without making them
world-readable. That is exactly what **POSIX ACLs** are for.

The point: an ACL adds named-user and named-group entries on top of the `ugo`
bits, without touching them. And what files created later inherit is not set in
the same place as the access you grant today.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/
