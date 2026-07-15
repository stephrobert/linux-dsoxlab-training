# Lab — liens physiques et symboliques

> Prépare l'espace : `dsoxlab run l1-links-hard-sym`

## Rappel

[**Naviguer dans les fichiers sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/)

Un **lien physique** (`ln cible nom`) est un autre nom pour le même inode : mêmes
données, compteur de liens qui augmente, et il survit à la suppression de
l'original. Un **lien symbolique** (`ln -s cible nom`) stocke un chemin vers la
cible ; il peut traverser les systèmes de fichiers et pointer un répertoire, mais
casse si la cible bouge. `ls -li` révèle l'inode et le compteur de liens.

## Objectifs

- `copie-dure.txt` — lien physique vers `original.txt` (`ln`).
- `raccourci.txt` — lien symbolique vers `original.txt` (`ln -s`).
- répertoire `data/` + lien symbolique `lien-data` vers lui.

## Valider

```bash
dsoxlab check l1-links-hard-sym
```
