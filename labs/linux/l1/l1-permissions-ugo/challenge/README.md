# Challenge — l1-permissions-ugo

## Mission

The files in `challenge/work/` are all `0644`. Set the right bits.

## Goal

1. `secret.txt` → `0600`.
2. `deploy.sh` → `0750`.
3. `notes.txt` → `0640`.
4. `prive/` → directory at `0700` (to be created).

## Constraints

- Only `chmod` (and `mkdir`): no need for `sudo`, you are the owner.
- Validation reads the **actual bits** via `stat`, not the command you typed.

## Validation

```bash
dsoxlab check l1-permissions-ugo
```
