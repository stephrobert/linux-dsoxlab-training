# Contexte — mettre un projet sous gestion de version

Démarre un dépôt Git de zéro, enregistre deux commits utiles, et ouvre une
branche pour travailler une fonctionnalité sans toucher à la ligne principale.
C'est la boucle que tu répètes sur chaque vrai projet.

Ta mission — dans le répertoire de travail, crée un dépôt `monprojet/` tel que :

1. c'est un dépôt Git (`git init`) ;
2. il a **au moins deux commits** ;
3. deux fichiers sont suivis : `README.md` et `app.sh` ;
4. une branche nommée `feature` existe ;
5. l'arbre de travail est **propre** (rien qui traîne non commité).

L'idée : `git init` crée le dépôt, `git add` indexe, `git commit` enregistre,
`git branch` / `git switch -c` ouvre une ligne de travail. Les tests inspectent
l'état du dépôt — commits, fichiers suivis, branches — pas les commandes tapées.

Si Git réclame une identité, règle-la une fois :
`git config user.name "Toi"` et `git config user.email "toi@example.com"`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/developper/version/git/bases-git/
