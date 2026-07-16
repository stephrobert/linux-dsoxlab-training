# Lab — hardened key-based SSH for a service user

> Prepare: `dsoxlab provision` then `dsoxlab run l4-ssh-key-auth-harden`

## Recap

[**SSH keys on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/)

`sshd` enforces strict permissions on key files: `~/.ssh` must be `0700` and
owned by the user, `authorized_keys` must be `0600` and owned by the user. Too
open, or owned by someone else, and the key is **silently ignored**. Read them
with `stat -c '%a %U:%G'`.

## Objectives

- `deploy` user exists;
- `~deploy/.ssh` is `0700`, owned `deploy:deploy`;
- `~deploy/.ssh/authorized_keys` is `0600`, owned `deploy:deploy`, key present.

## Validate

```bash
dsoxlab check l4-ssh-key-auth-harden
```
