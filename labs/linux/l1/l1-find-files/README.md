# Lab — locate files with find

## Reminder

[**find on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/)

`find <path> <predicates>` walks a tree from a starting point and keeps only the
objects that satisfy the given criteria: `-name` (pattern on the name), `-type`
(nature of the object), `-size` (size), `-perm` (mode), `-mtime` (modification
date), `-user` (owner). Criteria written one after another are combined with a
logical **AND**. The descent is recursive by default.

## The course

The examples below work on `/srv/inventaire`, a demonstration tree that you
build yourself, with the user `camille`: the challenge will ask you for other
paths, other patterns and other values. The goal is to learn the method and
above all to recognise the traps of `find`, not to copy a line.

All the outputs reproduced here come from an AlmaLinux 10 with
`find (GNU findutils) 4.10.0`.

### The demonstration setup

Digging through the real system is the best way to understand nothing: results
change from one machine to the next and permission errors clutter the output. So
you build a tree whose sizes, modes, owners and dates you know exactly.

```bash
sudo useradd -m camille
sudo mkdir -p /srv/inventaire/{rapports,sauvegardes/ancien,scripts,partage}

# contents of chosen sizes
sudo sh -c 'head -c 2500  /dev/zero | tr "\0" x > /srv/inventaire/rapports/ventes-2024.csv'
sudo sh -c 'head -c 1500  /dev/zero | tr "\0" v > /srv/inventaire/rapports/export-hebdo.csv'
sudo sh -c 'head -c 120   /dev/zero | tr "\0" y > /srv/inventaire/rapports/ventes-2025.csv'
sudo touch /srv/inventaire/rapports/brouillon.tmp
sudo sh -c 'head -c 30720 /dev/zero | tr "\0" z > /srv/inventaire/sauvegardes/base.sql.bak'
sudo sh -c 'head -c 5120  /dev/zero | tr "\0" w > /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak'
sudo sh -c 'printf "#!/bin/bash\necho collecte\n" > /srv/inventaire/scripts/collecte.sh'
sudo sh -c 'printf "#!/bin/bash\necho purge\n"    > /srv/inventaire/scripts/purge.sh'
sudo sh -c 'printf "ordre du jour\n"     > "/srv/inventaire/notes de reunion.txt"'
sudo sh -c 'printf "boite aux lettres\n" > /srv/inventaire/partage/depot.txt'
sudo ln -sfn /srv/inventaire/rapports /srv/inventaire/lien-rapports
```

Then the owners and the modes:

```bash
sudo chown -R root:root /srv/inventaire
sudo chown camille:camille /srv/inventaire/sauvegardes/base.sql.bak \
                           /srv/inventaire/scripts/purge.sh

sudo chmod 0755 /srv/inventaire /srv/inventaire/rapports /srv/inventaire/sauvegardes \
                /srv/inventaire/sauvegardes/ancien /srv/inventaire/scripts /srv/inventaire/partage
sudo chmod 0644 /srv/inventaire/rapports/ventes-2024.csv \
                /srv/inventaire/rapports/export-hebdo.csv \
                /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
sudo chmod 0640 /srv/inventaire/rapports/ventes-2025.csv
sudo chmod 0660 /srv/inventaire/rapports/brouillon.tmp
sudo chmod 0400 /srv/inventaire/sauvegardes/base.sql.bak
sudo chmod 0755 /srv/inventaire/scripts/collecte.sh
sudo chmod 0700 /srv/inventaire/scripts/purge.sh
sudo chmod 0604 "/srv/inventaire/notes de reunion.txt"
sudo chmod 0666 /srv/inventaire/partage/depot.txt
```

Finally the modification dates, computed relative to the present moment so that
the `-mtime` examples give the same result whatever the day you run them.
`touch -d` accepts an arbitrary date, there is nothing to wait for:

```bash
sudo touch -d "$(date -d '2 hours ago'  '+%F %T')" /srv/inventaire/rapports/ventes-2025.csv
sudo touch -d "$(date -d '1 day ago'    '+%F %T')" /srv/inventaire/rapports/brouillon.tmp
sudo touch -d "$(date -d '2 days ago'   '+%F %T')" /srv/inventaire/scripts/purge.sh
sudo touch -d "$(date -d '3 days ago'   '+%F %T')" "/srv/inventaire/notes de reunion.txt"
sudo touch -d "$(date -d '4 days ago'   '+%F %T')" /srv/inventaire/rapports/ventes-2024.csv
sudo touch -d "$(date -d '5 days ago'   '+%F %T')" /srv/inventaire/partage/depot.txt
sudo touch -d "$(date -d '7 days ago 12 hours ago' '+%F %T')" /srv/inventaire/rapports/export-hebdo.csv
sudo touch -d "$(date -d '12 days ago'  '+%F %T')" /srv/inventaire/scripts/collecte.sh
sudo touch -d "$(date -d '51 days ago'  '+%F %T')" /srv/inventaire/sauvegardes/base.sql.bak
sudo touch -d "$(date -d '434 days ago' '+%F %T')" /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
```

Here is the resulting inventory, size in bytes, octal mode, owner:

```bash
find /srv/inventaire -type f -printf '%8s  %m  %-8u  %p\n' | sort -k4
```

```text
      14  604  root      /srv/inventaire/notes de reunion.txt
      18  666  root      /srv/inventaire/partage/depot.txt
       0  660  root      /srv/inventaire/rapports/brouillon.tmp
    1500  644  root      /srv/inventaire/rapports/export-hebdo.csv
    2500  644  root      /srv/inventaire/rapports/ventes-2024.csv
     120  640  root      /srv/inventaire/rapports/ventes-2025.csv
    5120  644  root      /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
   30720  400  camille   /srv/inventaire/sauvegardes/base.sql.bak
      26  755  root      /srv/inventaire/scripts/collecte.sh
      23  700  camille   /srv/inventaire/scripts/purge.sh
```

Keep this table in front of you: every result that follows can be checked
against it.

### A starting point, then predicates

Without any criterion, `find` prints everything it meets, including the starting
point:

```bash
find /srv/inventaire
```

```text
/srv/inventaire
/srv/inventaire/rapports
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/sauvegardes
/srv/inventaire/sauvegardes/ancien
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/scripts
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
/srv/inventaire/lien-rapports
```

Two lessons in that single output. First, recursion is automatic,
`base-2023.sql.bak` is two levels down. Second, the order is **not**
alphabetical: it is the order in which the filesystem is walked. If you need a
sorted list, pipe explicitly through `| sort`.

### Searching by name: `-name`, `-iname`, `-path`

```bash
find /srv/inventaire -name '*.csv'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
```

The quotes around the pattern are not decoration. Without them, it is the shell
that expands the glob **before** running `find`, and the command fails as soon
as more than one matching file exists in the current directory:

```bash
cd /srv/inventaire/rapports
find . -name *.csv
```

```text
find: paths must precede expression: `ventes-2024.csv'
find: possible unquoted pattern after predicate `-name'?
```

The message is explicit if you know how to read it: `find` received three file
names where it expected a single pattern. Get into the habit of quoting, always.

`-iname` does the same thing without distinguishing upper and lower case:

```bash
find /srv/inventaire -iname '*.CSV'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
```

A classic trap: **`-name` only sees the last component of the path**, never the
directories that lead to the file. A pattern containing a `/` therefore matches
nothing:

```bash
find /srv/inventaire -name 'rapports/*'
```

```text
```

Nothing, and yet the return code is `0`: `find` did not fail, it simply found
nothing. To filter on the full path you need `-path`, and its pattern must cover
the whole path:

```bash
find /srv/inventaire -path '*/rapports/*.csv'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
```

### Filtering by type: `-type`

| Value | Meaning |
|---|---|
| `f` | regular file |
| `d` | directory |
| `l` | symbolic link |

```bash
find /srv/inventaire -type d
```

```text
/srv/inventaire
/srv/inventaire/rapports
/srv/inventaire/sauvegardes
/srv/inventaire/sauvegardes/ancien
/srv/inventaire/scripts
/srv/inventaire/partage
```

```bash
find /srv/inventaire -type l
```

```text
/srv/inventaire/lien-rapports
```

The symbolic link does **not** show up in `-type f`: a link is not a regular
file, even if it points to a directory full of files. By default `find` does not
follow links. The `-L` option, placed **before** the starting path, forces it
to, and the same tree is then visited twice:

```bash
find -L /srv/inventaire -name '*.csv'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/lien-rapports/ventes-2024.csv
/srv/inventaire/lien-rapports/export-hebdo.csv
/srv/inventaire/lien-rapports/ventes-2025.csv
```

Three files, six lines. On a real system, `-L` on a link that points back to a
parent makes `find` go round in circles, and it ends up complaining about a
loop. Only turn it on when you know why.

### Filtering by size: `-size`, and its rounding

The suffix gives the unit:

| Suffix | Unit |
|---|---|
| `c` | bytes |
| `k` | KiB (1024 bytes) |
| `M` | MiB |
| `G` | GiB |

The prefix gives the direction of the comparison: `+` for "strictly more",
`-` for "strictly less", nothing at all for "exactly".

```bash
find /srv/inventaire -type f -size +2000c -printf '%s %p\n'
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
5120 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
30720 /srv/inventaire/sauvegardes/base.sql.bak
```

The bound is **strict**: a file of 2500 bytes does not satisfy `-size +2500c`.

```bash
find /srv/inventaire -type f -size +2500c -printf '%s %p\n'
```

```text
5120 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
30720 /srv/inventaire/sauvegardes/base.sql.bak
```

`ventes-2024.csv` has disappeared. Without a prefix, you ask for exact equality:

```bash
find /srv/inventaire -type f -size 2500c -printf '%s %p\n'
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
```

Now comes the trap that surprises everybody. **With any unit other than `c`,
`find` rounds the size up to the next block before comparing.** A file of 1 byte
therefore counts as one block of 1 KiB, and as one block of 1 MiB. Consequence:

```bash
find /srv/inventaire -type f -size -1M -printf '%s %p\n'
```

```text
0 /srv/inventaire/rapports/brouillon.tmp
```

A single result, whereas nine files out of ten are smaller than 1 MiB.
"Strictly less than 1 block of 1 MiB" can only mean "zero blocks", that is, an
empty file. If you are looking for files under one MiB, write `-size -1048576c`,
or accept the bound rounded to the block.

The same rounding explains this:

```bash
find /srv/inventaire -type f -size 3k -printf '%s %p\n'
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
```

2500 bytes is 2.44 KiB, rounded up to 3 blocks. The file therefore matches
`-size 3k` and not `-size 2k`. Remember the rule: **`c` is the only unit that
compares the real size**, all the others compare a number of blocks rounded up.

For empty files, `-empty` is more readable than `-size 0c` and gives the same
result:

```bash
find /srv/inventaire -type f -empty -printf '%s %p\n'
```

```text
0 /srv/inventaire/rapports/brouillon.tmp
```

### Filtering by date: `-mtime` and its 24-hour slices

This is the most often misunderstood predicate. `-mtime n` does not talk about
"calendar days" but about **24-hour slices**, and the computation throws away
the fractional part: `find` divides the age of the file by 86400 seconds and
truncates.

- `-mtime -7`: truncated age **less** than 7, so modified less than 7 times
  24 hours ago;
- `-mtime +7`: truncated age **greater** than 7, so at least 8 times 24 hours;
- `-mtime 7`: truncated age **equal** to 7, the slice between 7 and 8 times
  24 hours.

Our files, with their ages:

```text
2025-05-14  base-2023.sql.bak   434 days
2026-06-01  base.sql.bak         51 days
2026-07-10  collecte.sh          12 days
2026-07-15  export-hebdo.csv      7 days and 12 hours
2026-07-17  depot.txt             5 days
2026-07-18  ventes-2024.csv       4 days
2026-07-19  notes de reunion.txt  3 days
2026-07-20  purge.sh              2 days
2026-07-21  brouillon.tmp         1 day
2026-07-22  ventes-2025.csv       2 hours
```

```bash
find /srv/inventaire -type f -mtime -7
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
```

```bash
find /srv/inventaire -type f -mtime +7
```

```text
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/scripts/collecte.sh
```

Six files on one side, three on the other: one out of ten is missing.
`export-hebdo.csv`, seven and a half days old, is neither in `-mtime -7` nor in
`-mtime +7`. It lives in the gap between the two:

```bash
find /srv/inventaire -type f -mtime 7
```

```text
/srv/inventaire/rapports/export-hebdo.csv
```

> `-mtime -7` and `-mtime +7` are therefore **not** complementary. Writing
> `-mtime +7` while thinking "everything that has not been modified this week"
> systematically lets a whole day of files slip through. If you really want the
> complement of `-mtime -7`, write `-not -mtime -7`.

When day granularity is not enough, `-mmin` counts in minutes:

```bash
find /srv/inventaire -type f -mmin -180
```

```text
/srv/inventaire/rapports/ventes-2025.csv
```

And `-newer` compares against a reference file, which avoids any computation:

```bash
find /srv/inventaire -type f -newer /srv/inventaire/rapports/ventes-2024.csv
```

```text
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/scripts/purge.sh
/srv/inventaire/notes de reunion.txt
```

The reference file itself is excluded: the comparison is strict.

### Filtering by owner: `-user`, `-group`

```bash
find /srv/inventaire -user camille -printf '%u:%g  %p\n'
```

```text
camille:camille  /srv/inventaire/sauvegardes/base.sql.bak
camille:camille  /srv/inventaire/scripts/purge.sh
```

`-group` works the same way on the owning group. Both accept a name as well as a
numeric UID or GID, which helps when the account has just been deleted. On a
test directory with an account `zoe` of UID 1002:

```bash
find /srv/verif -user 1002 -printf '%u %p\n'
```

```text
zoe /srv/verif/a.txt
```

Delete the account, and the file becomes orphaned: no name matches its UID any
more. `-nouser` and `-nogroup` are there to find them again, and it is a search
worth running after any account cleanup.

```bash
sudo userdel -r zoe
find /srv/verif -nouser -printf '%U:%G %p\n'
```

```text
1002:1002 /srv/verif/a.txt
```

### Filtering by permissions: the three forms of `-perm`

This is where the difference between knowing the command and knowing how to use
it plays out. `-perm` has three syntaxes that do not mean the same thing at all.

| Form | Meaning |
|---|---|
| `-perm 644` | the mode is **exactly** 644 |
| `-perm -644` | **all** the bits of 644 are present, the others are free |
| `-perm /644` | **at least one** of the bits of 644 is present |

On our tree, strict equality:

```bash
find /srv/inventaire -type f -perm 644 -printf '%m %p\n'
```

```text
644 /srv/inventaire/rapports/ventes-2024.csv
644 /srv/inventaire/rapports/export-hebdo.csv
644 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
```

The dash changes everything:

```bash
find /srv/inventaire -type f -perm -644 -printf '%m %p\n'
```

```text
644 /srv/inventaire/rapports/ventes-2024.csv
644 /srv/inventaire/rapports/export-hebdo.csv
644 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
755 /srv/inventaire/scripts/collecte.sh
666 /srv/inventaire/partage/depot.txt
```

`755` and `666` show up, because both do contain `rw` for the owner, `r` for the
group and `r` for the others, plus other bits on top. `604`, on the other hand,
stays out: it lacks the `r` for the group.

The slash is the "or":

```bash
find /srv/inventaire -type f -perm /044 -printf '%m %p\n'
```

```text
644 /srv/inventaire/rapports/ventes-2024.csv
644 /srv/inventaire/rapports/export-hebdo.csv
640 /srv/inventaire/rapports/ventes-2025.csv
660 /srv/inventaire/rapports/brouillon.tmp
644 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
755 /srv/inventaire/scripts/collecte.sh
666 /srv/inventaire/partage/depot.txt
604 /srv/inventaire/notes de reunion.txt
```

`/044` asks for "readable by the group **or** by the others": `640` gets in
through the group, `604` through the others. Only `400` and `700`, unreadable
for anyone who is not the owner, stay out. The same value as an exact mode
obviously returns nothing, since no file has precisely the mode `044`:

```bash
find /srv/inventaire -type f -perm 044 -printf '%m %p\n'
```

```text
```

> An exact mode is very rarely what you want for an audit: all nine bits have to
> match. To look for a risk, use `-perm -` or `-perm /`. To check a precise
> requirement, use the exact mode.

The two audit uses that come up in the exam as well as in production. Files
writable by everybody:

```bash
find /srv/inventaire -type f -perm -002 -printf '%m %p\n'
```

```text
666 /srv/inventaire/partage/depot.txt
```

And the SUID binaries, worth knowing because they are the ones that run with the
rights of their owner. Here on the real system, read only:

```bash
find /usr/bin -type f -perm -4000
```

```text
/usr/bin/umount
/usr/bin/mount
/usr/bin/chfn
/usr/bin/chage
/usr/bin/gpasswd
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/crontab
/usr/bin/su
/usr/bin/pkexec
/usr/bin/sudo
```

`-perm` also accepts the symbolic notation of `chmod`, often more readable:
`-perm -u=x` finds what is executable by its owner, `-perm -g=w` what is
writable by the group.

```bash
find /srv/inventaire -type f -perm -g=w -printf '%m %p\n'
```

```text
660 /srv/inventaire/rapports/brouillon.tmp
666 /srv/inventaire/partage/depot.txt
```

### Combining criteria

Two predicates in a row are joined by an implicit AND:

```bash
find /srv/inventaire -type f -name '*.bak' -size +10k -printf '%s %p\n'
```

```text
30720 /srv/inventaire/sauvegardes/base.sql.bak
```

The OR is written `-o`, and it requires parentheses, themselves protected from
the shell by a backslash. Without them, precedence works against you: AND has
priority, so `-type f -name '*.csv' -o -name '*.sh'` reads as "(regular file AND
name ending in `.csv`) OR name ending in `.sh`", and the `-type f` filter no
longer applies to the second term. With a directory named `archives.sh` in the
tree:

```bash
find /srv/inventaire -type f -name '*.csv' -o -name '*.sh'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/sauvegardes/archives.sh
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
```

The `archives.sh` directory has invited itself in. With the parentheses, it
disappears:

```bash
find /srv/inventaire -type f \( -name '*.csv' -o -name '*.sh' \)
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
```

Negation is written `-not` or `!`:

```bash
find /srv/inventaire -type f -not -name '*.csv'
```

```text
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
```

### Limiting the descent and silencing errors

`-maxdepth` bounds the depth, `-mindepth` sets a floor. Depth 1 is the direct
entries of the starting point:

```bash
find /srv/inventaire -maxdepth 1 -type f
```

```text
/srv/inventaire/notes de reunion.txt
```

These two options are **global**: their place on the line does not change their
effect, but `find` calls you to order if you write them after a test. From an
interactive terminal:

```bash
find /srv/inventaire -type f -maxdepth 1
```

```text
find: warning: you have specified the global option -maxdepth after the argument -type, but global options are not positional, i.e., -maxdepth affects tests specified before it as well as those specified after it.  Please specify global options before other arguments.
/srv/inventaire/notes de reunion.txt
```

The result is correct, only the warning differs. Note: this warning only appears
if standard input is a terminal. In a script it stays silent, which does not
help to spot the mistake. Write global options first, on principle.

To cut off a whole branch, `-prune` is the right tool. Its canonical form is
surprising, but it reads as: "if the path is that one, prune it, **otherwise**
print what satisfies the rest".

```bash
find /srv/inventaire -path /srv/inventaire/sauvegardes -prune -o -type f -print
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
```

The final `-print` is mandatory here: as soon as an explicit action appears in
the expression, `find` no longer adds the implicit printing.

One last point, errors. Run by an unprivileged account on a system tree, `find`
pours `Permission denied` messages onto the error output, mixed in with the
result:

```bash
find /etc -name 'shadow'
```

```text
find: ‘/etc/pki/rsyslog’: Permission denied
find: ‘/etc/credstore’: Permission denied
find: ‘/etc/credstore.encrypted’: Permission denied
find: ‘/etc/audit/plugins.d’: Permission denied
/etc/shadow
```

These lines go to channel 2, so you can discard them without touching the
result:

```bash
find /etc -name 'shadow' 2>/dev/null
```

```text
/etc/shadow
```

### Acting on the results

`-exec` runs a command for each match, `{}` being replaced by the path found.
The terminator changes everything.

With `\;`, one execution per file:

```bash
sudo find /srv/inventaire -type f -name '*.csv' -exec wc -c {} \;
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
1500 /srv/inventaire/rapports/export-hebdo.csv
120 /srv/inventaire/rapports/ventes-2025.csv
```

With `+`, the paths are accumulated and passed in one go:

```bash
sudo find /srv/inventaire -type f -name '*.csv' -exec wc -c {} +
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
1500 /srv/inventaire/rapports/export-hebdo.csv
 120 /srv/inventaire/rapports/ventes-2025.csv
4120 total
```

The `total` line alone proves that `wc` was launched only once. You can make it
even more visible by printing the PID of the launched process:

```bash
find /srv/inventaire -type f -name '*.csv' -exec sh -c 'echo pid=$$' \;
```

```text
pid=12334
pid=12335
pid=12336
```

```bash
find /srv/inventaire -type f -name '*.csv' -exec sh -c 'echo pid=$$' sh {} +
```

```text
pid=12338
```

Three processes against one. On three files it is anecdotal, on fifty thousand
it is the difference between a few seconds and several minutes. Prefer `+`
whenever the command accepts several arguments; keep `\;` when it only takes
one, or when `{}` has to appear somewhere other than at the end of the line.

That leaves the problem of file names containing spaces. The naive loop that
everybody writes once in their life chops the name into pieces:

```bash
for f in $(find /srv/inventaire -maxdepth 1 -type f); do echo "[$f]"; done
```

```text
[/srv/inventaire/notes]
[de]
[reunion.txt]
```

One file, three "paths", none of which exists. The remedy is `-print0`, which
separates the results with a null byte instead of a newline, together with
`xargs -0` which knows how to read them back:

```bash
find /srv/inventaire -maxdepth 1 -type f -print0 | xargs -0 -I{} echo "[{}]"
```

```text
[/srv/inventaire/notes de reunion.txt]
```

`-exec` does not suffer from this flaw: it passes the paths directly, without
ever having a shell re-read them. That is one more reason to prefer it.

Two printing actions complete the picture. `-printf` composes a custom line
(`%s` the size, `%m` the octal mode, `%u` the owner, `%p` the path,
`%TY-%Tm-%Td` the modification date):

```bash
find /srv/inventaire -type f -printf '%8s  %TY-%Tm-%Td  %m  %-8u  %p\n' | sort -k5
```

```text
      14  2026-07-19  604  root      /srv/inventaire/notes de reunion.txt
      18  2026-07-17  666  root      /srv/inventaire/partage/depot.txt
       0  2026-07-21  660  root      /srv/inventaire/rapports/brouillon.tmp
    1500  2026-07-15  644  root      /srv/inventaire/rapports/export-hebdo.csv
    2500  2026-07-18  644  root      /srv/inventaire/rapports/ventes-2024.csv
     120  2026-07-22  640  root      /srv/inventaire/rapports/ventes-2025.csv
    5120  2025-05-14  644  root      /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
   30720  2026-06-01  400  camille   /srv/inventaire/sauvegardes/base.sql.bak
      26  2026-07-10  755  root      /srv/inventaire/scripts/collecte.sh
      23  2026-07-20  700  camille   /srv/inventaire/scripts/purge.sh
```

And `-ls` produces a detailed listing directly, without going through an
external command:

```bash
find /srv/inventaire -type f -name '*.bak' -ls
```

```text
  8590673      8 -rw-r--r--   1 root     root         5120 May 14  2025 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
   379150     32 -r--------   1 camille  camille     30720 Jun  1 13:40 /srv/inventaire/sauvegardes/base.sql.bak
```

The first two columns are the inode number and the space actually used on disk
in blocks, two pieces of information that `ls -l` does not give.

### Deleting, with the precautions that go with it

> The commands in this section destroy files. Only run them on a throwaway tree,
> never from `/` nor from a system directory. The absolute rule: first run the
> search on its own, read the list, and only then add the action.

A sandbox:

```bash
mkdir -p /tmp/bac/sous
touch /tmp/bac/a.tmp /tmp/bac/facture.pdf /tmp/bac/sous/b.tmp
```

First look:

```bash
find /tmp/bac -type f -name '*.tmp'
```

```text
/tmp/bac/sous/b.tmp
/tmp/bac/a.tmp
```

The list is the expected one, so add `-delete`:

```bash
find /tmp/bac -type f -name '*.tmp' -delete
find /tmp/bac
```

```text
/tmp/bac
/tmp/bac/sous
/tmp/bac/facture.pdf
```

`-exec rm {} +` does exactly the same thing and is suitable when `-delete` is
not available. On a second, identical sandbox:

```bash
mkdir -p /tmp/bac3/sous
touch /tmp/bac3/a.tmp /tmp/bac3/facture.pdf /tmp/bac3/sous/b.tmp
find /tmp/bac3 -type f -name '*.tmp' -exec rm {} +
find /tmp/bac3
```

```text
/tmp/bac3
/tmp/bac3/sous
/tmp/bac3/facture.pdf
```

Now the accident. `-delete` is an **action**, not a filter, and `find` evaluates
its expression from left to right. Placed before the name, it applies to
everything the walk meets, that is, to the entire tree:

```bash
mkdir -p /tmp/bac2/sous
touch /tmp/bac2/a.tmp /tmp/bac2/facture.pdf /tmp/bac2/sous/b.tmp
find /tmp/bac2 -delete -name '*.tmp'
find /tmp/bac2
```

```text
find: ‘/tmp/bac2’: No such file or directory
```

The starting directory itself has been deleted, with all its contents,
including `facture.pdf` which had asked for nothing. No error is reported by the
offending command: it did what you wrote. Remember that **`-delete` always goes
last**, after all the filters.

When in doubt, `-ok` behaves like `-exec` but asks for confirmation on each file
before acting.

### `locate`: the index, fast but out of date

`find` searches the disk on every call. `locate` queries a database built in
advance, which is incomparably faster and incomparably less reliable.

```bash
sudo dnf install -y plocate
sudo updatedb
locate inventaire
```

```text
/srv/inventaire
/srv/inventaire/lien-rapports
/srv/inventaire/notes de reunion.txt
/srv/inventaire/partage
/srv/inventaire/rapports
/srv/inventaire/sauvegardes
/srv/inventaire/scripts
/srv/inventaire/partage/depot.txt
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/sauvegardes/ancien
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
```

`locate` lists files and directories alike, and its pattern is looked for
anywhere in the path, not only in the name.

The flaw can be demonstrated in three lines. Create a file, then look for it
with both tools:

```bash
sudo touch /srv/inventaire/rapports/tout-neuf.csv
locate tout-neuf.csv          # return code 1, no line
find /srv/inventaire -name 'tout-neuf.csv'
```

```text
/srv/inventaire/rapports/tout-neuf.csv
```

`locate` sees nothing, `find` finds it immediately. After a `sudo updatedb`,
`locate` finds it in turn. The index is rebuilt once a day by a systemd timer,
never in real time:

```bash
systemctl cat plocate-updatedb.timer
```

```text
# /usr/lib/systemd/system/plocate-updatedb.timer
[Unit]
Description=Update the plocate database daily

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
AccuracySec=6h
Persistent=true
```

**If freshness matters, it is `find` and nothing else.** `locate -i` ignores
case, like `-iname`.

> The companion guide says to install `mlocate` on RHEL and derivatives. On
> AlmaLinux 10, that package no longer exists: `dnf info mlocate` answers
> `No matching Packages to list`, and it is `plocate` that is shipped in the
> `baseos` repository. `dnf provides '*/bin/locate'` confirms it.

### `grep`: searching inside the content, and combining it with `find`

`find` and `locate` search for file **names**, `grep` searches for **text**
inside. `-r` makes the search recursive, `-n` adds the line number, `-i` ignores
case, `-l` prints only the names of matching files and `-v` inverts the
selection.

The two tools go together very well: `find` selects on system criteria that
`grep` cannot see (size, age, mode, owner), then `grep` decides on the content.

```bash
sudo find /srv/inventaire -type f -name '*.sh' -exec grep -Hn 'echo' {} +
```

```text
/srv/inventaire/scripts/collecte.sh:2:echo collecte
/srv/inventaire/scripts/purge.sh:2:echo purge
```

`-H` forces the file name to be printed, which is useful because `grep` omits it
when it receives a single argument, something that happens with `-exec ... \;`
and makes the output ambiguous.

### Which command for which need

| Need | Command |
|---|---|
| Find by name, result certain and up to date | `find /path -name 'pattern'` |
| Find by name, immediate result | `locate pattern` |
| Filter by size, type, date, mode, owner | `find` with `-size`, `-type`, `-mtime`, `-perm`, `-user` |
| Search for text in files | `grep 'pattern' file` |
| Search for text in a whole tree | `grep -r 'pattern' /path/` |
| Cross a system criterion with content | `find … -exec grep -Hn 'pattern' {} +` |

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `paths must precede expression` | the glob was not quoted, the shell expanded it |
| Nothing comes out although the file exists | pattern with a `/` passed to `-name`: use `-path` |
| An expected file is missing with `-size -1M` | rounding up to the block: switch to bytes with `c` |
| An expected file is missing with `-mtime +N` | it is in the `-mtime N` slice, neither `+N` nor `-N` |
| `-perm` returns almost nothing | exact mode requested: try `-perm -mode` |
| `-perm` returns almost everything | `-perm /mode` needs a single bit: try `-perm -mode` |
| The `-type f` seems ignored | a `-o` without parentheses split the expression in two |
| `Permission denied` all over the place | redirect the error channel: `2>/dev/null` |
| `warning: … global option -maxdepth after the argument` | write `-maxdepth` before the tests |
| A name with a space explodes into several entries | `$(find …)` re-read by the shell: use `-print0` with `xargs -0`, or `-exec` |
| The symbolic link does not appear in `-type f` | that is normal: `-type l`, or `-L` to follow it |
| `find … -prune` prints nothing | the final `-print` after the `-o` is missing |
| `locate` does not find a recent file | the index is out of date: `sudo updatedb`, or use `find` |
| Too many results | narrow the starting point or add `-maxdepth` |

To undo everything and put the machine back in its original state:

```bash
sudo rm -rf /srv/inventaire /srv/verif /tmp/bac /tmp/bac2 /tmp/bac3
sudo userdel -r camille
sudo dnf remove -y plocate      # if you installed it for the demonstration
```
