# Context — put teeth on password policy

Passwords that never expire and can be one character long are an audit finding
waiting to happen. Harden the policy at three levels: the existing account, the
system default for new accounts, and the complexity rule.

The point: those three levels are not set in the same place. Aging on an account
that already exists, the values inherited by accounts created later, and the
complexity demanded at the prompt are three distinct mechanisms, and you need to
identify them before touching the first one.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/
