# Du travail récurrent, façon systemd

## La situation

Une tâche de maintenance doit tourner régulièrement. Sur un hôte systemd,
l'approche moderne est une **unité timer** : un `.timer` qui déclenche un
`.service`, avec journalisation, dépendances et gestion par `systemctl` — et ça
revient après un reboot.

L'idée : le travail à faire et le moment où il se déclenche sont décrits dans
deux unités séparées, la seconde portant le planning. Et comme toute unité
systemd, un timer ne revient après un redémarrage que s'il a été activé pour
cela.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/

## Ce qui est demandé

### Mission

Planifie une tâche récurrente avec un timer systemd (`labbackup`).

### Objectif (état attendu)

1. `/etc/systemd/system/labbackup.service` et `labbackup.timer` existent.
2. Le timer a un planning `OnCalendar=`.
3. `labbackup.timer` est activé (enabled) et actif (`systemctl is-enabled/is-active`).

### Contraintes

- Utilise un timer systemd (pas cron/at). `daemon-reload` après création des unités.
- On lit les fichiers d'unité et l'état enabled/actif du timer.

### Validation

```bash
dsoxlab check l3-scheduling-timers
```
