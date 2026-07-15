# Lab — Redirections et pipes

> Prépare l'espace : `dsoxlab run l1-redirections-pipes`

## Rappel

[**Redirections et pipes sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/)

Chaque commande a trois flux : l'entrée standard (0), la sortie standard (1) et
la sortie d'erreur (2). `>` envoie la sortie standard dans un fichier (écrase),
`>>` ajoute, `2>` envoie la sortie d'erreur, `2>&1` fusionne l'erreur dans la
sortie standard, et `|` passe la sortie d'une commande à la suivante. Se tromper
d'opérateur perd des données en silence.

## Objectifs

À partir de `journal.log`, produis quatre fichiers :

- `total.txt` — le nombre de lignes de `journal.log` (redirection).
- `erreurs.txt` — uniquement les lignes `ERROR` (pipe + redirection).
- `stderr.txt` — le message d'erreur d'une commande qui échoue (`2>`).
- `tout.txt` — la sortie standard **et** l'erreur d'une commande, fusionnées (`2>&1`).

## Valider

```bash
dsoxlab check l1-redirections-pipes
```
