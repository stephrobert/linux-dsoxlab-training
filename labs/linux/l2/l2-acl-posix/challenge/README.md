# Challenge — l2-acl-posix

## Mission

Grant fine-grained access via ACLs on `/srv/projet` without touching the owner or
the ugo permissions.

## Goal (expected state)

1. `carol` has `rw` (user ACL) on `/srv/projet/report.txt`.
2. `auditors` has `r-x` (group ACL) on `/srv/projet`.
3. A **default** ACL gives `r` to `auditors` on future files in `/srv/projet`.

## Constraints

- `setfacl -m` to add, `d:` for the default ACL. Check with `getfacl`.
- Validation reads the **actual ACLs** (`getfacl`), not the command you typed.

## Validation

```bash
dsoxlab check l2-acl-posix
```
