# Context — let the directory users log in

A central **389 Directory Server** (base `dc=lab,dc=local`) holds your accounts —
including a posix user **`alice`**. This client machine doesn't know about it
yet: it cannot resolve `alice` at all. Wire it up with **SSSD** so directory
users resolve and can authenticate. You won't create local accounts.

The point: on RHEL you don't edit `nsswitch` or `pam` by hand, a dedicated tool
switches the system over to the SSSD plugins; SSSD then answers identity lookups
from the directory. Beware, it is picky about the permissions of its own
configuration and refuses to start if they are too open.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/
