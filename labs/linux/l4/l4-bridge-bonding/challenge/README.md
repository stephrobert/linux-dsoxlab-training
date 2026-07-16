# Challenge — l4-bridge-bonding

## Mission

Aggregate two links: an `active-backup` bond with two slaves, under a bridge.

## Goal (expected state)

1. `bond0` is a bond in `active-backup` mode, slaves `dummy1` + `dummy2`
   (`/proc/net/bonding/bond0`).
2. `br0` is a bridge and `bond0` is one of its ports
   (`/sys/class/net/br0/brif/`).
3. The connection profiles persist on disk.

## Constraints

- **Never touch the management interface** — the one carrying your default route. Work only on the dedicated interfaces.
- Validation reads the bonding state, the bridge ports and the on-disk profiles.

## Validation

```bash
dsoxlab check l4-bridge-bonding
```
