# Challenge — l2-user-lifecycle

## Mission

Crée le compte `alice` avec des attributs exacts (crée les groupes si besoin).

## Objectif (état attendu)

1. `alice` existe, **UID 1500**, home `/home/alice`, shell `/bin/bash`.
2. Groupe **primaire** : `staff`.
3. Groupe **secondaire** : `developers`.

## Contraintes

- `useradd` (et `groupadd`) ; `usermod -aG` pour ajouter un groupe secondaire
  sans écraser les autres (le `-a` est vital).
- La validation lit l'**état réel** (`getent`, `id`), pas la commande tapée.

## Validation

```bash
dsoxlab check l2-user-lifecycle
```
