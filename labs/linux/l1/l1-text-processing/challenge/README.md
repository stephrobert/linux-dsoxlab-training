# Turn a raw record file into facts

## The situation

You have `ventes.csv`, eight `;`-separated records of the shape
`date;region;product;amount`. With the shell's text toolbox alone, turn it into
four exact artifacts: the distinct regions, the count of sales per region, the
grand total, and a comma-separated version.

The point: every tool in the chain does exactly one job. The whole difficulty is
picking the right one for each question, and chaining them in the right order.

Method in the companion guides:
https://www.stephane-robert.info/en/docs/linux/fundamentals/files-and-text/filter-text/

## What is asked

### Mission

From `ventes.csv` (in `challenge/work/`, format `date;region;produit;montant`),
produce four files with `cut`, `sort`, `uniq`, `awk` and `sed`.

### Goal (files to produce)

1. `regions.txt` — the **distinct** regions, sorted.
2. `nb-par-region.txt` — the **number of sales per region**.
3. `total.txt` — the **sum** of the amount column.
4. `en-csv.txt` — the file with `;` replaced by `,`.

### Constraints

- Only the text tools: no editor, no spreadsheet.
- Validation reads the **actual content** of the files and recomputes each
  expected result from `ventes.csv`.

### Validation

```bash
dsoxlab check l1-text-processing
```
