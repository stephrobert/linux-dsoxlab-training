# Challenge — l3-app-constraints

## Mission

Raise the open-files limit for `appuser`, persistently.

## Goal (expected state)

1. A drop-in in `/etc/security/limits.d/` sets `nofile` for appuser.
2. Effective: `su - appuser -c 'ulimit -Sn'` → **4096** (soft).
3. Effective: `su - appuser -c 'ulimit -Hn'` → **8192** (hard).

## Constraints

- Edit `/etc/security/limits.d/appuser.conf`. Validation reads the
  **effective** limit in a login session (via pam_limits), not the command.

## Validation

```bash
dsoxlab check l3-app-constraints
```
