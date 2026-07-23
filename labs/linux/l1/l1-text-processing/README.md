# Lab — cut, sort, uniq, sed, awk

## Reminder

[**Transforming text on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/transformer-texte/)

`cut -d<sep> -f<N>` extracts column N from a file with delimited fields. `sort`
orders the lines (`-n` for a numeric sort, `-u` to deduplicate along the way),
`uniq -c` counts **consecutive** repetitions and therefore requires an input that
is already sorted. `tr` converts or deletes characters from standard input, `wc`
measures, `sed 's/pattern/replacement/g'` rewrites a stream, and `awk -F<sep>`
reasons field by field and knows how to compute. They all compose through pipes,
and none of them modifies the source file.

Additional guides: [sorting and counting](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/trier-compter/),
[sed](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/sed/) and [awk](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/awk/).

## The course

The examples below work on a fictitious record of interventions, with fields
separated by colons: the challenge will give you another file, another
separator, other columns and other computations. The point is to learn the
chaining, not to copy a line.

All the outputs shown were produced on Ubuntu 24.04 with GNU coreutils 9.4, GNU
sed 4.9 and GNU Awk 5.2.1. Since the example file is given in full, you can
replay each command and find the same lines again.

### The demonstration setup

```bash
mkdir -p /tmp/demo-texte && cd /tmp/demo-texte
cat > interventions.txt <<'EOF'
2026-03-02:reseau:Adrien:35
2026-03-02:stockage:elodie:120
2026-03-03:sauvegarde:bruno:9
2026-03-03:sauvegarde:Adrien:10
2026-03-04:messagerie:Zoe:5
2026-03-04:stockage:elodie:12
2026-03-05:reseau:Émile:90

2026-03-05:reseau:bruno:10
2026-03-06:messagerie:adrien:15
2026-03-07:stockage:Émile:60
2026-03-08:reseau:elodie:120
2026-03-08:sauvegarde:elodie:20
2026-03-09:reseau:Adrien:5

2026-03-10:messagerie:bruno:9
2026-03-11:reseau:Zoe:30
2026-03-12:stockage:adrien:9
2026-03-13:reseau:bruno:12
2026-03-14:sauvegarde:Zoe:35
EOF
```

The format is `date:service:agent:minutes`. The two empty lines are deliberate:
real exports always contain some, and they slip into the counts if you forget
them.

```bash
wc -l interventions.txt      # lines, empty lines included
grep -c . interventions.txt  # lines actually filled in
```

```text
20 interventions.txt
18
```

`wc -l` counts the line endings without judging the content; `grep -c .` only
keeps the lines that have at least one character. The gap of two is the empty
ones.

### Cutting out a column with `cut`

`cut` needs two things: the delimiter (`-d`) and the field or fields (`-f`).

```bash
cut -d: -f2 interventions.txt | head -8
```

```text
reseau
stockage
sauvegarde
sauvegarde
messagerie
stockage
reseau

```

The empty line goes through the cutting without a hitch: `cut` filters nothing,
it cuts. Several fields are asked for with a list (`-f2,4`) or with a range
(`-f3-` means "from field 3 to the end"), and `cut` copies the same delimiter
back on output:

```bash
cut -d: -f2,4 interventions.txt | head -4
```

```text
reseau:35
stockage:120
sauvegarde:9
sauvegarde:10
```

### Sorting and deduplicating, and the trap of the alphabetical sort

`sort -u` sorts and removes the duplicates in one pass. On the column of
services:

```bash
cut -d: -f2 interventions.txt | sort -u
```

```text

messagerie
reseau
sauvegarde
stockage
```

The first line of the result is empty: for `sort`, an empty line is a value like
any other. Insert `grep .` into the pipe to rule it out.

Trap number one comes next. Without an option, `sort` compares **text**:

```bash
cut -d: -f4 interventions.txt | grep . | sort -u  | tr '\n' ' '   # text
cut -d: -f4 interventions.txt | grep . | sort -nu | tr '\n' ' '   # numbers
```

```text
10 12 120 15 20 30 35 5 60 9 90
5 9 10 12 15 20 30 35 60 90 120
```

`10` comes before `9` because the character `1` precedes the character `9`. As
soon as a column contains numbers, `-n` is not a convenience option. The same
trap is set when you sort the whole file on a column, with `-t` for the
delimiter and `-k` for the field: `sort -t: -k4 -rn` does bring the 120-minute
interventions to the top, whereas `sort -t: -k4 -r` puts `90` first.

Second trap, less well known: **the locale changes the order**. The sort follows
`LC_COLLATE`, here `fr_FR.UTF-8`, which files uppercase letters and accents like
a dictionary. `LC_ALL=C` forces the byte order:

```bash
cut -d: -f3 interventions.txt | grep . | sort -u          # fr_FR.UTF-8
```

```text
adrien
Adrien
bruno
elodie
Émile
Zoe
```

```bash
cut -d: -f3 interventions.txt | grep . | LC_ALL=C sort -u # ASCII bytes
```

```text
Adrien
Zoe
adrien
bruno
elodie
Émile
```

The same six values, a different order: in `C`, all the uppercase letters come
before all the lowercase ones, and `Émile` ends up last because its UTF-8 bytes
are worth more than those of the ASCII letters. In a script whose output is
compared against an expected result, or before a `comm` that requires two files
sorted identically, set `LC_ALL=C` on both sides. Note in passing that `Adrien`
and `adrien` remain two distinct values in both orders: `sort -u` compares
strings, not identities (`sort -uf` folds the case).

### Counting with `uniq -c`, and why sorting is mandatory

`uniq` only looks at **the previous line**. On unsorted data, it therefore only
groups what touches:

```bash
cut -d: -f2 interventions.txt | uniq -c | head -8
```

```text
      1 reseau
      1 stockage
      2 sauvegarde     ← the only two identical neighbouring lines
      1 messagerie
      1 stockage
      1 reseau
      1
      1 reseau
```

The occurrences of `reseau` are counted one by one because they do not follow
each other, whereas the two neighbouring `sauvegarde` merge. That is the proof
of the mechanism: `uniq` has no memory at all, it compares neighbours. So it is
enough to sort beforehand to make all the identical values neighbours:

```bash
cut -d: -f2 interventions.txt | sort | uniq -c
```

```text
      2
      3 messagerie
      7 reseau
      4 sauvegarde
      4 stockage
```

The count becomes exact, and the two empty lines appear in broad daylight with
their own counter. The varying indentation in front of the numbers is normal:
`uniq -c` aligns on the width of the largest count.

### The complete pipeline, the one you write every day

Add a second sort, numeric and descending, then `head` to keep only the top of
the ranking:

```bash
cut -d: -f2 interventions.txt | grep . | sort | uniq -c | sort -rn | head -3
```

```text
      7 reseau
      4 stockage
      4 sauvegarde
```

Each link has one role and one only: `cut` isolates the column, `grep .` throws
away the empty lines, `sort` makes the identical values neighbours, `uniq -c`
counts, `sort -rn` ranks from the most frequent to the rarest, `head -3` cuts.
Change the single field number (`-f3`) and the same line ranks the agents:
`4 elodie`, `4 bruno`, `3 Zoe`, `3 Adrien`, `2 Émile`, `2 adrien`.

Two useful variants of the last link: `tail` when it is the bottom of the
ranking that interests you, and `wc -l` when the question is "how many distinct
values?". Here, the variant `... | sort -u | wc -l` answers `6`.

### When `cut` is no longer enough: `tr`, `sed` and `awk`

`cut -d' '` cuts on **one** space. Faced with columns aligned by multiple
spaces, it returns empty fields:

```bash
printf '%-12s %6s %s\n' serveur-01 12 reseau serveur-2 4 stockage \
  > charges.txt
cut -d' ' -f2 charges.txt | cat -A   # cat -A shows the empty lines
```

```text
$
$
```

```bash
awk '{print $2}' charges.txt         # separator: runs of spaces
```

```text
12
4
```

`cut` found nothing and returned two empty lines; `awk` gets it right first
time, because its default separator is "one or more spaces". The other solution
consists in normalising first with `tr -s` (squeeze), which reduces the
consecutive repetitions to a single occurrence:

```bash
tr -s ' ' < charges.txt | cut -d' ' -f2
```

```text
12
4
```

`tr` also serves to rewrite a delimiter character by character, and `sed` does
the same thing by substitution. The `g` flag of `sed` is not decorative:

```bash
sed 's/:/|/' interventions.txt | head -2      # without g
```

```text
2026-03-02|reseau:Adrien:35
2026-03-02|stockage:elodie:120
```

```bash
sed 's/:/|/g' interventions.txt | head -2     # with g
tr ':' '|' < interventions.txt | head -2      # same result, another tool
```

```text
2026-03-02|reseau|Adrien|35
2026-03-02|stockage|elodie|120
```

Finally, as soon as you have to **compute** on a field, `cut` stops and `awk`
takes over. `-F` sets the separator, a variable accumulates, the `END` block runs
after the last line:

```bash
awk -F: '{total += $4} END {print total}' interventions.txt
awk -F: 'NF {m[$2] += $4} END {for (s in m) print m[s], s}' \
    interventions.txt | sort -rn
```

```text
606
302 reseau
201 stockage
74 sauvegarde
29 messagerie
```

The `NF` safeguard ignores the empty lines (zero fields). And since `awk` does
not guarantee the order of the keys of an array, you go through `sort` again on
output.

### Troubleshooting

| Problem | Likely cause | Solution |
|---|---|---|
| `uniq -c` only counts 1s | Unsorted input, the identical ones do not touch | Insert `sort` before `uniq` |
| `10` ranked before `9` | Alphabetical sort by default | Add `-n` (or `-V` for versions) |
| `cut` returns empty fields | Delimiter absent, or multiple spaces | Check with `cat -A`, normalise with `tr -s ' '`, or move to `awk` |
| An empty line in the result | The source file contains some | Filter with `grep .` in the pipe |
| The sort differs from one machine to another | Different `LC_COLLATE` | Prefix with `LC_ALL=C sort` on both sides |
| `sort -u` leaves near-duplicates | Different case | Add `-f`: `sort -uf` |
| `sed` only replaces once per line | `g` flag forgotten | `s/pattern/replacement/g` |
| `tr` displays nothing | `tr` does not read a file passed as an argument | Feed it with a `< file` redirection or through a pipe |
| `awk`: total at `0` | Wrong separator, therefore wrong field | Check with `awk -F: '{print $4}'` |
