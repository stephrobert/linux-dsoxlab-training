# Empaqueter des fichiers avec tar

## La situation

Tu as trois fichiers, `rapport.txt`, `config.yaml` et `notes.txt`, et tu dois les
transformer en archives, les inspecter, puis en ressortir un seul fichier sans
tout dépaqueter. C'est le pain quotidien des sauvegardes et des transferts.

L'idée : `tar` ne fait que regrouper, et la compression est un service qu'il
délègue à un compresseur externe, gzip ou bzip2 selon ce qu'on lui demande.
Créer, lister, extraire, choisir la destination et n'extraire qu'un seul membre
sont autant d'usages du même outil.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/

## Ce qui est demandé

### Mission

À partir de `rapport.txt`, `config.yaml`, `notes.txt` (dans `challenge/work/`),
produis quatre artefacts avec `tar`.

### Objectif (fichiers à produire)

1. `docs.tar.gz` — archive **gzip** des trois fichiers.
2. `liste.txt` — le **listing** de l'archive.
3. `extrait/rapport.txt` — **uniquement** `rapport.txt`, extrait dans `extrait/`.
4. `docs.tar.bz2` — archive **bzip2** des trois fichiers.

### Contraintes

- Uniquement `tar` (et `mkdir` pour le dossier d'extraction) : pas d'archiveur graphique.
- La validation **ouvre réellement les archives** et vérifie leurs membres et la
  compression — taper la bonne commande sans produire le bon fichier échoue.

### Validation

```bash
dsoxlab check l1-tar-archives
```
