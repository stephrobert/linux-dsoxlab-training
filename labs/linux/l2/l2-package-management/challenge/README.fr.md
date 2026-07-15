# Challenge — l2-package-management

## Mission

Amène la machine à l'état logiciel cible.

## Objectif (état attendu)

1. Le paquet **`tree`** est **installé**.
2. Le paquet **`zip`** est **retiré**.
3. La commande `tree` est disponible.

## Contraintes

- `dnf install` / `dnf remove` ; vérifie avec `rpm -q`. La validation lit la
  **base RPM** (état réel), pas la commande tapée.

## Validation

```bash
dsoxlab check l2-package-management
```
