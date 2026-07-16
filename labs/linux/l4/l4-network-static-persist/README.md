# Lab — persistent static IPv4 with NetworkManager

> Prepare: `dsoxlab provision` then `dsoxlab run l4-network-static-persist`

## Recap

[**NetworkManager on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/)

On RHEL, `NetworkManager` owns the interfaces. `nmcli con add` creates a
connection profile; `ipv4.method manual` + `ipv4.addresses` sets a static
address; the profile lands in `/etc/NetworkManager/system-connections/` so it
survives reboot. `ip addr add` is volatile.

Work on the dedicated interface `lab0`, never on `enp5s0` (management).

## Objectives

- connection `lab-static` has `ipv4.method` = `manual`;
- its `ipv4.addresses` includes `192.0.2.50/24`;
- the profile file exists on disk;
- `lab0` carries `192.0.2.50` live.

## Validate

```bash
dsoxlab check l4-network-static-persist
```
