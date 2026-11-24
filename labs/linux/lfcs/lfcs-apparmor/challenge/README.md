# AppArmor, Debian's mandatory access control

## The situation

Where RHEL uses SELinux, Debian/Ubuntu uses **AppArmor**: per-program profiles
that confine what a binary can do. A profile runs in **enforce** (violations
blocked) or **complain** (violations only logged — the learning mode you use while
tuning a profile).

The point: AppArmor is driven profile by profile. You can put one profile into
learning mode, put it back into enforce, or unload it entirely, without touching
the others. It's AppArmor's answer to SELinux's enforcing/permissive — but per
program, not per machine.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/apparmor/

## What is asked

### Mission

Put the `ping` AppArmor profile into complain mode.

### Goal (expected state)

1. AppArmor is active with profiles loaded.
2. The `ping` profile is in `complain` mode (`aa-status`).

### Constraints

- Use AppArmor tooling (`aa-complain`), not SELinux.
- Don't disable AppArmor globally — switch this one profile.
- Validation reads `aa-status --json`.

### Validation

```bash
dsoxlab check lfcs-apparmor
```
