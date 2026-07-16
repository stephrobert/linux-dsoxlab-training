# Lab — répertoire collaboratif avec set-GID

> Préparer : `dsoxlab provision` puis `dsoxlab run l2-collaborative-setgid`

## Rappel

[**Permissions & propriété sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/)

Sur un répertoire, le bit **set-GID** (`chmod g+s` ou le `2` de tête dans `2775`)
fait hériter les nouveaux fichiers du groupe du répertoire. Combiné au bon groupe
et à `g+w`, c'est un dossier collaboratif : `/srv/partage` de groupe `devteam`,
mode `2775`. `ls -ld` montre un `s` à la place de l'exécution du groupe.

## Objectifs

- `/srv/partage` est un répertoire, groupe `devteam` ;
- son mode a le bit set-GID et est accessible en écriture au groupe (`2775`) ;
- un fichier créé dedans par un membre de `devteam` hérite du groupe `devteam`.

## Valider

```bash
dsoxlab check l2-collaborative-setgid
```
