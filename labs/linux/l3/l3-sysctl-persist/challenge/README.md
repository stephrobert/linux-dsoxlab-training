# Challenge — l3-sysctl-persist

## Mission

Harden the kernel: turn off IP routing and ICMP redirects, persistently.

## Goal (expected state)

1. `sysctl -n net.ipv4.ip_forward` → **0** (live).
2. `sysctl -n net.ipv4.conf.all.accept_redirects` → **0** (live).
3. Both are declared in `/etc/sysctl.d/` (reboot persistence).

## Constraints

- Drop-in `/etc/sysctl.d/99-hardening.conf`, then `sudo sysctl --system`.
  Validation reads the kernel's **active values** + the contents of sysctl.d.

## Validation

```bash
dsoxlab check l3-sysctl-persist
```
