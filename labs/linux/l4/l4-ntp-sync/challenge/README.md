# Challenge — l4-ntp-sync

## Mission

The clock is out of sync: wrong timezone, NTP off, `chronyd` down. Bring it back
and make it persist.

## Goal (expected state)

1. Timezone is `Europe/Paris`.
2. NTP is on (`timedatectl show -p NTP --value` → `yes`).
3. `chronyd` is **running and enabled**.

## Constraints

- Persistence matters: a running-but-not-enabled `chronyd` fails validation.
  Validation reads the **live** service state and `timedatectl`, not your history.

## Validation

```bash
dsoxlab check l4-ntp-sync
```
