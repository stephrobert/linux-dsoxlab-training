# Context — key auth that silently refuses

A `deploy` service user should log in over SSH with its key — the public key is
already in `~deploy/.ssh/authorized_keys`. Yet `sshd` rejects it and falls back
to nothing. The key is fine; the **permissions** are not: `sshd` ignores an
`authorized_keys` that is group/world-writable or not owned by the user.

Your mission, on the VM:

1. Make `~deploy/.ssh` a directory owned by `deploy:deploy`, mode **`0700`**.
2. Make `~deploy/.ssh/authorized_keys` owned by `deploy:deploy`, mode **`0600`**.
3. Keep the existing public key in place.

The point: SSH key auth is as much about **ownership and permissions** as about
the key. `sshd` silently refuses `authorized_keys` if `.ssh` is too open or not
owned by the user — the trap that wastes hours. `stat -c '%a %U:%G'` shows both.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/
