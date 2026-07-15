# Context — a landmine in the sshd config

Someone dropped a config snippet with a typo: `sshd -t` fails. The **running**
sshd still works (it only re-reads on reload), so you can still get in — but the
next `systemctl reload sshd` or reboot would leave the server unreachable.
Defuse it before that happens.

Your mission, on the VM:

1. Find the bad directive in `/etc/ssh/sshd_config.d/` (`sshd -t` tells you where).
2. **Fix the invalid value** (`MaxAuthTries` must be a number, e.g. `3`) while
   **keeping `PermitRootLogin no`**.
3. **Validate** with `sshd -t`, then `systemctl reload sshd`.

The point: `sshd -t` checks the config *offline* — always run it before a reload,
because a broken sshd config is how admins lock themselves out. `sshd -T` prints
the effective settings.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/
