# Lab — diagnose a down network connection

> Prepare: `dsoxlab provision` then `dsoxlab run l4-network-troubleshoot`

## Recap

[**Network diagnosis on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/)

`nmcli con show <name>` reveals a connection's state (`GENERAL.STATE`) and its
`connection.autoconnect` flag. A connection can be configured but **inactive**;
`nmcli con up` activates it, and `connection.autoconnect yes` makes it return
after a reboot. `ip addr` / `ip link` show the live interface.

Work on `lab1`, never on the management interface.

## Objectives

- `lab-net` is `activated`;
- `connection.autoconnect` = `yes`;
- `lab1` carries `198.51.100.10` live.

## Validate

```bash
dsoxlab check l4-network-troubleshoot
```
