# Challenge — l4-firewall-persist

## Mission

Open `http` through firewalld so it survives reload and reboot. Keep `ssh` open.

## Goal (expected state)

1. `http` in `firewall-cmd --list-services` (runtime).
2. `http` in `firewall-cmd --permanent --list-services` (reboot persistence).
3. `ssh` still allowed.

## Constraints

- **Never remove `ssh`** — it's your management access.
- Validation reads firewalld's runtime and permanent config, not your history.

## Validation

```bash
dsoxlab check l4-firewall-persist
```
