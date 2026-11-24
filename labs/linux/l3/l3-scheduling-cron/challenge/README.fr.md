# Lancer une tâche selon un horaire

## La situation

Un script de rapport (`/usr/local/bin/report.sh`) doit tourner **chaque jour à
02:30**, sans intervention. Personne ne va le lancer à la main — c'est le rôle de
**cron**.

L'idée : une ligne cron décrit d'abord *quand*, à travers plusieurs champs de
temps, puis *quoi*. Sa forme exacte n'est pas la même selon qu'elle est posée
dans la crontab d'un utilisateur ou dans un fichier système.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/

## Ce qui est demandé

### Mission

Planifie `/usr/local/bin/report.sh` pour qu'il tourne chaque jour à 02:30.

### Objectif (état attendu)

1. Une entrée cron lance `report.sh`.
2. La planification est **02:30 quotidien** (`30 2 * * *`).

### Contraintes

- N'importe quel mécanisme cron valide (`/etc/cron.d/`, `/etc/crontab`,
  `crontab -e`). La validation lit la **planification réelle**, pas la commande.

### Validation

```bash
dsoxlab check l3-scheduling-cron
```
