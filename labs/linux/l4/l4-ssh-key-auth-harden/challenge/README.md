# Challenge — l4-ssh-key-auth-harden

## Mission

`deploy` has its key in `authorized_keys` but `sshd` refuses it — fix the
ownership and permissions.

## Goal (expected state)

1. User `deploy` exists.
2. `~deploy/.ssh` → directory, `0700`, owned `deploy:deploy`.
3. `~deploy/.ssh/authorized_keys` → `0600`, owned `deploy:deploy`, key kept.

## Constraints

- Don't change the key content — only ownership and permissions are wrong.
- Validation reads the filesystem state (`stat`), not your history.

## Validation

```bash
dsoxlab check l4-ssh-key-auth-harden
```
