# Challenge — lfcs-netplan-static

## Mission

Configure a static IP and a static route with netplan on a dedicated interface.

## Goal (expected state)

1. `/etc/netplan/99-lab.yaml` declares `lab0` (dummy) with `192.0.2.50/24` and a
   route to `198.51.100.0/24 via 192.0.2.1`.
2. `lab0` carries `192.0.2.50` live.
3. The route to `198.51.100.0/24` is present.

## Constraints

- **Never touch the management interface** — the one carrying your default route. Work on `lab0`.
- Config file `0600`; apply with `netplan apply`.
- Validation reads the netplan file, `ip addr` and `ip route`.

## Validation

```bash
dsoxlab check lfcs-netplan-static
```
