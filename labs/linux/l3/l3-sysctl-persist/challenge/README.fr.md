# Challenge — l3-sysctl-persist

## Mission

Durcis le noyau : coupe le routage IP et les redirections ICMP, durablement.

## Objectif (état attendu)

1. `sysctl -n net.ipv4.ip_forward` → **0** (live).
2. `sysctl -n net.ipv4.conf.all.accept_redirects` → **0** (live).
3. Les deux sont déclarés dans `/etc/sysctl.d/` (persistance reboot).

## Contraintes

- Drop-in `/etc/sysctl.d/99-hardening.conf`, puis `sudo sysctl --system`. La
  validation lit les **valeurs actives** du noyau + le contenu de sysctl.d.

## Validation

```bash
dsoxlab check l3-sysctl-persist
```
