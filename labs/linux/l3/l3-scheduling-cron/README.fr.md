# Lab — planifier une tâche avec cron

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-scheduling-cron`

## Rappel

[**cron sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/)

Une ligne cron a cinq champs de temps — `minute heure jour-du-mois mois
jour-de-semaine` — puis la commande (les fichiers système `/etc/cron.d/` et
`/etc/crontab` ajoutent un champ utilisateur avant la commande). `30 2 * * *`
c'est 02:30 chaque jour. `crontab -e/-l` gère la table d'un utilisateur ;
`/etc/cron.d/` contient les tâches système. Le service `crond` doit tourner.

## Objectifs

- `/usr/local/bin/report.sh` planifié **chaque jour à 02:30** (`30 2 * * *`) ;
- via n'importe quel vrai mécanisme cron.

## Valider

```bash
dsoxlab check l3-scheduling-cron
```
