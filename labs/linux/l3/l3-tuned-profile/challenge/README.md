# Challenge — l3-tuned-profile

## Mission

Switch the active tuned profile to `throughput-performance`, persistently.

## Goal (expected state)

1. The `tuned` service is running.
2. `tuned-adm active` → **`throughput-performance`**.
3. `/etc/tuned/active_profile` contains `throughput-performance` (persistence).

## Constraints

- `tuned-adm profile throughput-performance`. Validation reads the **actually
  active profile**, not the command.

## Validation

```bash
dsoxlab check l3-tuned-profile
```
