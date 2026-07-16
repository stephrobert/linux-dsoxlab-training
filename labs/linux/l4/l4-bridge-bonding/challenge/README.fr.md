# Challenge — l4-bridge-bonding

## Mission

Agrège deux liens : un bond `active-backup` avec deux esclaves, sous un bridge.

## Objectif (état attendu)

1. `bond0` est un bond en mode `active-backup`, esclaves `dummy1` + `dummy2`
   (`/proc/net/bonding/bond0`).
2. `br0` est un bridge et `bond0` est un de ses ports
   (`/sys/class/net/br0/brif/`).
3. Les profils de connexion persistent sur disque.

## Contraintes

- **Ne touche jamais à `enp5s0`** (gestion). Travaille sur les interfaces dédiées.
- On lit l'état du bonding, les ports du bridge et les profils sur disque.

## Validation

```bash
dsoxlab check l4-bridge-bonding
```
