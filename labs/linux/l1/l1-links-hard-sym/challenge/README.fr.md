# Deux façons de pointer un fichier

## La situation

Tu as `original.txt`. Un **lien physique** est un second nom pour exactement le
même fichier (même inode, mêmes données) : supprime l'original et les données
survivent. Un **lien symbolique** est un petit pointeur qui stocke un chemin ;
si la cible bouge, il pend dans le vide. Apprends à faire les deux, et un lien
symbolique vers un répertoire aussi.

L'idée : les deux se créent avec le même outil, et une fois posés, rien ne les
distingue dans un listing ordinaire. Il te faudra donc aussi savoir quoi
demander au système pour prouver lequel est lequel.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/liens-fichiers/

## Ce qui est demandé

### Mission

À partir de `original.txt` (dans `challenge/work/`), crée deux types de liens.

### Objectif

1. `copie-dure.txt` — **lien physique** vers `original.txt` (même inode).
2. `raccourci.txt` — **lien symbolique** vers `original.txt`.
3. `data/` (répertoire) + `lien-data` — **lien symbolique** vers `data/`.

### Contraintes

- `ln` pour le lien physique, `ln -s` pour le symbolique. Pas de `cp`.
- La validation lit l'**inode**, le **compteur de liens** et la **cible** réelle
  (`readlink`) : une copie échoue le test.

### Validation

```bash
dsoxlab check l1-links-hard-sym
```
