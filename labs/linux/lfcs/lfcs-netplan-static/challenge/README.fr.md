# Challenge — lfcs-netplan-static

## Mission

Configure une IP statique et une route statique avec netplan sur une interface
dédiée.

## Objectif (état attendu)

1. `/etc/netplan/99-lab.yaml` déclare `lab0` (dummy) avec `192.0.2.50/24` et une
   route vers `198.51.100.0/24 via 192.0.2.1`.
2. `lab0` porte `192.0.2.50` en live.
3. La route vers `198.51.100.0/24` est présente.

## Contraintes

- **Ne touche jamais à l'interface de gestion** — celle qui porte ta route par défaut. Travaille sur `lab0`.
- Fichier de config `0600` ; applique avec `netplan apply`.
- On lit le fichier netplan, `ip addr` et `ip route`.

## Validation

```bash
dsoxlab check lfcs-netplan-static
```
