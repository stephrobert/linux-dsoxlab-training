# Lab — Redirections and pipes

## Reminder

[**Redirections and pipes on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/)

Every command has three streams: standard input (0), standard output (1) and
standard error (2). `>` sends stdout to a file (overwrite), `>>` appends, `2>`
sends stderr, `2>&1` merges stderr into stdout, and `|` feeds one command's
output into the next. Getting the operator wrong loses data silently.

## The course

The examples below work in `~/demo-flux`, on a demonstration file
`releve.txt`: the challenge will give you another file and ask you for other
artefacts. The point is to learn the method, not to copy a line.

All the output reproduced here was obtained on an AlmaLinux 10 with `bash` 5.2.
A redirection never warns you: it overwrites, it truncates, it loses an error
without a word. The only defence is to know exactly what each operator does,
and that can be checked in two lines.

### The demonstration setup

```bash
mkdir -p ~/demo-flux && cd ~/demo-flux
cat > releve.txt <<'EOF'
2026-07-20 OK sauvegarde quotidienne
2026-07-20 WARN espace disque faible
2026-07-21 OK sauvegarde quotidienne
2026-07-21 WARN certificat bientot expire
2026-07-22 OK sauvegarde quotidienne
EOF
```

This first block already uses a redirection: `cat > releve.txt` takes its
standard input (here the `<<'EOF'` document) and writes it into the file. Five
lines, two of which are `WARN`.

One point of vocabulary that avoids a lot of confusion: **the redirection is
done by the shell, not by the command**. `ls` does not know it is writing into
a file; it is `bash` that opened the file and plugged the output descriptor
onto it before starting `ls`. Everything that follows comes from that single
fact.

### The three streams, seen from the process

The table in the guide can be checked directly: `/proc/self/fd` shows where the
descriptors of a running process point.

```bash
bash -c 'ls -l /proc/self/fd' > rapport.out 2> defauts.err
cat rapport.out
```

```text
total 0
lr-x------. 1 ansible ansible 64 Jul 22 14:15 0 -> pipe:[52264]
l-wx------. 1 ansible ansible 64 Jul 22 14:15 1 -> /home/ansible/demo-flux/rapport.out
l-wx------. 1 ansible ansible 64 Jul 22 14:15 2 -> /home/ansible/demo-flux/defauts.err
lr-x------. 1 ansible ansible 64 Jul 22 14:15 3 -> /proc/13792/fd
```

Descriptor `1` (standard output) points at `rapport.out`, `2` (standard error)
at `defauts.err`. Without a redirection, both would point at the terminal. `0`
is standard input, `3` is a temporary descriptor opened by `ls` to read the
directory. `defauts.err` stayed empty: the command produced no error.

### `>` overwrites, `>>` appends

```bash
grep OK releve.txt > alertes.out
cat alertes.out
```

```text
2026-07-20 OK sauvegarde quotidienne
2026-07-21 OK sauvegarde quotidienne
2026-07-22 OK sauvegarde quotidienne
```

A second `>` on the same file does not complete the previous one, it replaces
everything:

```bash
grep WARN releve.txt > alertes.out
cat alertes.out
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
```

The three `OK` lines are gone. With `>>`, they would have been added:

```bash
grep OK releve.txt >> alertes.out
cat alertes.out
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
2026-07-20 OK sauvegarde quotidienne
2026-07-21 OK sauvegarde quotidienne
2026-07-22 OK sauvegarde quotidienne
```

Standard input is redirected with `<`, and the result is not quite the same as
an argument:

```bash
wc -l releve.txt      # 5 releve.txt
wc -l < releve.txt    # 5
```

In the first case `wc` knows the name of the file and prints it, in the second
it reads an anonymous stream and outputs only the number. When you want a file
that contains nothing but a number, `<` is the right tool.

### The `>` trap: it empties the file before the command starts

This is the most expensive point of the whole topic. The shell opens (and
truncates) the destination file **first**, then starts the command. If the
command fails, the file has been emptied all the same.

```bash
printf 'ligne A\nligne B\n' > important.txt
wc -c < important.txt                       # 16
grep MOTIF-ABSENT-XYZ absent.txt > important.txt
```

```text
grep: absent.txt: No such file or directory
```

```bash
echo $?                 # 2
wc -c < important.txt   # 0
```

The file `important.txt` is empty although `grep` wrote nothing at all, and
even failed. Worse, this also holds when the command does not exist:

```bash
printf 'ligne A\nligne B\n' > important.txt
commande-qui-nexiste-pas > important.txt
```

```text
bash: commande-qui-nexiste-pas: command not found
```

```bash
echo $?                 # 127
wc -c < important.txt   # 0
```

The shell truncated the file before discovering that the command did not exist.
A useful corollary: a redirection **without a command** empties a file.

```bash
printf 'du contenu\n' > jetable.txt
wc -c < jetable.txt   # 11
> jetable.txt
wc -c < jetable.txt   # 0
```

`bash` can protect you from these accidents with the `noclobber` option, which
refuses to overwrite an existing file:

```bash
set -o noclobber
echo ecrase > protege.txt
```

```text
bash: protege.txt: cannot overwrite existing file
```

The return code is `1` and the original content is intact. A `>|` forces the
overwrite despite `noclobber`, and `set +o noclobber` returns to the usual
behaviour. It is a session safeguard, not a property of the file: do not count
on it on a machine you do not configure.

### Redirecting errors with `2>`

A command that fails does not write on standard output. Let us separate the two
streams of a single command:

```bash
ls releve.txt absent.txt > part1.out 2> part2.err
cat part1.out
```

```text
releve.txt
```

```bash
cat part2.err
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

Remember the sizes, they will be useful: 11 bytes on standard output, 58 on
standard error.

### Merging the two streams: the order matters

`2>&1` does not mean "merge stdout and stderr", but "make descriptor 2 point
where descriptor 1 points **at this instant**". Since the shell processes
redirections from left to right, the position of `2>&1` changes everything.

The correct form, `2>&1` **after** the output redirection:

```bash
ls releve.txt absent.txt > fusion.out 2>&1
cat fusion.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
releve.txt
```

Both streams are in the file, nothing stays on the screen. Note in passing that
the error comes before the normal output: in a merged file, the order of the
lines is not that of the command line. Here `ls` reports the impossible access
before printing its list, and forcing the absence of buffering with
`stdbuf -o0` does not change that order.

The trapped form, `2>&1` **before**:

```bash
ls releve.txt absent.txt 2>&1 > fusion2.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

```bash
cat fusion2.out
```

```text
releve.txt
```

The error was displayed on the screen, only standard output is in the file. At
the moment `2>&1` is processed, descriptor 1 still points at the terminal:
descriptor 2 is therefore plugged onto the terminal. The `> fusion2.out` that
follows only moves descriptor 1, and 2 stays where it was put.

This can be proven by capturing the two streams of the calling shell
separately:

```bash
bash -c 'ls releve.txt absent.txt 2>&1 > fusion2.out' > echappe.out 2> reste.err
cat echappe.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

```bash
cat reste.err    # empty
```

The error did go to the **former** standard output, not to standard error.
`reste.err` is empty.

### `> f 2> f` is not `&> f`

The temptation to write two redirections towards the same file name is strong.
The result is a damaged file.

```bash
ls releve.txt absent.txt > double.out 2> double.out
cat double.out
```

```text
releve.txt
access 'absent.txt': No such file or directory
```

The error message lost its beginning, `ls: cannot `, exactly 11 characters: the
length of `releve.txt` plus the newline. The two `>` opened the file **twice**,
each opening having its own write position, both at zero. The two streams
therefore wrote over each other.

The arithmetic confirms it:

```bash
wc -c < double.out    # 58
```

58 bytes, the size of the error message alone, whereas the two streams total 69
bytes. Eleven bytes were lost.

`&>` (or the portable form `> f 2>&1`) opens the file only once and makes both
descriptors share the same position:

```bash
ls releve.txt absent.txt &> simple.out
wc -c < simple.out    # 69
cat simple.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
releve.txt
```

69 bytes: 58 + 11, nothing is lost. The version that appends instead of
overwriting is written `&>>` or `>> file 2>&1`.

One misleading detail: `ls -l /proc/self/fd` displays the same destination file
in both cases. What differs is not the target but the write position, and it is
visible nowhere. Hence the simple rule: **never two redirections towards the
same file**.

### The pipe carries standard output only

A `|` connects the standard output on the left to the standard input on the
right. Standard error does not enter the pipe and goes on to the screen.

```bash
bash -c 'ls releve.txt absent.txt | wc -l' 2> tube-erreurs.err
```

```text
1
```

```bash
cat tube-erreurs.err
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

`wc -l` counted only one line: the error went past the pipe. That is why a
`command | grep pattern` will never find an error message, and why a count made
at the end of a pipe silently ignores failures.

To make standard error enter the pipe, you have to merge it first:

```bash
ls releve.txt absent.txt 2>&1 | wc -l    # 2
ls releve.txt absent.txt |& wc -l        # 2
```

`|&` is the `bash` shorthand for `2>&1 |`. Be careful not to put the `2>&1` on
the wrong side: in `ls releve.txt absent.txt | grep cannot 2>&1`, the
redirection applies to `grep`, not to `ls`, and `grep` finds nothing (return
code 1).

A pipe can be chained as much as needed, each link doing only one thing:

```bash
cut -d' ' -f2 releve.txt | sort | uniq -c
```

```text
      3 OK
      2 WARN
```

`cut` extracts the second field, `sort` groups identical values, `uniq -c`
counts them. No intermediate file was created.

### The return code of a pipe, `PIPESTATUS` and `pipefail`

The return code of a pipe is that of its **last** command. Upstream failures
are therefore invisible.

```bash
grep MOTIF-ABSENT-XYZ releve.txt | wc -l
echo $?
```

```text
0
0
```

`grep` found nothing (it returns 1), but `wc` perfectly succeeded in counting
zero lines, and it is its code that came back. A script testing `$?` here will
conclude that all is well.

`bash` keeps every code in the `PIPESTATUS` array:

```bash
grep MOTIF-ABSENT-XYZ releve.txt | wc -l > /dev/null
echo "${PIPESTATUS[@]}"
```

```text
1 0
```

The most telling case is that of a missing command at the head of a pipe:

```bash
commande-absente-xyz | wc -l > /dev/null
```

```text
bash: commande-absente-xyz: command not found
```

```bash
echo "$? / ${PIPESTATUS[@]}"
```

```text
0 / 127 0
```

Global return code `0` although the first command failed with 127.
`PIPESTATUS` must be read **immediately**: the slightest following command
overwrites it.

The `pipefail` option fixes the behaviour globally: the pipe then returns the
code of the last failing link.

```bash
bash -c 'set -o pipefail; grep MOTIF-ABSENT-XYZ releve.txt | wc -l > /dev/null; echo $?'
bash -c '                  grep MOTIF-ABSENT-XYZ releve.txt | wc -l > /dev/null; echo $?'
```

```text
1
0
```

That is why a serious script often starts with `set -o pipefail`, generally
with `set -euo pipefail`.

### `tee`: see and record at the same time

A `>` redirection sends everything into the file and nothing to the screen any
more. `tee` does both: it writes into the file and copies to its standard
output.

```bash
grep WARN releve.txt | tee suivi.log
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
```

The content was displayed, and `suivi.log` contains exactly the same two lines.
`tee` without an option **overwrites** the file, like `>`; `tee -a` appends,
like `>>`:

```bash
grep OK releve.txt | tee -a suivi.log
cat suivi.log
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
2026-07-20 OK sauvegarde quotidienne
2026-07-21 OK sauvegarde quotidienne
2026-07-22 OK sauvegarde quotidienne
```

`tee` is at the end of the pipe: it therefore sees only standard output, like
everything else in the pipe. A `command | tee log` does not keep the errors,
unless you write `command 2>&1 | tee log`.

### `sudo` does not apply to the redirection

A classic mistake: you think you are writing into a protected file because
`sudo` is on the line, and the shell refuses.

```bash
sudo mkdir -p /etc/demo-flux.d
sudo touch /etc/demo-flux.d/reglage.conf     # owned by root, mode 0644
sudo echo "parametre=1" > /etc/demo-flux.d/reglage.conf
```

```text
bash: /etc/demo-flux.d/reglage.conf: Permission denied
```

The return code is `1`, and nothing was written. The reason is the one from the
beginning of this course: **the redirection is done by the calling shell**,
which runs under your account. `sudo` only elevates the `echo` command, which
has already lost the game before starting. Two correct ways of going about it:

```bash
echo "parametre=1" | sudo tee /etc/demo-flux.d/reglage.conf
sudo sh -c 'echo parametre=2 > /etc/demo-flux.d/reglage.conf'
```

Both return `0` and the file does contain the value. In the first case it is
`tee`, started by `sudo`, that opens the file; in the second it is a whole
shell running as root, redirection included. `tee` displays what it writes,
hence the usual `> /dev/null` when you do not want a duplicate on the screen,
and `sudo tee -a` to add a line without overwriting the file.

### `/dev/null`: throwing away the output, or throwing away the errors

`/dev/null` is a special file that swallows everything sent to it. What matters
is knowing **which** stream you send there: it is not at all the same gesture.

```bash
find /etc -name '*.conf' 2>&1 | wc -l        # 114
find /etc -name '*.conf' 2>/dev/null | wc -l # 99
bash -c "find /etc -name '*.conf' > /dev/null" 2>&1 | wc -l   # 15
```

On this machine and without privileges: 114 lines in total, of which 99 are
useful results and 15 are errors. `2>/dev/null` throws away the 15 errors and
keeps the results; `> /dev/null` does exactly the opposite. The discarded
errors look like this:

```text
find: ‘/etc/pki/rsyslog’: Permission denied
find: ‘/etc/credstore’: Permission denied
```

`> /dev/null 2>&1` throws away both and leaves only the return code: that is
the form used in scheduled tasks and silent tests.

> Throwing away standard error is comfortable, but `2>/dev/null` also hides the
> errors you were not expecting. On a diagnostic command, prefer
> `2> /tmp/erreurs.err`: you keep a readable result and you can still reread
> what failed.

### Summary

| Form | Effect |
|---|---|
| `cmd > f` | standard output into `f`, `f` is truncated first |
| `cmd >> f` | standard output appended to the end of `f` |
| `> f` | truncates `f` (or creates it), without running a command |
| `cmd < f` | `f` becomes the standard input of `cmd` |
| `cmd 2> f` | standard error alone into `f` |
| `cmd 2>> f` | standard error appended to `f` |
| `cmd > f 2>&1` | both streams into `f`, portable |
| `cmd &> f` | both streams into `f`, `bash` shorthand |
| `cmd &>> f` | both streams appended to `f` |
| `cmd 2>&1 > f` | **trap**: only standard output goes into `f` |
| `cmd > f 2> f` | **trap**: two openings, the streams overwrite each other |
| `cmd \| other` | standard output of `cmd` to the input of `other` |
| `cmd 2>&1 \| other` | both streams into the pipe (`cmd \|& other` in `bash`) |
| `cmd \| tee f` | displays and records (overwrites `f`) |
| `cmd \| tee -a f` | displays and appends to `f` |
| `cmd 2>/dev/null` | throws away the errors, keeps the result |
| `cmd > /dev/null` | throws away the result, keeps the errors |
| `cmd > /dev/null 2>&1` | throws away everything, keeps only the return code |

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| The destination file is empty and the command failed | `>` truncates before starting the command; use a temporary file then `mv` |
| The previous content is gone | `>` instead of `>>`, or `tee` without `-a` |
| The error still shows on the screen despite `2>&1` | `2>&1` placed before the output redirection; it must come after |
| The merged file has truncated lines | `> f 2> f`: two independent openings, write `> f 2>&1` or `&> f` |
| `grep` at the end of a pipe does not find the error message | the pipe only carries standard output; add `2>&1` before the `\|` |
| A script goes on although a command in the pipe failed | the pipe returns the code of the last link; read `PIPESTATUS` or set `set -o pipefail` |
| `PIPESTATUS` does not contain what you expect | it is overwritten by the next command; copy it into a variable straight away |
| `Permission denied` although `sudo` is on the line | the redirection is done by the calling shell; go through `sudo tee` or `sudo sh -c` |
| `cannot overwrite existing file` | the `noclobber` option is active; `>\|` to force, `set +o noclobber` to remove it |
| The file contains only a number, when you also wanted the name | `wc -l < f` hides the name; `wc -l f` keeps it |
| Nothing comes out of a pipe | the first command produces nothing on its standard output; test it on its own |

To undo everything and start again from scratch:

```bash
rm -rf ~/demo-flux
sudo rm -rf /etc/demo-flux.d
```
