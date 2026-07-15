# Lab — tar, gzip, bzip2

> Prépare l'espace : `dsoxlab run l1-tar-archives`

## Rappel

[**Archives et compression sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/)

`tar` regroupe des fichiers dans une seule archive ; la compression est une
option à part : `z` pour gzip, `j` pour bzip2. Verbes courants : `c` créer, `t`
lister, `x` extraire. `-f` nomme le fichier, `-C` fixe le répertoire
d'extraction, et nommer un membre n'extrait que celui-ci.

## Objectifs

À partir de `rapport.txt`, `config.yaml`, `notes.txt`, produis :

- `docs.tar.gz` — archive gzip (`tar czf`).
- `liste.txt` — le listing de l'archive (`tar tzf`).
- `extrait/rapport.txt` — uniquement `rapport.txt`, extrait dans `extrait/` (`tar xzf … -C`).
- `docs.tar.bz2` — archive bzip2 (`tar cjf`).

## Valider

```bash
dsoxlab check l1-tar-archives
```
