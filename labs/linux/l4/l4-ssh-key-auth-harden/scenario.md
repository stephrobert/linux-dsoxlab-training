# Context — key auth that silently refuses

A `deploy` service user should log in over SSH with its key — the public key is
already in `~deploy/.ssh/authorized_keys`. Yet `sshd` rejects it and falls back
to nothing. The key is fine; the **permissions** are not: `sshd` ignores an
`authorized_keys` that is group/world-writable or not owned by the user.

The point: SSH key auth is as much about **ownership and permissions** as about
the key. `sshd` silently refuses an `authorized_keys` whose surroundings are too
open or wrongly owned, and says nothing on the client side — the trap that wastes
hours.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/
