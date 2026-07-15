# Lab — grep and regular expressions

> Prepare the workspace: `dsoxlab run l1-grep-regex`

## Recap

[**Filter text with grep on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/)

`grep PATTERN file` keeps the lines that match. Regular expressions make the
pattern precise: `^` and `$` anchor to the start/end of a line, `[0-9]` is a
character class, `-E` enables extended regex, `-v` inverts the match, `-o` prints
only the matched text, and `-c` counts matching lines instead of printing them.

## Objectives

From `acces.log`, produce four files:

- `erreurs5xx.txt` — lines whose HTTP code is a 5xx (`grep -E ' 5[0-9][0-9]$'`).
- `sans-200.txt` — every line except the 200 ones (`grep -v`).
- `ips.txt` — the distinct client IPs, sorted (`grep -oE ... | sort -u`).
- `nb-post.txt` — the number of POST requests (`grep -c`).

## Validate

```bash
dsoxlab check l1-grep-regex
```
