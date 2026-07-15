# Lab — create a local account

> Prepare: `dsoxlab provision` then `dsoxlab run l2-user-lifecycle`

## Recap

[**Users & groups on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`useradd -u <uid> -m -d <home> -s <shell> -g <primary> -G <supp> <name>` creates
an account with a full identity. A user has **one primary group** (`-g`) and any
number of **supplementary groups** (`-G`). Later, `usermod -aG <group> <user>`
appends a group — the `-a` is vital, without it you replace all supplementary
groups. `id` and `getent passwd` inspect the result.

## Objectives

Create `alice`:

- UID `1500`, home `/home/alice`, shell `/bin/bash`;
- primary group `staff`;
- supplementary group `developers`.

## Validate

```bash
dsoxlab check l2-user-lifecycle
```
