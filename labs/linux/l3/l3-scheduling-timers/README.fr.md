# Lab — planification récurrente avec un timer systemd

> Préparer : `dsoxlab provision` puis `dsoxlab run l3-scheduling-timers`

## Rappel

[**Les timers systemd sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/)

Une unité `.timer` déclenche un `.service` selon un planning. Le service est
souvent `Type=oneshot` ; le `[Timer]` a `OnCalendar=` et son `[Install]` a
`WantedBy=timers.target`. `systemctl daemon-reload` prend en compte les nouvelles
unités ; `enable --now` le démarre et le rend persistant. `systemctl list-timers`
montre la prochaine exécution.

## Objectifs

- `labbackup.service` et `labbackup.timer` existent sous `/etc/systemd/system/` ;
- le timer a un planning `OnCalendar=` ;
- `labbackup.timer` est activé (enabled) et actif.

## Valider

```bash
dsoxlab check l3-scheduling-timers
```
