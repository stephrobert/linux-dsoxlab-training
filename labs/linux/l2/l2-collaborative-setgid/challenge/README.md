# Challenge — l2-collaborative-setgid

## Mission

Make `/srv/partage` a collaborative directory for the `devteam` group with the
set-GID bit.

## Goal (expected state)

1. `/srv/partage` is a directory owned by group `devteam`.
2. Its mode is `2775` (set-GID + `rwxrwxr-x`).
3. A file created inside by a `devteam` member inherits the `devteam` group.

## Constraints

- The group `devteam` and members `alice`/`bob` already exist.
- Validation reads the directory mode/group and creates a probe file as `alice`
  to check the inherited group.

## Validation

```bash
dsoxlab check l2-collaborative-setgid
```
