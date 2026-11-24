# Access that ugo cannot express

## The situation

`root` owns `/srv/projet` and `report.txt`. You must give **one specific user**
write access to the file and **one group** read access to the directory —
without changing the owner or the `ugo` bits, and without making them
world-readable. That is exactly what **POSIX ACLs** are for.

The point: an ACL adds named-user and named-group entries on top of the `ugo`
bits, without touching them. And what files created later inherit is not set in
the same place as the access you grant today.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/acl/

## What is asked

### Mission

Grant fine-grained access via ACLs on `/srv/projet` without touching the owner or
the ugo permissions.

### Goal (expected state)

1. `carol` has `rw` (user ACL) on `/srv/projet/report.txt`.
2. `auditors` has `r-x` (group ACL) on `/srv/projet`.
3. A **default** ACL gives `r` to `auditors` on future files in `/srv/projet`.

### Constraints

- `setfacl -m` to add, `d:` for the default ACL. Check with `getfacl`.
- Validation reads the **actual ACLs** (`getfacl`), not the command you typed.

### Validation

```bash
dsoxlab check l2-acl-posix
```
