# Mettre un projet sous gestion de version

## La situation

Démarre un dépôt Git de zéro, enregistre deux commits utiles, et ouvre une
branche pour travailler une fonctionnalité sans toucher à la ligne principale.
C'est la boucle que tu répètes sur chaque vrai projet.

Les tests inspectent l'**état du dépôt**, commits, fichiers suivis et branches,
pas les commandes que tu as tapées pour y arriver.

Si Git réclame une identité, règle-la une fois :
`git config user.name "Toi"` et `git config user.email "toi@example.com"`.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/developper/version/git/bases-git/

## Ce qui est demandé

### Mission

Dans `challenge/work/`, crée un dépôt Git `monprojet/` et fais-le vivre.

### Objectif (état attendu du dépôt)

1. `monprojet/` est un dépôt Git (`git init`).
2. Au moins **2 commits**.
3. `README.md` et `app.sh` sont **suivis**.
4. Une branche `feature` existe.
5. Arbre de travail **propre** (tout commité).

### Contraintes

- `git init`, `git add`, `git commit`, `git branch`/`git switch -c`. Pas de dépôt distant.
- La validation interroge l'**état du dépôt** (log, ls-files, branch, status),
  pas les commandes tapées.

### Validation

```bash
dsoxlab check l1-git-basics
```
