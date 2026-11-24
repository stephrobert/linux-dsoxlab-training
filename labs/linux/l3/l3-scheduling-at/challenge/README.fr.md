# Exécuter quelque chose une fois, plus tard

## La situation

Cron répète une tâche selon un planning. Mais parfois tu veux qu'une commande
s'exécute **une seule fois**, à une heure précise, et plus jamais — une
maintenance ce soir, un rappel dans une heure. C'est le rôle d'**`at`**.

L'idée : une tâche ponctuelle est mise en file d'attente, puis confiée à un démon
qui l'exécutera à l'heure dite et l'oubliera. Contrairement à cron, elle ne se
répète pas, et rien ne s'exécutera si ce démon ne tourne pas.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/

## Ce qui est demandé

### Mission

Planifie `touch /run/rapport.done` pour s'exécuter une fois, plus tard, avec `at`.

### Objectif (état attendu)

1. `atd` tourne.
2. Une tâche est en file (`atq` non vide), planifiée dans le futur.
3. La tâche en file exécute `touch /run/rapport.done` (`at -c <n>`).

### Contraintes

- Utilise `at` (pas cron) : la tâche doit être ponctuelle.
- On lit `atq` et le script de la tâche, pas ton historique.

### Validation

```bash
dsoxlab check l3-scheduling-at
```
