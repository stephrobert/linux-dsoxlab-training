# Put the clock back in sync

## The situation

This host drifted: its timezone is wrong, NTP is off and `chronyd` isn't even
running. Logs get confusing timestamps and TLS handshakes start failing when the
clock is off. Bring it back — and make it hold across a reboot.

The point: a timezone is only a display convention, it does not move the instant.
What matters lies elsewhere, in a question that is asked at boot as much as right
now: does this host keep its clock from the network? That lasting state is what
gets checked, not the commands you typed.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/networking/chrony/

## What is asked

### Mission

The clock is out of sync: wrong timezone, NTP off, `chronyd` down. Bring it back
and make it persist.

### Goal (expected state)

1. Timezone is `Europe/Paris`.
2. NTP is on (`timedatectl show -p NTP --value` → `yes`).
3. `chronyd` is **running and enabled**.

### Constraints

- Persistence matters: a running-but-not-enabled `chronyd` fails validation.
  Validation reads the **live** service state and `timedatectl`, not your history.

### Validation

```bash
dsoxlab check l4-ntp-sync
```
