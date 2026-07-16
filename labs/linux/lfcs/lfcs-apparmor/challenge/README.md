# Challenge — lfcs-apparmor

## Mission

Put the `ping` AppArmor profile into complain mode.

## Goal (expected state)

1. AppArmor is active with profiles loaded.
2. The `ping` profile is in `complain` mode (`aa-status`).

## Constraints

- Use AppArmor tooling (`aa-complain`), not SELinux.
- Don't disable AppArmor globally — switch this one profile.
- Validation reads `aa-status --json`.

## Validation

```bash
dsoxlab check lfcs-apparmor
```
