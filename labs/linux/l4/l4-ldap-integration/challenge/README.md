# Challenge — l4-ldap-integration

## Mission

Wire this client to the 389 Directory Server with SSSD so directory users resolve.

## Goal (expected state)

1. `getent passwd alice` returns the directory user (uid `10001`).
2. `id alice` works.
3. The active authselect profile is `sssd`.

## Constraints

- No local account: `alice` must come from LDAP, not `/etc/passwd`.
- `sssd.conf` must be `0600` or sssd won't start.
- The server IP is in `/root/ldap-server.env`. No TLS here — allow it explicitly.
- Validation reads `getent`, `id` and `authselect current`.

## Validation

```bash
dsoxlab check l4-ldap-integration
```
