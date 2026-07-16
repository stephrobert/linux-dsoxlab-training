# Challenge — l3-scheduling-at

## Mission

Planifie `touch /run/rapport.done` pour s'exécuter une fois, plus tard, avec `at`.

## Objectif (état attendu)

1. `atd` tourne.
2. Une tâche est en file (`atq` non vide), planifiée dans le futur.
3. La tâche en file exécute `touch /run/rapport.done` (`at -c <n>`).

## Contraintes

- Utilise `at` (pas cron) : la tâche doit être ponctuelle.
- On lit `atq` et le script de la tâche, pas ton historique.

## Validation

```bash
dsoxlab check l3-scheduling-at
```
