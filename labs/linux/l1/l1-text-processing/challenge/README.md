# Challenge — l1-text-processing

## Mission

À partir de `ventes.csv` (dans `challenge/work/`, format `date;region;produit;montant`),
produis quatre fichiers avec `cut`, `sort`, `uniq`, `awk` et `sed`.

## Objectif (fichiers à produire)

1. `regions.txt` — les régions **distinctes**, triées.
2. `nb-par-region.txt` — le **nombre de ventes par région**.
3. `total.txt` — la **somme** de la colonne montant.
4. `en-csv.txt` — le fichier avec `;` remplacé par `,`.

## Contraintes

- Uniquement les outils texte : pas d'éditeur, pas de tableur.
- La validation lit le **contenu réel** des fichiers et recalcule chaque attendu
  depuis `ventes.csv`.

## Validation

```bash
dsoxlab check l1-text-processing
```
