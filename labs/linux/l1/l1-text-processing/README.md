# Lab — cut, sort, uniq, sed, awk

> Prepare the workspace: `dsoxlab run l1-text-processing`

## Recap

[**Process text on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/traiter-texte/cut-tr-paste/)

`cut -d';' -fN` extracts column N, `sort` orders lines (`-u` also deduplicates),
`uniq -c` counts consecutive duplicates (so it needs a sorted input), `awk`
processes fields with a program (`-F';'` sets the separator), and `sed` edits a
stream with substitutions (`s/old/new/g`).

## Objectives

From `ventes.csv` (`date;region;product;amount`), produce four files:

- `regions.txt` — distinct regions, sorted (`cut` + `sort -u`).
- `nb-par-region.txt` — sales per region (`cut` + `sort` + `uniq -c`).
- `total.txt` — sum of the amount column (`awk`).
- `en-csv.txt` — the file with `;` replaced by `,` (`sed`).

## Validate

```bash
dsoxlab check l1-text-processing
```
