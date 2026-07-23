# Lab — get help from the command line

## Reminder

[**Getting help under Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/obtenir-aide/)

Nobody remembers every option of every command, and that is not the expected
skill: a Linux system carries its own documentation, and what is asked of you is
to know which one to query. `<command> --help` gives a quick reminder, `man` is
the reference, `info` hosts the detailed GNU manuals, `apropos` and `whatis`
find a name back when you do not know it. The manual itself is split into
**numbered sections**: the same name can appear several times there without
designating the same thing.

## The course

The examples below deal with `passwd`, `printf`, `ls`, `cp` and `echo`: the
challenge will ask you for other commands, which you will precisely have to find
with the tools presented here. The point is to learn how to query the
documentation of a system, not to copy a line.

Every output reproduced here was taken on **Debian 12 (bookworm)**, with
`man 2.11.2`, `GNU bash 5.2.15` and `info (GNU texinfo) 6.8`. The two readings
made elsewhere are flagged as such.

First reflex before anything else: check what you have, because on a minimal
installation these tools are missing. Taken on a minimal **AlmaLinux 10** image,
`command -v man info apropos` prints no line and exits with return code 1: the
three commands are missing, and the guide gives the packages to install
depending on the distribution.

### Three sources, and they do not say the same thing

Take `ls`, and compare what each of the three sources produces:

| Source | Command | Measured volume |
|---|---|---|
| Help built into the binary | `ls --help` | 138 lines |
| Manual page | `man ls` | 252 lines |
| GNU manual | `info '(coreutils) ls invocation'` | 832 lines |

This is not the same text inflated three times: the man page itself points to
`info` in its `SEE ALSO`, through the line
`or available locally via: info '(coreutils) ls invocation'`. The `info` manual
contains whole chapters the man page does not have (`Sorting the output`,
`Formatting file timestamps`, the `LS_COLORS` variable). For GNU tools
(coreutils, `find`, `sed`, `awk`), that is where the most complete text is.

The case where `--help` and `man` really diverge is nastier. In bash, `echo`
exists **twice**: a command built into the shell, and a `/usr/bin/echo` program.
The shell always gives priority to its own.

```bash
echo --help
type -a echo
```

```text
--help
echo is a shell builtin
echo is /usr/bin/echo
echo is /bin/echo
```

`echo --help` does not print any help: it **prints the text `--help`**, because
the built-in version does not know that option and treats it as a string to
print. The program does understand it (`/usr/bin/echo --help` answers
`Usage: /usr/bin/echo [SHORT-OPTION]... [STRING]...`), and it is indeed that
program, the one you are not running, that `man echo` documents.

> **The lesson.** Before believing a manual page, check that this is really the
> program the shell runs. That is the job of `type`, in the last section.

### The manual is split into numbered sections

This is the point almost nobody knows, and the one that separates someone who
searches from someone who finds. `man 1 man` gives the list:

```text
1   Executable programs or shell commands
2   System calls (functions provided by the kernel)
3   Library calls (functions within program libraries)
4   Special files (usually found in /dev)
5   File formats and conventions, e.g. /etc/passwd
[...]
8   System administration commands (usually only for root)
9   Kernel routines [Non standard]
```

The number goes **before** the name. See what it changes on `passwd`:

```bash
man 1 passwd
man 5 passwd
```

```text
PASSWD(1)                      User Commands                     PASSWD(1)

NAME
       passwd - change user password

SYNOPSIS
       passwd [options] [LOGIN]
[...]
PASSWD(5)             File Formats and Configuration             PASSWD(5)

NAME
       passwd - the password file

DESCRIPTION
       /etc/passwd contains one line for each user account, with seven
       fields delimited by colons (":"). These fields are:
[...]
```

Two unrelated pieces of documentation: the **command** that changes a password
on one side, the **format of the file** `/etc/passwd` on the other. Same thing
for `printf`, a utility in section 1 and a C language function in section 3:

```bash
man 3 printf
```

```text
printf(3)                Library Functions Manual                printf(3)

NAME
       printf, fprintf, dprintf, sprintf, snprintf, vprintf, vfprintf, vd-
       printf, vsprintf, vsnprintf - formatted output conversion
[...]
```

With no number, `man` opens the **first section found**, in number order:
`man printf` therefore gives you section 1, and you will never know that section
3 exists unless you ask for it.

### Knowing that a name exists in several sections

`whatis` (identical to `man -f`) lists every section where a name appears, with
its one-line description:

```bash
whatis printf
man -f man
```

```text
printf (1)           - format and print data
printf (3)           - formatted output conversion
man (1)              - an interface to the system reference manuals
man (7)              - macros to format man pages
```

This is the reflex to acquire before opening a page: in one line, you know how
many different pieces of documentation carry that name. `man -a printf` then
chains through all of them, offering to move on to the next at the end of each.

To know where those pages come from, `man -w` prints the path of the file
instead of its content, and `-aw` prints them all: `man -aw passwd` answers
`/usr/share/man/man1/passwd.1.gz` then `/usr/share/man/man5/passwd.5.gz`.

### Searching when you do not know the name

`apropos` (identical to `man -k`) searches your pattern in the one-line
descriptions of **all** the installed pages. The `-s` option restricts it to a
section, which avoids drowning a search for a configuration file under the
commands:

```bash
apropos "copy files"
apropos -s 5 password
```

```text
cp (1)               - copy files and directories
install (1)          - copy files and set attributes
login.defs (5)       - shadow password suite configuration
passwd (5)           - the password file
shadow (5)           - shadowed password file
```

Beware: `apropos` compares your pattern with the **exact text** of the
description. It does not understand synonyms, and a natural wording often fails:

```bash
apropos "disk usage"
echo "code retour = $?"
apropos "space usage"
```

```text
disk usage: nothing appropriate.
code retour = 16
df (1)               - report file system space usage
du (1)               - estimate file space usage
```

Both commands do exist, but their description says `space usage`, not
`disk usage`. The remedy is `-a`, which accepts several keywords in any order:
`apropos -a file space usage` does find `df` and `du` back.

**The next trap is more serious.** `apropos` and `whatis` do not read the pages:
they query an **index database** built by `mandb`. If that index is missing or
out of date, they answer `nothing appropriate` while the page exists.
Demonstration, with the index set aside:

```bash
apropos "copy files"
echo "code retour = $?"
man cp
```

```text
copy files: nothing appropriate.
code retour = 16
CP(1)                          User Commands                         CP(1)

NAME
       cp - copy files and directories
```

`apropos` fails, `man cp` succeeds and prints that description word for word:
the page is there, it is the index that is missing. `mandb`, run as root,
rebuilds it (`3314 manual pages were added.`), after which
`apropos "copy files"` finds `cp` and `install` back with return code 0.

The same message shows up for the opposite reason, and that is the case of the
workstation on which this lab was prepared, a **stripped-down Ubuntu 24.04**
where `man-db` is installed but where almost every page has been deleted. The
index there is perfectly up to date, it simply only indexes the little that is
left:

```text
$ whatis psql
psql (1)             - PostgreSQL interactive terminal
$ whatis ls
ls: nothing appropriate.
```

Two causes, a single message. `man -w <name>` settles it: if it returns no path,
the page really is missing.

### Reading a man page without reading all of it

`man` drops you into the `less` pager: **Space** moves forward one page, **b**
goes back, **/pattern** searches forward, **n** and **N** jump to the next and
previous occurrence, **q** quits.

Pages always follow the same plan, and that is what lets you jump to the right
place: **NAME** (is this the right command), **SYNOPSIS** (the syntax, with
brackets for what is optional), **DESCRIPTION**, **OPTIONS** (the complete
list), **EXAMPLES**, **FILES**, **SEE ALSO** (the neighbouring commands),
**EXIT STATUS** (the return codes). In a long page, type `/EXAMPLES` then Enter
to get there in one go.

### `which`, `type`, `command -v`: three different questions

`which` looks for a **file** in the `PATH`. `type` queries the **shell**, and
therefore also knows aliases, functions and built-in commands. On `cd`, built
into bash and with no file, the two diverge sharply:

```bash
type cd
which cd
echo "code retour = $?"
command -v cd
```

```text
cd is a shell builtin
code retour = 1
cd
```

`which` returns nothing and exits with an error, while the command exists and
works. Worse, it can return a path that is not what actually runs:

```bash
which pwd
type -a pwd
```

```text
/usr/bin/pwd
pwd is a shell builtin
pwd is /usr/bin/pwd
pwd is /bin/pwd
```

`type -a` lists every possibility **in priority order**: it is the first one,
the built-in version, that will be run, whereas `which` designates the second.
Aliases and functions escape `which` in the same way:

```bash
alias ll='ls -l --human-readable'
type ll
which ll
echo "code retour = $?"
```

```text
ll is aliased to `ls -l --human-readable'
code retour = 1
```

`type -t` answers in a single word, which is handy in a script: `alias`,
`function`, `builtin`, `file`, or nothing at all.

That leaves the case of built-in commands: `man cd` fails with
`No manual entry for cd` (return code 16), because they are not documented by
separate pages but by the shell itself, through `help`:

```bash
help cd
```

```text
cd: cd [-L|[-P [-e]] [-@]] [dir]
    Change the shell working directory.

    Change the current directory to DIR.  The default DIR is the value of the
    HOME shell variable. If DIR is "-", it is converted to $OLDPWD.
[...]
```

`help -d cd` gives the one-line version of it, `help` alone lists every built-in
command. They also appear in `man bash`, section `SHELL BUILTIN COMMANDS`, but
that is a page several thousand lines long.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `No manual entry for xxx` on a command that works | command built into the shell | `type xxx`, then `help xxx` |
| `No manual entry for xxx` on a real program | page not installed | `man -w xxx`, then install the doc package |
| `nothing appropriate` but `man` works | `mandb` index missing or out of date | rebuild the index with `mandb` |
| `nothing appropriate` and `man -w` returns nothing | the pages themselves are missing | install `man-pages` / `manpages` |
| `apropos: command not found` | `man-db` not installed | see the packages at the top of the guide |
| `man` shows the wrong documentation | wrong section picked | `whatis name`, then `man <number> name` |
| `<command> --help` prints `--help` | built-in command that ignores the option | `help command` |
| the man page does not match what runs | another binary is being run | `type -a command` |
