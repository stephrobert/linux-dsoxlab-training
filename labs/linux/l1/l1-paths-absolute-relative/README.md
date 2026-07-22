# Lab — absolute and relative paths

## Reminder

[**Absolute and relative paths on Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/chemins-linux/)

Every command that touches a file must first know where it is. An **absolute**
path starts with `/`: it starts from the root and designates the same location
whatever the place you type it from. A **relative** path does not start with `/`:
the shell resolves it from the current directory, the one `pwd` displays. Four
notations complete the writing of paths: `.` (here), `..` (the parent
directory), `~` (your home directory) and `-` (the previous directory, with `cd`
only).

## The course

The examples below work in `/tmp/cours-l1-paths`, a small tree you build
yourself and will throw away at the end: the challenge will deal with other
directories and other files. The point is to learn to read and write a path, not
to copy a line.

Every output reproduced here was obtained with `GNU bash, version
5.2.21(1)-release` and `realpath (GNU coreutils) 9.4`.

### The demonstration setup

Build the tree. No command in this section needs `sudo`: everything happens in
`/tmp`, where your account can write.

```bash
mkdir -p /tmp/cours-l1-paths/atelier/notes
mkdir -p /tmp/cours-l1-paths/atelier/outils
mkdir -p /tmp/cours-l1-paths/atelier/archives/2019
echo 'Memo du mardi.' > /tmp/cours-l1-paths/atelier/notes/memo.txt
echo 'Bilan 2019.'    > /tmp/cours-l1-paths/atelier/archives/2019/bilan.md
find /tmp/cours-l1-paths | sort
```

```text
/tmp/cours-l1-paths
/tmp/cours-l1-paths/atelier
/tmp/cours-l1-paths/atelier/archives
/tmp/cours-l1-paths/atelier/archives/2019
/tmp/cours-l1-paths/atelier/archives/2019/bilan.md
/tmp/cours-l1-paths/atelier/notes
/tmp/cours-l1-paths/atelier/notes/memo.txt
/tmp/cours-l1-paths/atelier/outils
```

Every line of that output is an absolute path: it starts with `/`.

### Absolute or relative: the difference can be measured

A relative path means nothing as long as you do not know where you type it from.
The same command, run from two different directories, therefore does not do the
same thing. Here is the demonstration.

```bash
cd /tmp/cours-l1-paths/atelier/notes
pwd
cat memo.txt
cd /tmp/cours-l1-paths/atelier/outils
pwd
cat memo.txt
```

```text
/tmp/cours-l1-paths/atelier/notes
Memo du mardi.
/tmp/cours-l1-paths/atelier/outils
cat: memo.txt: No such file or directory
```

The file did not move and the command did not change by one letter. Only `pwd`
changed, and that is enough to make it fail.

The absolute path, on the other hand, depends on nothing. Even from the root:

```bash
cd /
pwd
cat /tmp/cours-l1-paths/atelier/notes/memo.txt
```

```text
/
Memo du mardi.
```

### `..`, the parent directory

`..` goes up one level. You chain it as many times as needed, and you can go
back down in the same move. Each `cd` is followed by a `pwd` to see where you
landed:

```bash
cd /tmp/cours-l1-paths/atelier/notes
pwd
cd ..
pwd
cd ..
pwd
```

```text
/tmp/cours-l1-paths/atelier/notes
/tmp/cours-l1-paths/atelier
/tmp/cours-l1-paths
```

In a single command, you go up then back down into another branch:

```bash
cd /tmp/cours-l1-paths/atelier/notes
cd ../archives/2019
pwd
```

```text
/tmp/cours-l1-paths/atelier/archives/2019
```

Read `../archives/2019` from left to right: go up into `atelier`, then down into
`archives`, then into `2019`. That is exactly the reasoning you follow to build
a relative path between two points.

One particular case to know: **the root has no parent**. `cd ..` from `/`
produces neither an error nor a move.

```bash
cd /
pwd
cd ..
pwd
```

```text
/
/
```

### `.`, `~` and `-`

`.` designates the current directory. Its most frequent use is to serve as a
destination: "copy this file here".

```bash
cd /tmp/cours-l1-paths/atelier/notes
pwd
cp /tmp/cours-l1-paths/atelier/archives/2019/bilan.md .
ls
```

```text
/tmp/cours-l1-paths/atelier/notes
bilan.md
memo.txt
```

`~` is replaced by your home directory, whatever the place you are in. It is
worth the same as the `$HOME` variable:

```bash
cd /tmp/cours-l1-paths/atelier/outils
echo "$HOME"
cd ~
pwd
```

```text
/home/student
/home/student
```

On the machine that produced this output, the user is called `student`: on yours,
`pwd` will display your own home directory.

The dash `-` takes you back to the last directory visited, and `cd -` displays
along the way the directory it takes you to:

```bash
cd /tmp/cours-l1-paths/atelier/archives
pwd
cd /tmp/cours-l1-paths/atelier/outils
pwd
cd -
pwd
```

```text
/tmp/cours-l1-paths/atelier/archives
/tmp/cours-l1-paths/atelier/outils
/tmp/cours-l1-paths/atelier/archives
/tmp/cours-l1-paths/atelier/archives
```

The third line is displayed by `cd -` itself, the fourth by the `pwd` that
follows: it is indeed the same directory.

### `./script` and `script` are not the same command

This is the only place where the `.` is mandatory rather than decorative. Create
a script and run it both ways:

```bash
printf '#!/bin/bash\necho "script lance depuis $(pwd)"\n' \
  > /tmp/cours-l1-paths/atelier/outils/bonjour.sh
chmod +x /tmp/cours-l1-paths/atelier/outils/bonjour.sh
cd /tmp/cours-l1-paths/atelier/outils
./bonjour.sh
bonjour.sh
```

```text
script lance depuis /tmp/cours-l1-paths/atelier/outils
bash: bonjour.sh: command not found
```

`./bonjour.sh` is a path, the shell opens the file. `bonjour.sh` without a prefix
is a **command name**: the shell looks for it in the directories of the `PATH`,
and the current directory is not one of them. Check it: the search below returns
no line, and the return code 1 of `grep` means "no match".

```bash
echo "$PATH" | tr ':' '\n' | grep -x '\.'
echo "code retour = $?"
```

```text
code retour = 1
```

> **This is deliberate.** If the current directory were in the `PATH`, a file
> named `ls` dropped in a directory you pass through would be executed instead of
> the real `ls`. The mandatory `./` makes the intent explicit.

This script displays `pwd`. Called by its absolute path from
`/tmp/cours-l1-paths/atelier/notes` then from `/tmp`, it answers
`script lance depuis /tmp/cours-l1-paths/atelier/notes`, then
`script lance depuis /tmp`. Any relative path written inside would therefore
resolve to two different places depending on the call: that is why the guide
recommends absolute paths in scripts.

### Knowing where you really are: `pwd -P` and `realpath`

Add a symbolic link and enter it:

```bash
ln -s atelier/notes /tmp/cours-l1-paths/raccourci
cd /tmp/cours-l1-paths/raccourci
pwd
pwd -P
```

```text
/tmp/cours-l1-paths/raccourci
/tmp/cours-l1-paths/atelier/notes
```

`pwd` displays the **logical** path, the one you arrived by. `pwd -P` displays
the **physical** path, links resolved. As long as no link is crossed, the two
are identical; here they diverge.

Direct consequence, and a classic trap: `cd ..` follows the logical path.

```bash
cd ..
pwd
```

```text
/tmp/cours-l1-paths
```

You go up into the parent of the **link**, not into that of the real directory.
To reason in physical terms, enter with `cd -P /tmp/cours-l1-paths/raccourci`:
the following `cd ..` then leads to `/tmp/cours-l1-paths/atelier`.

`realpath` does the reverse of what you do in your head: it translates a
relative path into an absolute path, taking the current directory into account.

```bash
cd /tmp/cours-l1-paths/atelier/notes
realpath memo.txt
cd /tmp/cours-l1-paths/atelier/outils
realpath memo.txt
```

```text
/tmp/cours-l1-paths/atelier/notes/memo.txt
/tmp/cours-l1-paths/atelier/outils/memo.txt
```

Two different answers for the same argument: that is the very definition of a
relative path. The second one concerns, by the way, a file that does not exist,
and `realpath` answers all the same: it computes the path without requiring the
target. Add `-e` for it to refuse a nonexistent path (`realpath -e memo.txt`
then returns `realpath: memo.txt: No such file or directory` and a return code
of 1).

`readlink -f` gives the same result and additionally resolves the symbolic
links, where `realpath -s` refrains from it:

```bash
cd /tmp/cours-l1-paths
readlink -f raccourci
realpath -s raccourci
```

```text
/tmp/cours-l1-paths/atelier/notes
/tmp/cours-l1-paths/raccourci
```

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `cat: file: No such file or directory` on a relative path | you are not in the directory you think you are | `pwd`, then try again in absolute form |
| `cat: /path/…: No such file or directory` on an absolute path | typo in the path | complete with **Tab**, or `ls` on the parent directory |
| `bash: command: command not found` for a local script | the current directory is not in the `PATH` | prefix it with `./` |
| `bash: ./script.sh: Permission denied` | the script is not executable | `ls -l script.sh`, then `chmod +x script.sh` |
| `bash: cd: notes/memo.txt: Not a directory` | you gave a file to `cd` | `ls -ld` on the target |
| `pwd` and `pwd -P` do not say the same thing | you crossed a symbolic link | `ls -l` on the suspect link |
| `~` is not interpreted in a script | tilde inside quotes | use `$HOME` |

To wipe everything and start again from scratch, a single absolute path is
enough:

```bash
cd ~
rm -rf /tmp/cours-l1-paths
```
