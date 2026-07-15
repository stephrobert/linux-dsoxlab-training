# Lab — file permissions with chmod

> Prepare the workspace: `dsoxlab run l1-permissions-ugo`

## Recap

[**Change permissions on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/)

Every file has three permission triads — owner, group, other — each with read
(4), write (2), execute (1). `chmod` sets them in octal (`chmod 640 file`) or
symbolically (`chmod g+r,o-r file`). A directory needs `x` to be entered. Least
privilege: grant exactly what the file needs, no more.

## Objectives

- `secret.txt` → `0600` (private).
- `deploy.sh` → `0750` (owner/group executable).
- `notes.txt` → `0640` (group readable).
- `prive/` → directory `0700`.

## Validate

```bash
dsoxlab check l1-permissions-ugo
```
