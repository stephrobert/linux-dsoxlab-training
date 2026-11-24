# Give each file the right permissions

## The situation

Everything in your work directory is world-readable (`0644`), which is wrong for
half of it. A secret must stay private, a script must be runnable, a team note
should be readable by the group only, and you need a private directory. Fix the
permission bits: no more, no less than needed.

The point: a mode can be set in two ways, one numeric and one symbolic, and it
always reads as three triads: owner, group and others. Least privilege means
granting exactly what is required, and nothing more.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/users-permissions-processes/change-permissions/

## What is asked

### Mission

The files in `challenge/work/` are all `0644`. Set the right bits.

### Goal

1. `secret.txt` → `0600`.
2. `deploy.sh` → `0750`.
3. `notes.txt` → `0640`.
4. `prive/` → directory at `0700` (to be created).

### Constraints

- Only `chmod` (and `mkdir`): no need for `sudo`, you are the owner.
- Validation reads the **actual bits** via `stat`, not the command you typed.

### Validation

```bash
dsoxlab check l1-permissions-ugo
```
