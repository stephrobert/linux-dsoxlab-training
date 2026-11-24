# Key auth that silently refuses

## The situation

A `deploy` service user should log in over SSH with its key — the public key is
already in `~deploy/.ssh/authorized_keys`. Yet `sshd` rejects it and falls back
to nothing. The key is fine; the **permissions** are not: `sshd` ignores an
`authorized_keys` that is group/world-writable or not owned by the user.

The point: SSH key auth is as much about **ownership and permissions** as about
the key. `sshd` silently refuses an `authorized_keys` whose surroundings are too
open or wrongly owned, and says nothing on the client side — the trap that wastes
hours.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/ssh/ssh-keys/

## What is asked

### Mission

`deploy` has its key in `authorized_keys` but `sshd` refuses it — fix the
ownership and permissions.

### Goal (expected state)

1. User `deploy` exists.
2. `~deploy/.ssh` → directory, `0700`, owned `deploy:deploy`.
3. `~deploy/.ssh/authorized_keys` → `0600`, owned `deploy:deploy`, key kept.

### Constraints

- Don't change the key content — only ownership and permissions are wrong.
- Validation reads the filesystem state (`stat`), not your history.

### Validation

```bash
dsoxlab check l4-ssh-key-auth-harden
```
