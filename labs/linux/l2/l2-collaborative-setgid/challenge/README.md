# A shared directory that actually shares

## The situation

The `devteam` group (alice, bob) needs a common directory, `/srv/partage`, where
everyone can drop files that the **whole group** can then edit. Right now it's
owned by `root:root` and every file someone creates keeps *their own* group — so
collaboration breaks. The fix is the **set-GID bit** on the directory.

The point: on a **directory**, the set-GID bit makes every new file inside
inherit the directory's group instead of the creator's primary group — the one
thing that makes a shared folder truly collaborative.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/permissions-ownership/

## What is asked

### Mission

Make `/srv/partage` a collaborative directory for the `devteam` group with the
set-GID bit.

### Goal (expected state)

1. `/srv/partage` is a directory owned by group `devteam`.
2. Its mode is `2775` (set-GID + `rwxrwxr-x`).
3. A file created inside by a `devteam` member inherits the `devteam` group.

### Constraints

- The group `devteam` and members `alice`/`bob` already exist.
- Validation reads the directory mode/group and creates a probe file as `alice`
  to check the inherited group.

### Validation

```bash
dsoxlab check l2-collaborative-setgid
```
