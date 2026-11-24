# Static networking the Ubuntu way: netplan

## The situation

Debian and Ubuntu describe the network in **netplan** YAML files under
`/etc/netplan/`. You need a fixed address and a static route on a dedicated
interface, and both must come back after a reboot.

You work on the dedicated interface `lab0`. **Never touch the management
interface** — the one carrying your default route: it is your link to the box.

The point: netplan is declarative, you describe the wanted state in YAML instead
of chaining `ip` commands. Writing the file is not enough: until it has been
rendered to the network backend, nothing changes on the machine. And getting that
content wrong on a remote host means losing your hand on it.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/networking/netplan/

## What is asked

### Mission

Configure a static IP and a static route with netplan on a dedicated interface.

### Goal (expected state)

1. `/etc/netplan/99-lab.yaml` declares `lab0` (dummy) with `192.0.2.50/24` and a
   route to `198.51.100.0/24 via 192.0.2.1`.
2. `lab0` carries `192.0.2.50` live.
3. The route to `198.51.100.0/24` is present.

### Constraints

- **Never touch the management interface** — the one carrying your default route. Work on `lab0`.
- Config file `0600`; apply with `netplan apply`.
- Validation reads the netplan file, `ip addr` and `ip route`.

### Validation

```bash
dsoxlab check lfcs-netplan-static
```
