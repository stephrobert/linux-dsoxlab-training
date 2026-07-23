# Lab — Read and decode a command

## Reminder

[**Anatomy of a Linux command**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/anatomie-commande/)

Every Linux command follows the same pattern: `command [options] [arguments]`.
The **command** is the program to run, the **options** modify its behaviour, the
**arguments** say what it acts on. The guide draws a promise from it:
understanding this structure means being able to read **every** command you will
come across, without learning them by heart. This lab adds what the structure
alone does not say: that the shell transforms your line **before** the command
sees it, and that a synopsis line reads like a notation, not like a sentence.

Querying the documentation (`--help`, `man`, `apropos`, `type`) is covered in
the neighbouring lab `l1-get-help`: none of that is repeated here.

## The course

The examples below work in `/tmp/cours-l1-anatomie`, a small setup that you
build yourself and will throw away at the end. The challenge is about other
files and other commands: the point is to learn to break a line down, not to
copy the solution.

All the output reproduced here was recorded on **Ubuntu 24.04.2 LTS** with
`GNU bash, version 5.2.21(1)-release` and `coreutils 9.4`, **without a single
`sudo`**: everything happens in `/tmp`, where your account can write. The
machine is in a French locale, hence the dates of the form `juil. 22 18:43`.
The behaviour described is that of **bash**: other shells (zsh in particular)
handle some of the cases below differently, which is pointed out when it
matters. Set the scene:

```bash
mkdir -p /tmp/cours-l1-anatomie/bilans
cd /tmp/cours-l1-anatomie
printf 'lundi\nmardi\nmercredi\njeudi\nvendredi\nsamedi\ndimanche\n' > journal-01.log
printf 'janvier\nfevrier\nmars\n' > journal-02.log
printf 'note interne\n' > rapport.md
touch bilans/.cache-vide
```

### The three parts, and the order that matters

`ls -l journal-01.log` answers
`-rw-rw-r-- 1 student student 52 juil. 22 18:43 journal-01.log`, and this line
breaks down into three blocks:

```text
  ls          -l          journal-01.log
  ──          ──          ──────────────
  │           │                 │
  │           │                 └─ argument: what you act on
  │           └─ option: how you do it (detailed format)
  └─ command: the program that runs
```

These three blocks are separated by **spaces**, and it is the shell that splits
the line on them. A command therefore does not receive a sentence: it receives
a **list of words**. Everything that follows comes from there.

The order of the options among themselves does not matter at all, and the shell
does not reorder them: it is the command that processes them all before acting.
The three following lines give the same output:

```bash
ls -l -a bilans
ls -a -l bilans
ls -al bilans
```

```text
total 8
drwxrwxr-x 2 student student 4096 juil. 22 18:43 .
[...]
-rw-rw-r-- 1 student student    0 juil. 22 18:43 .cache-vide
```

The order of the **arguments**, on the other hand, almost always matters,
because each position has a role. `grep` expects the pattern first, the files
afterwards: swap them, and `grep journal-01.log mardi` answers
`grep: mardi: No such file or directory`. The searched pattern has become
`journal-01.log` and `mardi` was taken for a file name. The command guessed
nothing: it read the words in order.

One last point, specific to the GNU tools: `ls bilans -la` works, options after
the argument, whereas the POSIX standard would want `-la` to be taken for a
file name. This can be checked by switching `ls` back to POSIX mode:
`POSIXLY_CORRECT=1 ls bilans -la` answers
`ls: cannot access '-la': No such file or directory`. So keep the canonical
order from the guide: options first, arguments afterwards.

### Short, long, grouped and value-taking options

A short option is a dash and **one letter** (`-l`), a long option two dashes
and **one word** (`--all`). Short ones group behind a single dash: `-la` is
exactly `-l -a`, as the previous section showed. Long ones never group.

Some options expect a **value**. There are four forms, and they are equivalent:

```bash
head -n 2 journal-01.log      # short, separated value
head -n2 journal-01.log       # short, attached value
head --lines=2 journal-01.log # long, with the equals sign
head --lines 2 journal-01.log # long, separated value
```

```text
lundi
mardi
```

A value-taking option **consumes the next word**, whatever it is. Forget the
value and the file name replaces it: `head -n journal-01.log` answers
`head: invalid number of lines: ‘journal-01.log’`.

Same rule in a group: the value-taking option must be the **last** of the
bundle, otherwise everything that follows it is swallowed as a value. So
`head -vn2 journal-01.log` does display the first two lines, preceded by
`==> journal-01.log <==`; the same letters in the other order,
`head -n2v journal-01.log`, answer `head: invalid number of lines: ‘2v’`.

> **No option is universal.** The guide insists on this point, and the help
> screens confirm it: `-r` is `--recursive` for `grep`, but `--reverse` for
> `sort`. Likewise `--lines=2`, which `head` understands, makes `ls` answer
> `ls: unrecognized option '--lines=2'`. Each command defines its own.

### `--`: the end of the options

The shell splits the line into words, and the command then decides which words
are options: those starting with a dash. A file whose name starts with a dash
therefore becomes unreadable. Make one:

```bash
printf 'contenu piege\n' > ./-journal.log
head -n1 -journal.log
```

```text
head: invalid option -- 'j'
Try 'head --help' for more information.
```

`head` did not look for a file: it read `-journal.log` as the option group
`-j -o -u -r ...` and stopped on the first unknown one. Two solutions, both
valid:

```bash
head -n1 -- -journal.log   # -- : everything that follows is an argument
head -n1 ./-journal.log    # the name no longer starts with a dash
```

```text
contenu piege
contenu piege
```

The most dangerous case is that of a file named `-f`, because `rm` knows that
option. The guide announces an error; the machine does worse:

```bash
mkdir piege && cd piege
touch ./-f
rm -f
echo "code retour = $?"
ls
```

```text
code retour = 0
-f
```

No message, a return code of `0`, and the file **still there**: `rm -f` was
understood as "remove, without asking anything, no file at all". A command that
fails silently costs more than a command that refuses. `rm -- -f` removes it
for good (`ls -A` returns nothing any more); then come back to the setup with
`cd ..`. With a letter unknown to `rm`, the message is in fact very well made:
`rm -x` answers `rm: invalid option -- 'x'`, then
`Try 'rm ./-x' to remove the file '-x'.`

### What the shell does before the command starts

This is the point the `command [options] [arguments]` structure hides: the line
you type is **not** the one the command receives. The shell transforms it
first. `echo` lets you observe everything without breaking anything, since it
merely displays the words it is given.

```bash
echo *.log
echo "*.log"
echo '*.log'
```

```text
journal-01.log journal-02.log -journal.log
*.log
*.log
```

The `*` wildcard is expanded by the **shell**, not by the command: `echo` never
saw a star, it received three words. Between quotes, single or double, the star
is no longer a wildcard and the word goes through as is.

A direct consequence, and it is today's trap: the expansion can produce an
argument that starts with a dash. `ls *.log`, a correct command nonetheless,
answers `ls: invalid option -- 'j'`: it is `-journal.log`, picked up by the
star, that was read as options. `ls -l -- *.log` does list the three files. To
see what the command really receives, `set -x` displays the line **after**
transformation, preceded by a `+`:

```bash
set -x
head -n1 *.log
set +x
```

```text
+ head -n1 journal-01.log journal-02.log -journal.log
head: invalid option -- 'j'
```

When the pattern matches **no** file, bash does not expand it and passes the
literal pattern, which produces a confusing message: `head -n1 *.csv` answers
`head: cannot open '*.csv' for reading: No such file or directory`. The file
`*.csv` does not exist, indeed: nobody ever asked `head` to understand the
star. (Under zsh, the same line fails earlier, with
`zsh:1: no matches found: *.csv`.)

There remains the difference between the two kinds of quotes. **Double** ones
let the shell replace variables, **single** ones block everything:

```bash
echo "$HOME"
echo '$HOME'
```

```text
/home/student
$HOME
```

They have a second role: without them, multiple spaces disappear when the line
is split into words. `echo bonjour     tout   le monde` displays
`bonjour tout le monde`, the same line between double quotes keeps its spaces.
Hence the classic, on a file whose name contains a space:

```bash
printf 'brouillon\n' > "mon rapport.md"
head -n1 mon rapport.md
```

```text
head: cannot open 'mon' for reading: No such file or directory
==> rapport.md <==
note interne
```

Two words, so two arguments, so two files requested: `head` displayed the
second one topped with its name, as it does as soon as it receives several
files. `head -n1 "mon rapport.md"` answers `brouillon`.

### Reading a synopsis line

The first line of a `--help` (and the `SYNOPSIS` section of a manual page) is
not a sentence: it is a notation, the same everywhere.

| Notation | Meaning |
|---|---|
| `word` in capitals | to be replaced by your value |
| `[ ]` | optional |
| `...` | repeatable |
| `\|` | a choice, one **or** the other |
| `or:` | another form of invocation, complete |

Take a real case, the first line of `grep --help`:

```text
Usage: grep [OPTION]... PATTERNS [FILE]...
```

Word for word: `grep` accepts **zero, one or several** options (`[OPTION]` in
brackets so optional, followed by `...` so repeatable); then **exactly one**
`PATTERNS`, without brackets, so **mandatory**; then **as many** `FILE` **as you
want, including none**. Both predictions check out:

```bash
grep
grep mardi journal-01.log journal-02.log
```

```text
Usage: grep [OPTION]... PATTERNS [FILE]...
Try 'grep --help' for more information.
journal-01.log:mardi
```

Without a pattern, `grep` refuses and **returns its own synopsis line** to you:
that message is not a blunt rejection, it is the answer to your question. With
two files, it prefixes each result with the file name. Compare with `mkdir`,
whose argument is mandatory **and** repeatable (`DIRECTORY...`, without
brackets): `mkdir` alone answers `mkdir: missing operand`, while
`mkdir -p bilans/2024 bilans/2025` creates both.

The vertical bar and the multiple forms can be read on the first two lines of
`date --help`:

```text
Usage: date [OPTION]... [+FORMAT]
  or:  date [-u|--utc|--universal] [MMDDhhmm[[CC]YY][.ss]]
```

Two distinct usages: displaying the date, or setting it. In the second one,
`-u|--utc|--universal` announces three spellings of one and the same option,
and `[MMDDhhmm[[CC]YY][.ss]]` **nested** brackets: the century, the year and
the seconds are each optional inside an argument that is itself optional. The
vertical bar can be checked in one line: `date -u +%H:%M`, `date --utc +%H:%M`
and `date --universal +%H:%M` all three answered `16:37`.

### Troubleshooting

One last reflex before the table: `echo $?` gives the return code of the last
command. The guide gives the list of them; the four you will come across are
`0` (success), `1` (error), `2` (misuse) and `127` (command not found).

| Symptom | Likely cause | Check |
|---|---|---|
| `invalid option -- 'x'` on a correct command | an argument starts with a dash | run it again with `--` before the arguments |
| `command not found`, code `127` | typo or missing package | check the spelling, then `type` |
| `No such file or directory` on a name you can see | space in the name, or wrong path | put quotes around the argument |
| `invalid number of lines: 'file'` | value-taking option without its value | put the value back right after the option |
| a command acts on more files than expected | a wildcard was expanded by the shell | replay the line with `echo` in front |
| `cannot open '*.ext'` | the wildcard found nothing, the pattern went through as is | check with `ls` that files exist |
| the command does nothing and returns `0` | the argument was taken for an option | `set -x` to see the real line |

To finish, wipe the setup:

```bash
cd ~ && rm -rf /tmp/cours-l1-anatomie
```
