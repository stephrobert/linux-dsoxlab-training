# Challenge — l2-password-policy

## Mission

Harden the password policy on the VM (`bob` account + system defaults).

## Goal (expected state)

1. `bob` : **max 60** age, **min 7**, **warning 7** (`chage -l bob`).
2. `PASS_MAX_DAYS 60` in `/etc/login.defs`.
3. `minlen = 12` (≥ 12) in `/etc/security/pwquality.conf`.

## Constraints

- `chage` for the account, editing `/etc/login.defs` and `pwquality.conf` for
  the defaults. Validation reads the **real state** (`chage -l`, file contents).

## Validation

```bash
dsoxlab check l2-password-policy
```
