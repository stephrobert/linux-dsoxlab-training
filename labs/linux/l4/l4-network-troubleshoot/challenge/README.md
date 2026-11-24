# The interface is configured but dead

## The situation

A connection called `lab-net` exists on interface `lab1` with a correct static
address, yet the interface carries no IP and it won't come back after a reboot.
Something's off with its state — find it and bring the link back to life.

You work on `lab1`. **Never touch the management interface** — the one carrying
your default route: it is your link to the box.

The point: a connection can be fully configured and still carry nothing, and one
that comes up today will not necessarily come up at the next boot. Those are two
distinct states, both readable in what NetworkManager reports: to be read, not
guessed.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/networking/diagnostics/

## What is asked

### Mission

`lab-net` on `lab1` is configured but dead and won't survive a reboot. Diagnose
and restore it.

### Goal (expected state)

1. Connection `lab-net` is `activated` (`nmcli -g GENERAL.STATE con show lab-net`).
2. `connection.autoconnect` = `yes` (reboot persistence).
3. `lab1` carries `198.51.100.10` live.

### Constraints

- **Never touch the management interface** (management link). Work only on `lab1`.
- Validation reads NetworkManager state and the live interface, not history.

### Validation

```bash
dsoxlab check l4-network-troubleshoot
```
