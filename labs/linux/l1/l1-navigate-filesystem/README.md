# Lab — navigating the filesystem

## Reminder

[**Navigate and manage files under Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/)

Three commands form the tripod of navigation: `pwd` says where you are, `cd`
moves you, `ls` shows what is around. The guide draws a rule from it: after
every operation, check the result. This lab therefore trains the eye as much as
the movement: reading `ls -l` column by column, telling the content of a
directory from the directory itself, and knowing what to ask `file` and `stat`
when `ls` is no longer enough.

Writing paths (`.`, `..`, `~`, absolute against relative) is covered in the
neighbouring lab `l1-paths-absolute-relative`: it is not repeated here.

## The course

The examples below work in `/tmp/course-l1-navigate`, a small tree that you
build yourself and that you will throw away at the end. The challenge itself
will be about other directories and other files: the point is to learn to look,
not to copy a line.

Every output reproduced here was obtained on Ubuntu 24.04 with
`GNU bash 5.2.21(1)`, `ls (GNU coreutils) 9.4` and `file-5.45`, without a single
`sudo`: everything happens in `/tmp`, where your account can write. The machine
is in a French locale, hence the dates of the form `juil. 22 17:48`; in English
you will read `Jul 22 17:48`.

### The demonstration setup

```bash
mkdir -p /tmp/course-l1-navigate/library/{catalogue,loans,archives/2018}
cd /tmp/course-l1-navigate/library
printf 'title;author;year\nThe Horla;Maupassant;1887\n' > catalogue/inventory.csv
printf 'short notes\n'                        > catalogue/memo.md
head -c 120     /dev/urandom                  > catalogue/thumbnail.png
head -c 74000   /dev/urandom                  > catalogue/poster.jpg
head -c 2500000 /dev/urandom                  > loans/register.dat
printf 'Reading room information sheet.\n'    > notice.md
printf 'archive 2018\n'                       > archives/2018/summary.txt
printf 'cache\n'                              > .opening-hours
ln -s catalogue/inventory.csv latest-inventory
```

To see the whole thing at once, the reflex is `tree`. It still has to be
installed, which is not guaranteed: on the machine that produced this course, it
was not. `command -v tree` printed no line there and returned the code 1, the
proof that the command does not exist. `find` replaces it without installing
anything, and it shows on top of that the hidden files, which `ls` without
options passes over in silence.

```bash
cd /tmp/course-l1-navigate
find library | sort
```

```text
library
library/archives
library/archives/2018
library/archives/2018/summary.txt
[...]
library/notice.md
library/.opening-hours
```

`find library -type d` keeps only the directories, `-type f` only the files. The
guide also mentions `ls -R`, which lists recursively.

### `pwd` and `cd`: locating yourself, moving around

`pwd` (print working directory) prints the current directory, `cd` (change
directory) changes it. The guide gives the rule: after every `cd`, a `pwd`
confirms the position.

```bash
cd /tmp/course-l1-navigate/library/archives/2018 ; pwd
cd                                               ; pwd
```

```text
/tmp/course-l1-navigate/library/archives/2018
/home/student
```

`cd` with no argument brings you back to your home directory. On the machine
that produced this output, the user is called `student`; on yours, `pwd` will print
your own. One mistake comes back often, giving a file to `cd`: the answer is
then `bash: cd: notice.md: Not a directory`, and the return code is 1.

### Reading `ls -l` column by column

Without options, `ls` gives only names. In a terminal it spreads them over
several columns; as soon as its output goes into a pipe or a file, it switches
to one name per line. That is its default behaviour, not a setting.

`-l` (long format) is the option that does all the work:

```bash
cd /tmp/course-l1-navigate/library
ls -l
```

```text
total 16
drwxrwxr-x 3 student student 4096 juil. 22 17:48 archives
drwxrwxr-x 2 student student 4096 juil. 22 17:48 catalogue
lrwxrwxrwx 1 student student   23 juil. 22 17:48 latest-inventory -> catalogue/inventory.csv
drwxrwxr-x 2 student student 4096 juil. 22 17:48 loans
-rw-rw-r-- 1 student student   32 juil. 22 17:48 notice.md
```

Here is the last line, broken down column by column:

```text
-rw-rw-r--  1  student  student  32  juil. 22 17:48  notice.md
│           │  │        │        │   │               │
│           │  │        │        │   │               └─ name
│           │  │        │        │   └─ date of last modification (mtime)
│           │  │        │        └─ size in bytes
│           │  │        └─ owning group
│           │  └─ owning user
│           └─ number of links
└─ type and permissions
```

The very first character gives the **type**, and it is not part of the
permissions: `-` for an ordinary file, `d` for a directory, `l` for a symbolic
link. All three cases appear above, and the link additionally shows its target
after an arrow.

Three values are read wrong. The **size** of a directory (4096 here) is that of
the directory entry, not that of what it contains. The size of the link is 23:
it is the length of the path it holds, `catalogue/inventory.csv`, exactly 23
characters. And **`total 16`** is a total of disk blocks, not a number of files.

### The `ls` options that change the view

`-a` (all) adds the entries starting with a dot: `.` (the directory itself),
`..` (its parent) and the configuration files.

```text
drwxrwxr-x 5 student student 4096 juil. 22 17:48 .              # ls -la
drwxrwxr-x 3 student student 4096 juil. 22 17:48 ..
[...]
-rw-rw-r-- 1 student student    6 juil. 22 17:48 .opening-hours
```

`-h` (human readable) turns bytes into readable units. The same line, without
then with `-h`, shows that nothing else changes:

```text
-rw-rw-r-- 1 student student 2500000 juil. 22 17:48 register.dat     # ls -l  loans
-rw-rw-r-- 1 student student    2,4M juil. 22 17:48 register.dat     # ls -lh loans
```

`-h` on its own is useless: it only applies to the sizes printed by `-l`. `-S`,
for its part, sorts by decreasing size, and `-r` reverses any sort (`ls -lhSr`
would give exactly the reverse order of the four lines below):

```text
-rw-rw-r-- 1 student student 73K juil. 22 17:48 poster.jpg       # ls -lhS catalogue
-rw-rw-r-- 1 student student 120 juil. 22 17:48 thumbnail.png
-rw-rw-r-- 1 student student  44 juil. 22 17:48 inventory.csv
-rw-rw-r-- 1 student student  12 juil. 22 17:48 memo.md
```

`-t` sorts by modification date, the most recent first. Combined with `-r`, it
gives `ls -ltr`, the most useful command of the lot: the file modified last
lands right above your prompt. Change one, watch it move down:

```bash
ls -ltr
echo 'Exceptional closure on the 15th.' >> notice.md
ls -ltr
```

```text
[...]
-rw-rw-r-- 1 student student   32 juil. 22 17:48 notice.md   <- before: 3rd line out of 5
[...]
-rw-rw-r-- 1 student student   65 juil. 22 17:49 notice.md   <- after: last line
```

### `ls -l` against `ls -ld`: the content or the directory itself

This is the trap that confuses everybody. Give a directory to `ls -l`: it lists
what is **inside**. Add `-d` (directory): it describes the directory
**itself**.

```bash
ls -l  archives
ls -ld archives
```

```text
total 4
drwxrwxr-x 2 student student 4096 juil. 22 17:48 2018       <- the CONTENT of archives
drwxrwxr-x 3 student student 4096 juil. 22 17:48 archives   <- archives ITSELF
```

So `ls -ld` is what you must use as soon as you want to check the permissions or
the owner of a directory: without `-d`, you read those of its content and draw
the opposite conclusion. The difference goes further than a display: listing the
content requires the read permission on the directory, describing it requires
nothing of it. On a directory set to `chmod 000`, the two commands therefore
diverge:

```text
ls: cannot open directory 'reserve': Permission denied   # ls -l,  rc=2
d--------- 2 student student 4096 juil. 22 17:51 reserve         # ls -ld, rc=0
```

**The link counter of a directory is not a number of files.** It is 2 plus the
number of subdirectories: 1 for its name in the parent, 1 for its own `.`, and 1
per `..` of each subdirectory. Watch it climb:

```bash
mkdir -p /tmp/course-l1-navigate/counter && cd /tmp/course-l1-navigate/counter
ls -ld .
mkdir room1 ; ls -ld .
mkdir room2 ; ls -ld .
touch file1 file2 ; ls -ld .
```

```text
drwxrwxr-x 2 student student 4096 juil. 22 17:51 .   <- empty
drwxrwxr-x 3 student student 4096 juil. 22 17:51 .   <- 1 subdirectory
drwxrwxr-x 4 student student 4096 juil. 22 17:51 .   <- 2 subdirectories
drwxrwxr-x 4 student student 4096 juil. 22 17:51 .   <- + 2 files: unchanged
```

It starts at 2, climbs with the subdirectories and does not move when you add
ordinary files: a directory whose `ls -ld` prints 5 therefore contains 3
subdirectories, whatever the number of files it carries.

### `file` and `stat`: what a file really is

`ls` only shows one view. `file` inspects the **content** and does not trust the
name: copy a text file under an image extension, `ls` will believe you, `file`
will not.

```bash
cd /tmp/course-l1-navigate/library/catalogue
cp ../notice.md photo.png
file photo.png poster.jpg /bin/ls ../latest-inventory
```

```text
photo.png:           ASCII text
poster.jpg:          data
/bin/ls:             ELF 64-bit LSB pie executable, x86-64, [...] stripped
../latest-inventory: symbolic link to catalogue/inventory.csv
```

The file named `.png` is text; the one named `.jpg`, filled with random bytes,
matches no known signature and `file` answers `data`.

`stat` gives the complete **metadata**, the one that `ls -l` only summarises:
type, permissions in octal **and** in symbolic form, owner with its numeric UID,
inode, link counter and four dates.

```bash
cd /tmp/course-l1-navigate/library
stat catalogue
```

```text
  File: catalogue
  Size: 4096      	Blocks: 8          IO Block: 4096   directory
Device: 252,0	Inode: 8558931     Links: 2
Access: (0775/drwxrwxr-x)  Uid: ( 1000/ student)   Gid: ( 1000/ student)
Access: 2026-07-22 17:48:20.420444140 +0200
Modify: 2026-07-22 17:51:06.808771424 +0200
Change: 2026-07-22 17:51:06.808771424 +0200
 Birth: 2026-07-22 17:48:20.389441849 +0200
```

`-c` extracts only what you ask for, which makes `stat` usable in a script:
`stat -c '%n: %F, %s bytes, %A (%a), %U:%G, %h link(s)' catalogue` answers
`catalogue: directory, 4096 bytes, drwxrwxr-x (775), student:student, 2 link(s)`.

**The three timestamps do not measure the same thing**, and the only way to be
convinced of it is to move them one by one:

```bash
F='mtime %y\nctime %z\natime %x\n'
printf 'Monthly bulletin.\n' > bulletin.txt ; stat --printf="$F" bulletin.txt
echo 'Open on Thursdays.' >> bulletin.txt   ; stat --printf="$F" bulletin.txt
chmod 640 bulletin.txt                      ; stat --printf="$F" bulletin.txt
cat bulletin.txt > /dev/null                ; stat --printf="$F" bulletin.txt
```

A `sleep 2` was slipped between each step so that the seconds can be read:

```text
mtime 2026-07-22 18:00:02.953754056 +0200   <- initial state
ctime 2026-07-22 18:00:02.953754056 +0200
atime 2026-07-22 18:00:02.953754056 +0200
mtime 2026-07-22 18:00:04.955903833 +0200   <- the CONTENT changed
ctime 2026-07-22 18:00:04.955903833 +0200
atime 2026-07-22 18:00:02.953754056 +0200
mtime 2026-07-22 18:00:04.955903833 +0200   <- the PERMISSIONS changed
ctime 2026-07-22 18:00:06.958053611 +0200
atime 2026-07-22 18:00:02.953754056 +0200
mtime 2026-07-22 18:00:04.955903833 +0200   <- the file was READ
ctime 2026-07-22 18:00:06.958053611 +0200
atime 2026-07-22 18:00:08.963203616 +0200
```

| Timestamp | What makes it move | Observed above |
|---|---|---|
| `mtime` (Modify) | the **content** changes | moves on the added line, not on the `chmod` |
| `ctime` (Change) | the content **or** the metadata changes | moves on the addition **and** on the `chmod` |
| `atime` (Access) | the file is **read** | moves only on the `cat` |

It is `mtime` that `ls -l` prints, and therefore `mtime` that `ls -lt` sorts on.
Checked on the test machine: after a `chmod 775 catalogue`, `ls -ltr` leaves
`catalogue` in place with its 17:48 date, whereas `ls -ltr --time=ctime` moves it
to last with 17:50.

> **`atime` is not reliable for dating a read.** The root of the test machine is
> mounted with `relatime` (`findmnt -no OPTIONS /` answers `rw,relatime`), a mode
> where the kernel only writes `atime` if it is older than `mtime` or more than
> 24 hours old; with `noatime`, it never moves. The fourth date, `Birth`, is that
> of the creation of the inode: it only exists on the filesystems that store it.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `ls: cannot access 'x': No such file or directory` | typo or wrong directory | `pwd`, then complete with **Tab** |
| `bash: cd: x: Not a directory` | you gave a file to `cd` | `file x` or `ls -ld x` |
| `bash: cd: x: Permission denied` | traversal permission missing on the directory | `ls -ld x` |
| `ls: cannot open directory 'x': Permission denied` | read permission missing, while `ls -ld x` works | `ls -ld x` |
| `ls -l dir` does not print what you expected | it lists the content, not the directory | add `-d` |
| `tree: command not found` | `tree` is not installed | `find . -type d` |
| a file "missing" from `ls` | its name starts with a dot | `ls -a` |
| `ls -lt` ignores a recent `chmod` | `-t` sorts on `mtime`, not on `ctime` | `stat <file>` |
| the extension lies about the content | the name commits to nothing | `file <file>` |
| `ls` prints a single column | the output goes into a pipe or a file | normal behaviour |

To erase everything and start over, a single absolute path is enough:

```bash
cd ~
rm -rf /tmp/course-l1-navigate
```
