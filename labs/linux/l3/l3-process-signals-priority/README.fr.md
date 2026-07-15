# Lab — priorité de processus avec Nice

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-process-signals-priority`

## Rappel

[**Processus sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/comprendre-processus/)

Les valeurs de nice vont de `-20` (priorité max) à `19` (min). `nice -n N cmd`
démarre un processus à une priorité, `renice N -p PID` change celle d'un
processus en cours. Pour un service, `Nice=` dans l'unit (ou un drop-in
`systemctl edit`) le rend durable. Les signaux — `kill -TERM/-HUP/-9` — pilotent
les processus en cours. `ps -o ni -p <pid>` montre le nice courant.

## Objectifs

- `labworker.service` tourne à **nice 10** (drop-in `Nice=10`, reload, restart) ;
- prouvé sur le processus live et dans la config de l'unit.

## Valider

```bash
dsoxlab check l3-process-signals-priority
```
