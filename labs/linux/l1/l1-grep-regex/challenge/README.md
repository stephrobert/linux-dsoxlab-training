# Read an access log with grep alone

## The situation

You have `acces.log`, ten lines of the shape `IP - METHOD /path CODE`. Using only
`grep` and regular expressions, extract four exact facts into separate files: the
server errors, everything that is not a success, the distinct client IPs, and how
many POST requests there were.

The point: the same file yields four different facts depending on how you
question it. Selecting lines, excluding them, extracting only part of a line, or
returning nothing but a number are four distinct uses of a single tool.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/regex-basics/

## What is asked

### Mission

From `acces.log` (in `challenge/work/`), produce four files with
`grep` and regular expressions.

### Goal (files to produce)

1. `erreurs5xx.txt` — only the lines whose **HTTP code is 5xx**.
2. `sans-200.txt` — all lines **except** the `200` ones.
3. `ips.txt` — the **distinct IPs**, sorted.
4. `nb-post.txt` — the **number** of POST requests.

### Constraints

- Only `grep` (and `sort -u` to deduplicate the IPs): no editor.
- Validation reads the **real content** of the files, not the command typed, and
  recomputes each expected result from `acces.log`.

### Validation

```bash
dsoxlab check l1-grep-regex
```
