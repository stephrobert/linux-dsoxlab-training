# Challenge — l4-network-troubleshoot

## Mission

`lab-net` on `lab1` is configured but dead and won't survive a reboot. Diagnose
and restore it.

## Goal (expected state)

1. Connection `lab-net` is `activated` (`nmcli -g GENERAL.STATE con show lab-net`).
2. `connection.autoconnect` = `yes` (reboot persistence).
3. `lab1` carries `198.51.100.10` live.

## Constraints

- **Never touch the management interface** (management link). Work only on `lab1`.
- Validation reads NetworkManager state and the live interface, not history.

## Validation

```bash
dsoxlab check l4-network-troubleshoot
```
