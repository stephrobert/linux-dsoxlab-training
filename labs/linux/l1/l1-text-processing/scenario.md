# Context — turn a raw record file into facts

You have `ventes.csv`, eight `;`-separated records of the shape
`date;region;product;amount`. With the text toolbox — `cut`, `sort`, `uniq`,
`awk`, `sed` — turn it into four exact artifacts: the distinct regions, the count
of sales per region, the grand total, and a comma-separated version.

Your mission — produce, in the work directory:

1. `regions.txt` — the **distinct** regions, sorted.
2. `nb-par-region.txt` — the **count of sales per region**.
3. `total.txt` — the **sum** of the amount column.
4. `en-csv.txt` — the same file with `;` replaced by `,`.

Each tool does one job: `cut` slices a column, `sort -u` deduplicates,
`uniq -c` counts runs, `awk` sums a field, `sed` rewrites a delimiter.

Method in the companion guides:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/traiter-texte/cut-tr-paste/
