# Challenge — l1-tar-archives

## Mission

À partir de `rapport.txt`, `config.yaml`, `notes.txt` (dans `challenge/work/`),
produis quatre artefacts avec `tar`.

## Objectif (fichiers à produire)

1. `docs.tar.gz` — archive **gzip** des trois fichiers.
2. `liste.txt` — le **listing** de l'archive.
3. `extrait/rapport.txt` — **uniquement** `rapport.txt`, extrait dans `extrait/`.
4. `docs.tar.bz2` — archive **bzip2** des trois fichiers.

## Contraintes

- Uniquement `tar` (et `mkdir` pour le dossier d'extraction) : pas d'archiveur graphique.
- La validation **ouvre réellement les archives** et vérifie leurs membres et la
  compression — taper la bonne commande sans produire le bon fichier échoue.

## Validation

```bash
dsoxlab check l1-tar-archives
```
