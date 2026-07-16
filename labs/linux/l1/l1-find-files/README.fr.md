# Lab — localiser des fichiers avec find

> Préparer : `dsoxlab run l1-find-files` (copie `projet.tar.gz` dans le work dir)

## Rappel

[**find sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/)

`find <chemin> <prédicats>` parcourt un arbre et filtre : `-name '*.log'` (glob),
`-size +1000c` (octets ; `k`/`M` pour Kio/Mio), `-perm 600` (mode exact),
`-type f` (fichiers réguliers). Récursif par défaut. `tar xpzf` extrait en
préservant les permissions stockées.

## Objectifs (fichiers à produire dans le work dir)

- `logs.txt` — tous les chemins `*.log` sous `projet/` ;
- `gros.txt` — les fichiers réguliers de plus de 1000 octets ;
- `prives.txt` — les fichiers réguliers aux permissions exactement `600`.

## Valider

```bash
dsoxlab check l1-find-files
```
