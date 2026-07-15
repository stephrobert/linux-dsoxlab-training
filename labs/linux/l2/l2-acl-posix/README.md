# Lab — POSIX ACLs

> Prepare: `dsoxlab provision` then `dsoxlab run l2-acl-posix`

## Recap

[**ACLs on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/)

`setfacl -m u:<user>:<perms> <path>` adds a named-user entry, `g:<group>:` a
named-group one. On a directory, `d:` (or `-d`) sets a **default** ACL that new
files inherit. `getfacl <path>` prints all entries; `setfacl -b` removes them;
`ls -l` shows a trailing `+` on ACL-bearing files.

## Objectives

- `carol` → `rw` on `/srv/projet/report.txt`;
- `auditors` → `rx` on `/srv/projet`;
- default ACL: `auditors` → `r` on new files in `/srv/projet`.

## Validate

```bash
dsoxlab check l2-acl-posix
```
