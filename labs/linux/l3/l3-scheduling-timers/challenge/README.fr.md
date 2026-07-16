# Challenge — l3-scheduling-timers

## Mission

Planifie une tâche récurrente avec un timer systemd (`labbackup`).

## Objectif (état attendu)

1. `/etc/systemd/system/labbackup.service` et `labbackup.timer` existent.
2. Le timer a un planning `OnCalendar=`.
3. `labbackup.timer` est activé (enabled) et actif (`systemctl is-enabled/is-active`).

## Contraintes

- Utilise un timer systemd (pas cron/at). `daemon-reload` après création des unités.
- On lit les fichiers d'unité et l'état enabled/actif du timer.

## Validation

```bash
dsoxlab check l3-scheduling-timers
```
