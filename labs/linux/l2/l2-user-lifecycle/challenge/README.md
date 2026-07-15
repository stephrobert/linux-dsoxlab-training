# Challenge — l2-user-lifecycle

## Mission

Create the `alice` account with exact attributes (create the groups if needed).

## Goal (expected state)

1. `alice` exists, **UID 1500**, home `/home/alice`, shell `/bin/bash`.
2. **Primary** group: `staff`.
3. **Secondary** group: `developers`.

## Constraints

- `useradd` (and `groupadd`); `usermod -aG` to add a secondary group
  without overwriting the others (the `-a` is vital).
- Validation reads the **actual state** (`getent`, `id`), not the typed command.

## Validation

```bash
dsoxlab check l2-user-lifecycle
```
