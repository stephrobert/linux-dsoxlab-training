# Lab — un premier script Bash

> Prépare l'espace : `dsoxlab run l1-bash-script`

## Rappel

[**Écrire son premier script sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/scripts-bash/premier-script/)

Un script commence par un shebang (`#!/usr/bin/env bash`) et doit être exécutable
(`chmod +x`). `$1` est le premier argument. Une boucle `while read` parcourt un
fichier ligne par ligne, des variables accumulent les compteurs, `if` teste une
condition, et `exit <n>` fixe le code de retour que l'appelant vérifie avec `$?`.

## Objectifs

Écris `rapport.sh` pour que `./rapport.sh serveurs.txt` :

- parcoure les lignes et compte UP / DOWN dans des variables ;
- affiche `UP=<n>` et `DOWN=<n>` ;
- sorte en erreur si un hôte est down, `0` sinon.

## Valider

```bash
dsoxlab check l1-bash-script
```
