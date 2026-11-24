# Put teeth on password policy

## The situation

Passwords that never expire and can be one character long are an audit finding
waiting to happen. Harden the policy at three levels: the existing account, the
system default for new accounts, and the complexity rule.

The point: those three levels are not set in the same place. Aging on an account
that already exists, the values inherited by accounts created later, and the
complexity demanded at the prompt are three distinct mechanisms, and you need to
identify them before touching the first one.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/users-groups/

## What is asked

### Mission

Harden the password policy on the VM (`bob` account + system defaults).

### Goal (expected state)

1. `bob` : **max 60** age, **min 7**, **warning 7** (`chage -l bob`).
2. `PASS_MAX_DAYS 60` in `/etc/login.defs`.
3. `minlen = 12` (≥ 12) in `/etc/security/pwquality.conf`.

### Constraints

- `chage` for the account, editing `/etc/login.defs` and `pwquality.conf` for
  the defaults. Validation reads the **real state** (`chage -l`, file contents).

### Validation

```bash
dsoxlab check l2-password-policy
```
