# Challenge — l3-boot-target

## Mission

The default boot target is `graphical.target`. Set it back to server.

## Goal (expected state)

1. `systemctl get-default` → **`multi-user.target`**.

## Constraints

- `systemctl set-default`. Validation reads the **actual target**, not the command.

## Validation

```bash
dsoxlab check l3-boot-target
```
