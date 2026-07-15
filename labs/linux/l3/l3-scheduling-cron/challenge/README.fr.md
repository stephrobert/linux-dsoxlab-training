# Challenge — l3-scheduling-cron

## Mission

Planifie `/usr/local/bin/report.sh` pour qu'il tourne chaque jour à 02:30.

## Objectif (état attendu)

1. Une entrée cron lance `report.sh`.
2. La planification est **02:30 quotidien** (`30 2 * * *`).

## Contraintes

- N'importe quel mécanisme cron valide (`/etc/cron.d/`, `/etc/crontab`,
  `crontab -e`). La validation lit la **planification réelle**, pas la commande.

## Validation

```bash
dsoxlab check l3-scheduling-cron
```
