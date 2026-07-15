# Challenge — l1-permissions-ugo

## Mission

Les fichiers de `challenge/work/` sont tous en `0644`. Pose les bons bits.

## Objectif

1. `secret.txt` → `0600`.
2. `deploy.sh` → `0750`.
3. `notes.txt` → `0640`.
4. `prive/` → répertoire en `0700` (à créer).

## Contraintes

- Uniquement `chmod` (et `mkdir`) : pas besoin de `sudo`, tu es propriétaire.
- La validation lit les **bits réels** via `stat`, pas la commande tapée.

## Validation

```bash
dsoxlab check l1-permissions-ugo
```
