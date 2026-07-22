# Lab — grep and regular expressions

## Reminder

[**Filter text with grep on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/)

`grep PATTERN file` keeps the lines that match. Regular expressions make the
pattern precise: `^` and `$` anchor to the start/end of a line, `[0-9]` is a
character class, `-E` enables extended regex, `-v` inverts the filter, `-o`
prints only the matched text, and `-c` counts lines instead of printing them.

## The course

The examples below work on an inventory of machines (`parc.csv`) and a workshop
log (`notes.txt`), which you build yourself: the challenge will hand you a
completely different file, other fields and other questions. The point is to
learn the method, not to copy a line.

Every output reproduced here was obtained on an AlmaLinux 10.2 VM with
**GNU grep 3.11** and the `en_US.UTF-8` locale. A whole section is devoted to
the results that change with the locale.

### The demonstration setup

Build the setup rather than digging through `/var/log`: that way you control the
edge cases, and your outputs are reproducible.

```bash
mkdir -p ~/atelier-grep/config && cd ~/atelier-grep

{
  printf '# parc de demonstration - atelier grep\n'
  printf 'nom;service;port;version;etat\n'
  printf 'web-01;frontal;8080;1.2.3;actif\n'
  printf 'web-02;frontal;8080;1.10.0;ARRETE\n'
  printf 'db-01;base;5432;15.4;actif \n'
  printf 'cache-01;cache;6379;7.2;Actif\n'
  printf '\tproxy-01;frontal;3128;3.5;actif\n'
  printf '\n'
  printf 'bastion-01;acces;22;9.6;maintenance\n'
  printf 'export-nuit;sauvegarde;2049;4.0;actif\n'
  printf 'supervision;metrologie;9090;2.51;arrêté\n'
} > parc.csv

{
  printf 'Journal de l atelier\n'
  printf '\n'
  printf '2026-07-22 [INFO] [web-01] redemarrage planifie puis controle du redemarrage\n'
  printf '2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee\n'
  printf '2026-07-22 [INFO] [proxy-01] fichier proxyXconf ignore par erreur\n'
  printf '2026-07-22 [ERREUR] [cache-01] le modele proxy-conf.tpl reste a jour\n'
  printf 'Le café de la salle est prêt, CAFÉ en majuscules aussi.\n'
  printf '\tcette ligne commence par une tabulation\n'
} > notes.txt

printf 'timeout=30\nupstream=web-01\n' > config/proxy.conf
printf 'timeout=15\nworkers=4\n'       > config/web.conf
ln -s config lien-config
```

This file deliberately contains six traps: a comment line, a header line, an
**empty** line, a line indented with a **tab**, a line with an invisible
**trailing space**, and states written in three different cases plus an accent.
`cat -A` makes them visible (`$` marks the end of a line, `^I` a tab):

```bash
cat -A parc.csv
```

```text
# parc de demonstration - atelier grep$
nom;service;port;version;etat$
web-01;frontal;8080;1.2.3;actif$
web-02;frontal;8080;1.10.0;ARRETE$
db-01;base;5432;15.4;actif $
cache-01;cache;6379;7.2;Actif$
^Iproxy-01;frontal;3128;3.5;actif$
$
bastion-01;acces;22;9.6;maintenance$
export-nuit;sauvegarde;2049;4.0;actif$
supervision;metrologie;9090;2.51;arrM-CM-*tM-CM-)$
```

Remember line 5: `actif $`, with a space after the word. It is about to be
useful.

### Searching for a literal pattern

The simplest case. `-n` prefixes each result with its line number, `-i` ignores
case.

```bash
grep -n actif parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
5:db-01;base;5432;15.4;actif 
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

Four lines only, whereas the file has five that describe a running service.
`cache-01` is written `Actif`: `grep` is case sensitive.

```bash
grep -in actif parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

The reflex: when a result looks too short, replay it with `-i` before concluding
that the data is missing.

### Anchoring with `^` and `$`

An anchor consumes no character, it fixes **where** the match must happen: `^`
at the start of the line, `$` at the end.

```bash
grep -n "^web" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
```

The anchor rules out everything that contains `web` elsewhere on the line.
Without it, the same search widened to the three files brings back lines that
are not inventory entries:

```bash
grep -n web parc.csv notes.txt config/proxy.conf
```

```text
parc.csv:3:web-01;frontal;8080;1.2.3;actif
parc.csv:4:web-02;frontal;8080;1.10.0;ARRETE
notes.txt:3:2026-07-22 [INFO] [web-01] redemarrage planifie puis controle du redemarrage
config/proxy.conf:2:upstream=web-01
```

When `grep` receives several files, it prefixes each line with the file name.
`-h` removes that prefix, `-H` forces it on a single file.

Two anchors stuck together, `^$`, describe an empty line:

```bash
grep -n "^$" parc.csv
```

```text
8:
```

Now the trap. Let us look for the machines whose state, **at the end of the
line**, is `actif`:

```bash
grep -n "actif$" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

Line 5 has vanished. The bare pattern `grep actif` found it, the `$` anchor
loses it: that line ends with a space, so `actif` is not the last character.
This kind of bug is invisible on screen, hence the first diagnostic move:

```bash
grep -n actif parc.csv | cat -A
```

```text
3:web-01;frontal;8080;1.2.3;actif$
5:db-01;base;5432;15.4;actif $
7:^Iproxy-01;frontal;3128;3.5;actif$
10:export-nuit;sauvegarde;2049;4.0;actif$
```

The fix is to tolerate trailing blanks:

```bash
grep -nE "actif[[:blank:]]*$" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
5:db-01;base;5432;15.4;actif 
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

The same mishap exists at the start of a line. `^proxy` finds nothing, because
line 7 starts with a tab:

```bash
grep -n "^proxy" parc.csv ; echo "code=$?"
```

```text
code=1
```

```bash
grep -nE "^[[:blank:]]*proxy" parc.csv
```

```text
7:	proxy-01;frontal;3128;3.5;actif
```

`[[:blank:]]` covers the space and the tab, which `" "` alone does not.

### The dot, the classes, and escaping

`.` matches **any character**. That is handy, and it is the most frequent trap:
it also catches what you did not want. Let us look for the log lines that talk
about the `proxy.conf` file:

```bash
grep -n "proxy.conf" notes.txt
```

```text
4:2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee
5:2026-07-22 [INFO] [proxy-01] fichier proxyXconf ignore par erreur
6:2026-07-22 [ERREUR] [cache-01] le modele proxy-conf.tpl reste a jour
```

Three lines, two of which do not talk about the right file: the `.` accepted the
`X` and the `-`. For a **literal** dot, you must escape it:

```bash
grep -n "proxy\.conf" notes.txt
```

```text
4:2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee
```

A class `[...]` matches **a single** character among those listed. POSIX classes
are portable from one distribution to another:

| Class | Equivalent | Use |
|---|---|---|
| `[[:digit:]]` | `[0-9]` | digits |
| `[[:alpha:]]` | `[a-zA-Z]` | letters |
| `[[:alnum:]]` | `[a-zA-Z0-9]` | letters and digits |
| `[[:blank:]]` | space and tab | horizontal blanks |
| `[[:space:]]` | `[ \t\n]` | all blanks |
| `[[:upper:]]` / `[[:lower:]]` | `[A-Z]` / `[a-z]` | case |

A `^` in **first position inside the brackets** means "none of": `[^;]` matches
any character that is not a semicolon. Do not confuse it with the `^` anchor at
the start of a pattern.

```bash
grep -nE "^[[:alpha:]]+;" parc.csv
```

```text
2:nom;service;port;version;etat
11:supervision;metrologie;9090;2.51;arrêté
```

Only two lines have a first field made only of letters: all the others contain a
digit or a dash.

Finally, an accent is a character like any other: it cannot be guessed.

```bash
grep -n "arrete" parc.csv ; echo "code=$?"
```

```text
code=1
```

```bash
grep -n "arr.t." parc.csv
```

```text
11:supervision;metrologie;9090;2.51;arrêté
```

The unaccented pattern finds nothing, even though line 11 exists. Note in
passing that `.` did go through `ê` and `é`: in a UTF-8 locale, `.` counts
**characters**, not bytes. We come back to this further down.

### BRE against ERE: what `-E` changes

`grep` knows two dialects of regular expressions:

| Dialect | Enabled by | Quantifiers, alternation and groups |
|---|---|---|
| **BRE** (basic) | `grep` by default | must be **escaped**: `\+` `\?` `\{n,m\}`, the vertical bar and `\(\)` |
| **ERE** (extended) | `grep -E` | written **as is**: `+` `?` `{n,m}`, the vertical bar and `()` |

In the tables above and below, the vertical bar is spelled out: it is the `|`
character, the "or" alternation.

The demonstration takes two lines. Let us look for the machines that are stopped
**or** under maintenance:

```bash
grep -n "ARRETE|maintenance" parc.csv ; echo "code=$?"
```

```text
code=1
```

No result, and no error: in BRE, `|` is not alternation, `grep` looked for the
literal string `ARRETE|maintenance`. This is the worst case, a silent false
negative. The two correct spellings:

```bash
grep -n "ARRETE\|maintenance" parc.csv    # BRE, with escaping
grep -nE "ARRETE|maintenance" parc.csv    # ERE, more readable
```

```text
4:web-02;frontal;8080;1.10.0;ARRETE
9:bastion-01;acces;22;9.6;maintenance
```

Same story with `+`:

```bash
grep -n "web-0[0-9]+" parc.csv ; echo "code=$?"
```

```text
code=1
```

In BRE, `+` is an ordinary character: the pattern literally asked for a `+`
after the digit. The two forms that work, and that return exactly the same list,
the names made of letters then a dash then digits:

```bash
grep -n  "^[a-z]\+-[0-9]\+" parc.csv   # BRE
grep -nE "^[a-z]+-[0-9]+"   parc.csv   # ERE
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
9:bastion-01;acces;22;9.6;maintenance
```

The bounded quantifier follows the same rule, `{n,m}` in ERE and `\{n,m\}` in
BRE. The two commands below give exactly the same result, the four-digit ports:

```bash
grep -nE ";[0-9]{4};" parc.csv
grep -n  ";[0-9]\{4\};" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
11:supervision;metrologie;9090;2.51;arrêté
```

`bastion-01` is missing: its port is `22`, two digits.

The `?` (zero or one) is checked on three made-up words:

```bash
printf 'arret\narrete\narretee\n' | grep -E "arrete?$"
```

```text
arret
arrete
```

Finally the parentheses, which group:

```bash
grep -nE "^(web|db)-" parc.csv     # ERE
grep -n  "^\(web\|db\)-" parc.csv  # BRE, same result
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
```

The rule of conduct: as soon as your pattern contains `+`, `?`, `{n,m}`, `|` or
`()`, switch to `-E`. You will avoid half of the false negatives.

### `-w`: the whole word

`grep` looks for a **substring**, not a word. Let us look for the `port` field:

```bash
grep -n port parc.csv
```

```text
2:nom;service;port;version;etat
10:export-nuit;sauvegarde;2049;4.0;actif
```

Line 10 is a false positive: `export` contains `port`. `-w` requires a word
boundary on either side of the pattern:

```bash
grep -nw port parc.csv
```

```text
2:nom;service;port;version;etat
```

The semicolon acts as a boundary, the `x` of `export` does not. `-w` is
equivalent to the BRE pattern `\<port\>` and serves the same purpose as `\b` in
other languages.

### `-o`: print only what matches

By default, `grep` prints the whole line. `-o` prints only the matching portion,
one per line. Let us extract the severity levels from the log:

```bash
grep -oE "\[[^]]+\]" notes.txt
```

```text
[INFO]
[web-01]
[WARN]
[db-01]
[INFO]
[proxy-01]
[ERREUR]
[cache-01]
```

Why `[^]]+` rather than `.*`? Because quantifiers are **greedy**: they take as
much as possible.

```bash
grep -oE "\[.*\]" notes.txt
```

```text
[INFO] [web-01]
[WARN] [db-01]
[INFO] [proxy-01]
[ERREUR] [cache-01]
```

`.*` swallowed the closing bracket, the space and the following opening bracket:
a single match per line instead of two. The POSIX workaround is always the same,
replace `.` with a **negated class** that excludes the delimiter: `[^]]` here,
`[^;]` for a CSV field, `[^>]` for a tag.

`-o` is mostly used to extract a field in order to count it afterwards. The last
field of each line, that is everything after the last `;`:

```bash
grep -v "^#" parc.csv | grep -oE "[^;]+$" | sort | uniq -c | sort -rn
```

```text
      3 actif
      1 maintenance
      1 etat
      1 arrêté
      1 ARRETE
      1 Actif
      1 actif 
```

Seven categories for four real states: `Actif` and `actif ` are counted
separately, and the `etat` header slipped in. An extraction is never a count:
you must first discard the service lines, then normalise case and blanks. That
is the real work.

### `-c` counts lines, never occurrences

The log contains the word `redemarrage` twice, on a single line.

```bash
grep -c redemarrage notes.txt
```

```text
1
```

```bash
grep -o redemarrage notes.txt | wc -l
```

```text
2
```

`-c` answers "one line contains the pattern", not "the pattern appears once". To
count **occurrences**, you must go through `-o` then `wc -l`. The confusion is
classic and silently falsifies reports.

On several files, `-c` gives one count per file, prefixed with the name:

```bash
grep -c timeout config/*.conf
```

```text
config/proxy.conf:1
config/web.conf:1
```

### `-v`: keep what does not match

`-v` inverts the selection. Combined with an anchor, it is the configuration
file cleaner:

```bash
grep -vnE "^[[:blank:]]*(#|$)" parc.csv
```

```text
2:nom;service;port;version;etat
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
7:	proxy-01;frontal;3128;3.5;actif
9:bastion-01;acces;22;9.6;maintenance
10:export-nuit;sauvegarde;2049;4.0;actif
11:supervision;metrologie;9090;2.51;arrêté
```

The pattern reads: start of line, optional blanks, then a `#` **or** the end of
the line. Lines 1 and 8, the comment and the empty line, are discarded. Note
that `-v` applies to the whole line: there is no "everything but this word"
inside a line.

### Searching a tree: `-r`, `-R`, `-l`

`-r` descends recursively into subdirectories:

```bash
grep -rn timeout .
```

```text
./config/proxy.conf:1:timeout=30
./config/web.conf:1:timeout=15
```

The `lien-config` symbolic link does point to that same `config` directory, and
its files do not show up. This is not an oversight: **`-r` does not follow the
symbolic links met during the walk**. `-R` follows all of them:

```bash
grep -Rn timeout .
```

```text
./config/proxy.conf:1:timeout=30
./config/web.conf:1:timeout=15
./lien-config/proxy.conf:1:timeout=30
./lien-config/web.conf:1:timeout=15
```

Each file is found twice, once per path. A nuance worth remembering: `-r` still
follows a link **named explicitly** on the command line.

```bash
grep -rn timeout lien-config
```

```text
lien-config/proxy.conf:1:timeout=30
lien-config/web.conf:1:timeout=15
```

On a link that goes back up the tree, `-R` detects the loop and says so, but
only after having walked the files one more time:

```bash
mkdir -p boucle && ln -s .. boucle/remonte
grep -Rn timeout boucle
```

```text
boucle/remonte/config/proxy.conf:1:timeout=30
boucle/remonte/config/web.conf:1:timeout=15
boucle/remonte/lien-config/proxy.conf:1:timeout=30
boucle/remonte/lien-config/web.conf:1:timeout=15
grep: boucle/remonte/boucle: warning: recursive directory loop
```

Nothing hangs, but the results are duplicated and a warning slips into the error
output. Prefer `-r`, and use `-R` only if you know why.

Two options that go with recursion. `-l` returns only the file names, which is
useful to chain with `xargs`:

```bash
grep -rl timeout .
```

```text
./config/proxy.conf
./config/web.conf
```

`--include` restricts the walk to a **file name** pattern, not to be confused
with the pattern being searched:

```bash
grep -rn --include="*.conf" timeout .
```

```text
./config/proxy.conf:1:timeout=30
./config/web.conf:1:timeout=15
```

### Return codes, and `grep -q` in a test

This is what makes `grep` usable in a script. Three values:

| Code | Meaning |
|---|---|
| `0` | at least one line matches |
| `1` | no line matches (this is **not** an error) |
| `2` | error: unreadable file, invalid regex |

```bash
grep -q actif parc.csv;    echo "trouve      -> $?"
grep -q inconnu parc.csv;  echo "pas trouve  -> $?"
grep -q actif absent.csv;  echo "erreur      -> $?"
```

```text
trouve      -> 0
pas trouve  -> 1
grep: absent.csv: No such file or directory
erreur      -> 2
```

`-q` (quiet) prints nothing on standard output: this is the form to use in a
test, where only the code matters. Beware, it does not silence **errors**, which
go to the error output: the `No such file or directory` message above was indeed
emitted despite `-q`. To silence that too, add `-s`, but the code stays `2`:

```bash
grep -qs actif absent.csv ; echo "code=$?"
```

```text
code=2
```

`-q` also stops **at the first match**, which can be proven on an infinite
stream: the command on the left returns immediately, the one on the right never
stops and gets killed by `timeout` after 3 seconds (code `124`).

```bash
timeout 5 bash -c 'yes correspondance | grep -q correspondance'      ; echo "code=$?"
timeout 3 bash -c 'yes correspondance | grep correspondance >/dev/null' ; echo "code=$?"
```

```text
code=0
code=124
```

The common usage pattern:

```bash
if grep -q "^bastion-01;" parc.csv; then
  echo "bastion-01 est inventorie"
else
  echo "absent"
fi

if grep -q "^switch-01;" parc.csv; then
  echo "switch-01 est inventorie"
else
  echo "switch-01 absent de l inventaire"
fi
```

```text
bastion-01 est inventorie
switch-01 absent de l inventaire
```

Telling `1` from `2` matters: a script that only tests "non-zero code" confuses
"the machine is not in the inventory" with "the inventory file cannot be found".
The second case deserves an alert, not an `else` branch.

### The locale changes the meaning of classes

On this VM, `locale` returns `LANG=en_US.UTF-8` and `LC_ALL` is empty. The
following results depend on it: prefixing a command with `LC_ALL=C` changes the
locale for that command only.

```bash
echo "café prêt" | grep -oE "[[:alpha:]]+"
```

```text
café
prêt
```

```bash
echo "café prêt" | LC_ALL=C grep -oE "[[:alpha:]]+"
```

```text
caf
pr
t
```

In the `C` locale, `é` and `ê` are not letters: every accented word is cut into
pieces. Same effect on case folding, where `-i` stops matching `CAFÉ` with
`café`:

```bash
grep -oi "CAFÉ" notes.txt
```

```text
café
CAFÉ
```

```bash
LC_ALL=C grep -oi "CAFÉ" notes.txt
```

```text
CAFÉ
```

And on the dot, which counts characters in UTF-8 and bytes in `C`:

```bash
echo "café" | grep -c "^c.f.$"
echo "café" | LC_ALL=C grep -c "^c.f.$"
```

```text
1
0
```

The pattern `^c.f.$` asks for four characters. In UTF-8, `é` is one of them and
the line matches; in the `C` locale, `é` counts as two (`0xC3 0xA9`), the line
has five and the pattern fails.

The gap is not only semantic, it is also spectacular in computing time. On a
138 MiB file built for the occasion, the same `grep` with a POSIX class takes
7.7 seconds in UTF-8 and 0.12 second in the `C` locale:

```bash
yes "ligne de test avec du texte accentué café prêt et des chiffres 12345" \
  | head -2000000 > /tmp/gros.txt
time grep -c "[[:alpha:]]\+345" /tmp/gros.txt
time LC_ALL=C grep -c "[[:alpha:]]\+345" /tmp/gros.txt
rm -f /tmp/gros.txt
```

Three measurements of each, on the lab VM: `7.73 / 7.73 / 7.70 s` against
`0.13 / 0.12 / 0.12 s`, a factor of sixty. In UTF-8, `grep` has to decode each
multi-byte character; in `C` it compares bytes.

Practical consequence: in a script, forcing `LC_ALL=C` speeds up `grep` and
makes sorting reproducible, but it breaks any pattern that relies on accented
letters. Choose knowingly, and write it down in the script.

### The pattern must be protected from the shell

The shell interprets `*`, `?`, `$`, `[` and the space **before** `grep` ever
sees them. In a directory that contains `proxy.conf` and `web.conf`:

```bash
printf 'inclure *.conf au demarrage\n' > config/liste.txt
cd config
grep *.conf liste.txt ; echo "code=$?"
```

```text
code=1
```

Nothing, even though the string `*.conf` is indeed in the file. The shell
replaced `*.conf` with the list of matching files: `grep` received
`grep proxy.conf web.conf liste.txt`, so it looked for the pattern `proxy.conf`
in the two other files. A quoted pattern, or `-F` for a strictly literal search,
put things right:

```bash
grep "\*\.conf" liste.txt
grep -F "*.conf" liste.txt
cd ..
```

```text
inclure *.conf au demarrage
inclure *.conf au demarrage
```

One line per command: both spellings find the same thing.

The same reflex applies to `$`:

```bash
printf 'prix: 10$\n' > /tmp/prix.txt
grep    "prix: 10$" /tmp/prix.txt ; echo "code=$?"
grep -F "prix: 10$" /tmp/prix.txt ; echo "code=$?"
```

```text
code=1
prix: 10$
code=0
```

Without `-F`, the `$` is read as the end-of-line anchor, and the pattern becomes
impossible to satisfy. Simple rule: **always put the pattern in single quotes**,
and pass `-F` when it contains no regular expression.

Last classic of the genre, `grep` finding itself:

```bash
ps -ef | grep chronyd
```

```text
chrony       707       1  0 13:30 ?        00:00:00 /usr/sbin/chronyd -n -F 2
ansible    15077   15075  0 14:01 ?        00:00:00 grep chronyd
```

(The process numbers and times differ on your machine, the second line does
not.) The `grep` process appears in the list `ps` has just produced. You discard
it with a second filter:

```bash
ps -ef | grep chronyd | grep -v grep
```

```text
chrony       707       1  0 13:30 ?        00:00:00 /usr/sbin/chronyd -n -F 2
```

### Seeing the context of a match

On a log, the matching line is often not enough: `-A N` prints N lines after,
`-B N` N lines before, `-C N` on both sides. Context lines are prefixed with `-`
instead of `:`, which lets you tell them apart:

```bash
grep -n -A1 "WARN" notes.txt
```

```text
4:2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee
5-2026-07-22 [INFO] [proxy-01] fichier proxyXconf ignore par erreur
```

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| No result although the data exists | different case: replay with `-i` |
| No result with a pattern containing `+`, `?`, `{}`, `()` or the vertical bar | ERE pattern run as BRE: add `-E` (or escape) |
| A `$` anchor loses lines | invisible trailing spaces: check with `cat -A`, tolerate with `[[:blank:]]*$` |
| A `^` anchor loses lines | indented line: accept `^[[:blank:]]*` |
| Too many results, pattern containing a dot | `.` accepts anything: write `\.` for a literal dot |
| Too many results, partial match | substring instead of word: add `-w` |
| `-o` returns only one match per line | greediness of `.*`: use a negated class `[^X]*` |
| The count is smaller than expected | `-c` counts lines: go through `grep -o` then `wc -l` |
| Absurd results, pattern containing `*` or `$` | pattern interpreted by the shell: put it in single quotes, or use `-F` |
| An accent is not found, or a word is cut | locale: compare with and without `LC_ALL=C` |
| The files behind a symbolic link are ignored | `-r` does not follow links met during the walk: use `-R` knowingly |
| `grep: ...: No such file or directory` | return code `2`, this is not "no match" |
| `grep: Invalid regular expression` | unclosed bracket or parenthesis, or ERE syntax in BRE |
| `Binary file ... matches` | file seen as binary: force with `-a` |

### Tearing down the setup

```bash
rm -rf ~/atelier-grep /tmp/prix.txt
```
