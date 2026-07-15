# Lab — grep et expressions régulières

> Prépare l'espace : `dsoxlab run l1-grep-regex`

## Rappel

[**Filtrer du texte avec grep sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/)

`grep MOTIF fichier` garde les lignes qui correspondent. Les expressions
régulières rendent le motif précis : `^` et `$` ancrent au début/à la fin d'une
ligne, `[0-9]` est une classe de caractères, `-E` active le regex étendu, `-v`
inverse le filtre, `-o` n'affiche que le texte correspondant, et `-c` compte les
lignes au lieu de les afficher.

## Objectifs

À partir de `acces.log`, produis quatre fichiers :

- `erreurs5xx.txt` — les lignes dont le code HTTP est un 5xx (`grep -E ' 5[0-9][0-9]$'`).
- `sans-200.txt` — toutes les lignes sauf les 200 (`grep -v`).
- `ips.txt` — les IP clientes distinctes, triées (`grep -oE ... | sort -u`).
- `nb-post.txt` — le nombre de requêtes POST (`grep -c`).

## Valider

```bash
dsoxlab check l1-grep-regex
```
