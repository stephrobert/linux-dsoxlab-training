# Challenge — l1-links-hard-sym

## Mission

À partir de `original.txt` (dans `challenge/work/`), crée deux types de liens.

## Objectif

1. `copie-dure.txt` — **lien physique** vers `original.txt` (même inode).
2. `raccourci.txt` — **lien symbolique** vers `original.txt`.
3. `data/` (répertoire) + `lien-data` — **lien symbolique** vers `data/`.

## Contraintes

- `ln` pour le lien physique, `ln -s` pour le symbolique. Pas de `cp`.
- La validation lit l'**inode**, le **compteur de liens** et la **cible** réelle
  (`readlink`) : une copie échoue le test.

## Validation

```bash
dsoxlab check l1-links-hard-sym
```
