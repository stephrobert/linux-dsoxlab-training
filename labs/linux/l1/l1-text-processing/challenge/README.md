# Challenge — l1-text-processing

## Mission

From `ventes.csv` (in `challenge/work/`, format `date;region;produit;montant`),
produce four files with `cut`, `sort`, `uniq`, `awk` and `sed`.

## Goal (files to produce)

1. `regions.txt` — the **distinct** regions, sorted.
2. `nb-par-region.txt` — the **number of sales per region**.
3. `total.txt` — the **sum** of the amount column.
4. `en-csv.txt` — the file with `;` replaced by `,`.

## Constraints

- Only the text tools: no editor, no spreadsheet.
- Validation reads the **actual content** of the files and recomputes each
  expected result from `ventes.csv`.

## Validation

```bash
dsoxlab check l1-text-processing
```
