# Raise an application's resource ceiling

## The situation

The service running as **`appuser`** opens thousands of files and keeps hitting
the default open-files limit. You must raise its `nofile` limit — and make it
stick for every new session, not just this shell.

The point: what you tweak inside a shell only holds for that shell. A durable
policy is declared elsewhere and applied when each session opens. And two values
coexist: the soft limit, which is the default in force, and the hard limit, which
is the ceiling a user can raise up to.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/processes/resource-limits/

## What is asked

### Mission

Raise the open-files limit for `appuser`, persistently.

### Goal (expected state)

1. A drop-in in `/etc/security/limits.d/` sets `nofile` for appuser.
2. Effective: `su - appuser -c 'ulimit -Sn'` → **4096** (soft).
3. Effective: `su - appuser -c 'ulimit -Hn'` → **8192** (hard).

### Constraints

- Edit `/etc/security/limits.d/appuser.conf`. Validation reads the
  **effective** limit in a login session (via pam_limits), not the command.

### Validation

```bash
dsoxlab check l3-app-constraints
```
