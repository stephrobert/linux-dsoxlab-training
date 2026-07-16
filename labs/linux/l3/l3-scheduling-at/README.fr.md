# Lab — planification ponctuelle avec at

> Préparer : `dsoxlab provision` puis `dsoxlab run l3-scheduling-at`

## Rappel

[**at sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/)

`at` met en file une commande à exécuter **une seule fois** plus tard, gérée par
`atd`. Passe la commande sur l'entrée standard : `echo 'cmd' | at <heure>`. `atq`
liste les tâches en attente, `at -c <n>` affiche le script d'une tâche, `atrm <n>`
la supprime. Contrairement à cron, elle ne se répète pas.

## Objectifs

- `atd` tourne ;
- une tâche est en file (`atq` non vide) ;
- cette tâche exécute `touch /run/rapport.done`.

## Valider

```bash
dsoxlab check l3-scheduling-at
```
