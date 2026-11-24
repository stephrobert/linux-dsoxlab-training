# Intégrer un nouvel utilisateur, au détail près

## La situation

Un nouveau développeur arrive. Tu dois créer son compte avec des attributs
précis — le genre de tâche notée à la lettre au RHCSA : un UID fixe, un vrai
shell de connexion, un home, le bon groupe **primaire** et le bon groupe
**secondaire**.

L'idée : fixer l'identité d'un compte au moment de sa création n'est pas la même
chose que l'ajuster ensuite. Et l'erreur classique tient dans une nuance :
ajouter un groupe secondaire sans effacer ceux que l'utilisateur avait déjà.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

## Ce qui est demandé

### Mission

Crée le compte `alice` avec des attributs exacts (crée les groupes si besoin).

### Objectif (état attendu)

1. `alice` existe, **UID 1500**, home `/home/alice`, shell `/bin/bash`.
2. Groupe **primaire** : `staff`.
3. Groupe **secondaire** : `developers`.

### Contraintes

- `useradd` (et `groupadd`) ; `usermod -aG` pour ajouter un groupe secondaire
  sans écraser les autres (le `-a` est vital).
- La validation lit l'**état réel** (`getent`, `id`), pas la commande tapée.

### Validation

```bash
dsoxlab check l2-user-lifecycle
```
