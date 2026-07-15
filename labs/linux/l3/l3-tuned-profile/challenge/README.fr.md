# Challenge — l3-tuned-profile

## Mission

Bascule le profil tuned actif sur `throughput-performance`, durablement.

## Objectif (état attendu)

1. Le service `tuned` tourne.
2. `tuned-adm active` → **`throughput-performance`**.
3. `/etc/tuned/active_profile` contient `throughput-performance` (persistance).

## Contraintes

- `tuned-adm profile throughput-performance`. La validation lit le **profil
  réellement actif**, pas la commande.

## Validation

```bash
dsoxlab check l3-tuned-profile
```
