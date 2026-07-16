# Lab — static IP & route with netplan

> Prepare: `dsoxlab provision` then `dsoxlab run lfcs-netplan-static`

## Recap

[**netplan on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/)

netplan describes the network in `/etc/netplan/*.yaml`. A device gets
`addresses:` for static IPs and `routes:` (`to:`/`via:`) for static routes.
`netplan generate` validates, `netplan apply` renders and brings it up (persistent
at boot). Config files should be `0600`.

Work on `lab0`, never on the management interface.

## Objectives

- `/etc/netplan/99-lab.yaml` declares `lab0` with `192.0.2.50/24` and the route;
- `lab0` carries `192.0.2.50` live;
- the route to `198.51.100.0/24` is present.

## Validate

```bash
dsoxlab check lfcs-netplan-static
```
