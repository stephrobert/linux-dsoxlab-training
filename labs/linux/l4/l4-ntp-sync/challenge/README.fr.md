# Challenge — l4-ntp-sync

## Mission

L'horloge est désynchronisée : mauvais fuseau, NTP désactivé, `chronyd` arrêté.
Remets-la d'aplomb et fais-la persister.

## Objectif (état attendu)

1. Le fuseau est `Europe/Paris`.
2. Le NTP est activé (`timedatectl show -p NTP --value` → `yes`).
3. `chronyd` **tourne et est activé**.

## Contraintes

- La persistance compte : un `chronyd` qui tourne sans être `enabled` échoue à la
  validation. On lit l'état **actif** du service et `timedatectl`, pas ton
  historique.

## Validation

```bash
dsoxlab check l4-ntp-sync
```
