# Challenge — l3-ssh-access-recovery

## Mission

An sshd drop-in has an invalid directive (`sshd -t` fails). Fix it before a
reload cuts off access.

## Goal (expected state)

1. `sshd -t` returns 0 (valid config).
2. sshd is running.
3. The bad value (`beaucoup-trop`) is gone.
4. `PermitRootLogin no` is **effective** (`sshd -T`).

## Constraints

- Fix `/etc/ssh/sshd_config.d/99-lab.conf` (MaxAuthTries = a number), keep
  `PermitRootLogin no`, validate with `sshd -t`, then `systemctl reload sshd`.
  Never reload a config that `sshd -t` rejects.

## Validation

```bash
dsoxlab check l3-ssh-access-recovery
```
