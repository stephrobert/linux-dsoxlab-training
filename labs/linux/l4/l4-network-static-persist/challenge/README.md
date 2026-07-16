# Challenge — l4-network-static-persist

## Mission

Give this host a static IPv4 on a dedicated interface, the persistent way.

## Goal (expected state)

1. NetworkManager connection `lab-static` on interface `lab0` (type `dummy`).
2. `ipv4.method` = `manual`, `ipv4.addresses` includes `192.0.2.50/24`.
3. The profile is written under `/etc/NetworkManager/system-connections/`
   (reboot persistence) and `lab0` carries the address live.

## Constraints

- **Never touch `enp5s0`** — that's the management link; changing it locks you
  out. Work only on `lab0`.
- Validation reads NetworkManager and the live interface, not your shell history.

## Validation

```bash
dsoxlab check l4-network-static-persist
```
