# Lab — bond + bridge link aggregation with nmcli

> Prepare: `dsoxlab provision` then `dsoxlab run l4-bridge-bonding`

## Recap

[**Bond & bridge on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/)

A **bond** aggregates interfaces; `active-backup` keeps one active with the other
as standby, `miimon` polls link state. A **bridge** on top gives one L2 domain.
`nmcli con add type bond|dummy|bridge` + `bond.options` + `master`/`slave-type`
wire it; each connection profile persists across reboot.
`/proc/net/bonding/bond0` and `/sys/class/net/br0/brif/` show the result.

Work on `dummy1`/`dummy2`/`bond0`/`br0`, never on the management interface.

## Objectives

- `bond0` is a bond in `active-backup` mode with slaves `dummy1` + `dummy2`;
- `br0` is a bridge and `bond0` is one of its ports;
- the connection profiles persist on disk.

## Validate

```bash
dsoxlab check l4-bridge-bonding
```
