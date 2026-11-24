# Onboard a new user, exactly

## The situation

A new developer joins. You must create their account with precise attributes —
the kind of task graded to the letter on RHCSA: a fixed UID, a real login shell,
a home directory, the right **primary** group and the right **supplementary**
group.

The point: pinning an account's identity when you create it is not the same as
adjusting it afterwards. And the classic mistake hangs on one nuance: adding a
supplementary group without wiping the ones the user already had.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/users-groups/

## What is asked

### Mission

Create the `alice` account with exact attributes (create the groups if needed).

### Goal (expected state)

1. `alice` exists, **UID 1500**, home `/home/alice`, shell `/bin/bash`.
2. **Primary** group: `staff`.
3. **Secondary** group: `developers`.

### Constraints

- `useradd` (and `groupadd`); `usermod -aG` to add a secondary group
  without overwriting the others (the `-a` is vital).
- Validation reads the **actual state** (`getent`, `id`), not the typed command.

### Validation

```bash
dsoxlab check l2-user-lifecycle
```
