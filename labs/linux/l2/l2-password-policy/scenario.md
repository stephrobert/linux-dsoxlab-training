# Context — put teeth on password policy

Passwords that never expire and can be one character long are an audit finding
waiting to happen. Harden the policy at three levels: the existing account, the
system default for new accounts, and the complexity rule.

Your mission, on the VM:

1. For user **`bob`**, set aging with `chage`: **max 60** days, **min 7** days,
   **warn 7** days before expiry.
2. Set the system default **`PASS_MAX_DAYS`** to **60** in `/etc/login.defs`
   (applies to accounts created afterwards).
3. Require a minimum password length of **12** in
   `/etc/security/pwquality.conf` (`minlen`).

The point: `chage` sets aging per account, `login.defs` seeds the defaults for
new users, and `pwquality` enforces complexity. `chage -l bob` shows the result.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/
