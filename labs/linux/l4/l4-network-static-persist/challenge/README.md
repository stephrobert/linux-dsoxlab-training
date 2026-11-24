# A static address that survives reboot

## The situation

A service needs a fixed IPv4 on this host, on a dedicated interface — and it must
come back after a reboot, not vanish. An `ip addr add` lasts until the next
reboot; the durable way on RHEL is a **NetworkManager connection profile**.

You work on the dedicated interface `lab0`. **Never touch the management
interface** — the one carrying your default route: it is your link to the box.

The point: a NetworkManager connection profile is written on disk, and that file
is what brings the address back after a reboot. But the profile must not only
exist, it must also be active: those are two separate checks.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/networking/networkmanager/

## What is asked

### Mission

Give this host a static IPv4 on a dedicated interface, the persistent way.

### Goal (expected state)

1. NetworkManager connection `lab-static` on interface `lab0` (type `dummy`).
2. `ipv4.method` = `manual`, `ipv4.addresses` includes `192.0.2.50/24`.
3. The profile is written under `/etc/NetworkManager/system-connections/`
   (reboot persistence) and `lab0` carries the address live.

### Constraints

- **Never touch the management interface** — that's the management link; changing it locks you
  out. Work only on `lab0`.
- Validation reads NetworkManager and the live interface, not your shell history.

### Validation

```bash
dsoxlab check l4-network-static-persist
```
