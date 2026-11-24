# Aggregate two links for redundancy

## The situation

Two network links should act as one, with failover: if the active one drops, the
other takes over. That's a **bond** in `active-backup` mode, with `miimon=100`.
On top of it sits a **bridge** — the layer where VMs or containers would attach.
Build both with NetworkManager, on dedicated interfaces, and make it persistent.

You work on `dummy1`, `dummy2`, `bond0` and `br0`. **Never touch the management
interface** — the one carrying your default route: it is your link to the box.

The point: a bond aggregates links (`active-backup` = redundancy, one active at a
time, `miimon` polls link state), and a bridge sits above to give a single L2
domain. NetworkManager keeps each one as a connection profile on disk, and that
profile is what makes the whole thing survive a reboot.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/networking/bond-bridge/

## What is asked

### Mission

Aggregate two links: an `active-backup` bond with two slaves, under a bridge.

### Goal (expected state)

1. `bond0` is a bond in `active-backup` mode, slaves `dummy1` + `dummy2`
   (`/proc/net/bonding/bond0`).
2. `br0` is a bridge and `bond0` is one of its ports
   (`/sys/class/net/br0/brif/`).
3. The connection profiles persist on disk.

### Constraints

- **Never touch the management interface** — the one carrying your default route. Work only on the dedicated interfaces.
- Validation reads the bonding state, the bridge ports and the on-disk profiles.

### Validation

```bash
dsoxlab check l4-bridge-bonding
```
