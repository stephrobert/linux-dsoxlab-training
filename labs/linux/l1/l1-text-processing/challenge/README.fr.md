# Transformer un fichier brut en faits

## La situation

Tu as `ventes.csv`, huit enregistrements séparés par `;` de la forme
`date;region;produit;montant`. Avec la seule boîte à outils texte du shell,
transforme-le en quatre artefacts précis : les régions distinctes, le nombre de
ventes par région, le total général, et une version séparée par des virgules.

L'idée : chaque outil de la chaîne ne sait faire qu'une chose. Toute la
difficulté est de choisir le bon pour chaque question, et de les enchaîner dans
le bon ordre.

Méthode dans les guides compagnons :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/

## Ce qui est demandé

### Mission

À partir de `ventes.csv` (dans `challenge/work/`, format `date;region;produit;montant`),
produis quatre fichiers avec `cut`, `sort`, `uniq`, `awk` et `sed`.

### Objectif (fichiers à produire)

1. `regions.txt` — les régions **distinctes**, triées.
2. `nb-par-region.txt` — le **nombre de ventes par région**.
3. `total.txt` — la **somme** de la colonne montant.
4. `en-csv.txt` — le fichier avec `;` remplacé par `,`.

### Contraintes

- Uniquement les outils texte : pas d'éditeur, pas de tableur.
- La validation lit le **contenu réel** des fichiers et recalcule chaque attendu
  depuis `ventes.csv`.

### Validation

```bash
dsoxlab check l1-text-processing
```
