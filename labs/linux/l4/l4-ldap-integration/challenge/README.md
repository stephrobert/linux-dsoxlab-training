# Let the directory users log in

## The situation

A central **389 Directory Server** (base `dc=lab,dc=local`) holds your accounts —
including a posix user **`alice`**. This client machine doesn't know about it
yet: it cannot resolve `alice` at all. Wire it up with **SSSD** so directory
users resolve and can authenticate. You won't create local accounts.

The point: on RHEL you don't edit `nsswitch` or `pam` by hand, a dedicated tool
switches the system over to the SSSD plugins; SSSD then answers identity lookups
from the directory. Beware, it is picky about the permissions of its own
configuration and refuses to start if they are too open.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/ldap-sssd/

## What is asked

### Mission

Wire this client to the 389 Directory Server with SSSD so directory users resolve.

### Goal (expected state)

1. `getent passwd alice` returns the directory user (uid `10001`).
2. `id alice` works.
3. The active authselect profile is `sssd`.

### Constraints

- No local account: `alice` must come from LDAP, not `/etc/passwd`.
- `sssd.conf` must be `0600` or sssd won't start.
- The server IP is in `/root/ldap-server.env`. No TLS here — allow it explicitly.
- Validation reads `getent`, `id` and `authselect current`.

### Validation

```bash
dsoxlab check l4-ldap-integration
```
