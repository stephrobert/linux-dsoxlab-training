# A landmine in the sshd config

## The situation

Someone dropped a config snippet with a typo: the sshd configuration no longer
passes its syntax check. The **running** sshd still works (it only re-reads on
reload), so you can still get in — but the next `systemctl reload sshd` or reboot
would leave the server unreachable. Defuse it before that happens.

The point: a broken sshd config is how admins lock themselves out. The daemon can
check its configuration *offline*, before any reload, and can also print the
settings it would really apply. That reflex is what's missing here.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/troubleshoot/lost-ssh-access/

## What is asked

### Mission

An sshd drop-in has an invalid directive (`sshd -t` fails). Fix it before a
reload cuts off access.

### Goal (expected state)

1. `sshd -t` returns 0 (valid config).
2. sshd is running.
3. The bad value (`beaucoup-trop`) is gone.
4. `PermitRootLogin no` is **effective** (`sshd -T`).

### Constraints

- Fix `/etc/ssh/sshd_config.d/99-lab.conf` (MaxAuthTries = a number), keep
  `PermitRootLogin no`, validate with `sshd -t`, then `systemctl reload sshd`.
  Never reload a config that `sshd -t` rejects.
- Deleting the file is not a repair: the security setting would go with it.
- Keep a **second SSH session open** for the whole exercise: no account on the
  VM has a password, so the serial console would not save you.

### Validation

```bash
dsoxlab check l3-ssh-access-recovery
```
