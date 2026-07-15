# Challenge — l1-grep-regex

## Mission

From `acces.log` (in `challenge/work/`), produce four files with
`grep` and regular expressions.

## Goal (files to produce)

1. `erreurs5xx.txt` — only the lines whose **HTTP code is 5xx**.
2. `sans-200.txt` — all lines **except** the `200` ones.
3. `ips.txt` — the **distinct IPs**, sorted.
4. `nb-post.txt` — the **number** of POST requests.

## Constraints

- Only `grep` (and `sort -u` to deduplicate the IPs): no editor.
- Validation reads the **real content** of the files, not the command typed, and
  recomputes each expected result from `acces.log`.

## Validation

```bash
dsoxlab check l1-grep-regex
```
