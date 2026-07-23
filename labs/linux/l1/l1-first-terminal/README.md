# Lab — first steps in the terminal

## Reminder

[**Opening a terminal and understanding the prompt**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/prompt-terminal/)

Before you have typed a single letter, the terminal already shows a line: the
**prompt**. The guide explains how to read it: it says who you are, on which
machine and in which directory you are, and its last character announces whether
you are working as an ordinary user (`$`) or as the administrator (`#`). It also
recalls three words that are readily confused: the **terminal** is the window
that displays text, the **shell** is the program that interprets what you type,
the **session** is the active connection, from login to logout. This lab adds
what reading alone does not tell: where that line comes from (the `PS1`
variable), how to know which shell is really running, and which typing habits
save time from the first hour.

The structure of a command and how to query the documentation are covered in the
neighbouring labs `l1-read-a-command` and `l1-get-help`: none of that is repeated
here.

## The course

The examples below are not about the challenge: they work in
`/tmp/cours-l1-terminal`, a setup you build and will throw away at the end. The
point is to learn to read your screen and to use your keyboard, not to copy an
answer.

Every output reproduced here was recorded on **Ubuntu 24.04.2 LTS** with
`GNU bash, version 5.2.21(1)-release`, **without a single `sudo`**. The session
used for the captures runs under **zsh**, not bash: every time a bash behaviour
is shown, bash was started explicitly, with `bash -c '...'` for a single command
and `script -qec "bash --norc -i"` when a real interactive terminal was needed.

### The prompt, piece by piece

Build the setup, then open a bash **with no configuration** thanks to `--norc`:

```bash
mkdir -p /tmp/cours-l1-terminal/atelier/notes/2026
cd /tmp/cours-l1-terminal
bash --norc -i
```

The prompt immediately becomes `bash-5.2$`: this is the **default bash prompt**,
compiled into the program and used when no configuration file is read. Neither
your name, nor the machine, nor the directory: all of that comes from the
distribution, not from bash. You will leave this shell with `exit`. The usual
prompt of a distribution rather looks like this (the guide's example):

```text
student@serveur:~$
```

| Element | Meaning |
|---|---|
| `student` | name of the logged-in user |
| `@` and `:` | separators |
| `serveur` | machine name |
| `~` | current directory (`~` is the shortcut for the home directory) |
| `$` | you are an ordinary user (`#` if you are root) |

On the capture machine, after the `cd` of the setup, the real prompt was
`student@poste:/tmp/cours-l1-terminal$`. The directory is no longer `~` but the
path of the setup: that part **follows your moves**, recomputed before each
display. This is the first reason to read it.

### `$` or `#`: the distinction that costs dearly

The guide is categorical: if the prompt ends with `#`, you are **root**, the
administrator, and a mistake can break the system. Stay an ordinary user unless
you explicitly need otherwise.

That character is not chosen at random in the configuration: bash decides it
itself according to the effective identity of the process. The sequence that
produces it is `\$`; on an ordinary account it gives `$`, with an effective
identifier equal to 0 it gives `#`. The two cases side by side (`${PS1@P}` asks
bash to expand a prompt as it would on screen, which avoids opening a real
session):

```bash
bash -c 'PS1='\''\u@\h:\w\$ '\''; echo "[${PS1@P}]"'
fakeroot -- bash -c 'PS1='\''\u@\h:\w\$ '\''; echo "[${PS1@P}]"'
```

```text
[student@poste:/tmp/cours-l1-terminal$ ]
[root@poste:/tmp/cours-l1-terminal# ]
```

> `fakeroot` is **not** a way of becoming the administrator: it only makes
> programs believe they run as root, without giving them the rights. Here it
> only serves to show the `#`. On a real administration session (`sudo -i`),
> that `#` appears for real.

The habit to build: **before validating a destructive command, look at the last
character of your prompt.**

### `PS1`: the recipe behind the display

Everything above lives in one variable, `PS1`, and `echo "$PS1"` reveals the
recipe. In the configuration-less bash started earlier, it answers `\s-\v\$ `,
which explains the `bash-5.2$` observed: `\s` is the shell name, `\v` its
version, `\$` the final character. In a bash that reads the distribution
configuration (`bash -i`), the same command gives something else:

```text
${debian_chroot:+($debian_chroot)}\u@\h:\w\$
```

You find in it exactly the prompt `student@poste:/tmp/cours-l1-terminal$`. That
recipe did not fall from the sky: on this Ubuntu machine, it is written plainly
in the template configuration file for new accounts.

```bash
grep -n 'PS1=' /etc/skel/.bashrc
```

```text
60:    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
62:    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
[...]
```

Two versions, chosen depending on whether the terminal can display colours or
not: line 62 is the plain version, line 60 the same one with colour codes
(`\[\033[01;32m\]` and friends) inserted.

| Sequence | What it displays |
|---|---|
| `\u` | user name |
| `\h` | machine name |
| `\w` | current directory, full path (`~` for the home directory) |
| `\W` | current directory, **last element only** |
| `\$` | `#` if the effective identifier is 0, `$` otherwise |
| `\s` `\v` | name and version of the shell |

The difference between `\w` and `\W` shows in two lines, from
`/tmp/cours-l1-terminal/atelier/notes/2026`:

```bash
bash -c 'PS1='\''\u@\h:\w\$ '\''; echo "${PS1@P}"'
bash -c 'PS1='\''\u@\h:\W\$ '\''; echo "${PS1@P}"'
```

```text
student@poste:/tmp/cours-l1-terminal/atelier/notes/2026$
student@poste:2026$
```

`\W` fits in a corner of the screen but does not say where you are: two `2026`
directories located in two different trees look identical.

### Terminal, shell, console: three distinct things

The most stubborn confusion of the beginner clears up with two commands that
**do not answer the same thing**. Run first in the capture session, then inside
a bash:

```bash
echo "$SHELL" ; ps -p $$ -o comm=
bash -c 'echo "$SHELL" ; ps -p $$ -o comm='
```

```text
/usr/bin/zsh
zsh
/usr/bin/zsh
bash
```

`$SHELL` did not move, and that is normal: this variable contains the shell
**declared for your account** in the user database, not the one that is running.
That field is read directly, it is the seventh of the line:
`getent passwd "$(id -u)" | cut -d: -f7` answers `/usr/bin/zsh` here, the same
value as `$SHELL`.

`ps -p $$ -o comm=`, on the other hand, queries the current process: `$$` is the
number of the running shell and `comm` its name. This is **the** reliable answer
to the question "which shell am I in?". The two diverge as soon as a shell
starts another one, which happens all the time.

The terminal is **another process**, the parent of the shell:

```bash
ps -o pid,tty,comm --forest -p $PPID --ppid $PPID
```

```text
    PID TT       COMMAND
1768434 ?        script
1768437 pts/9     \_ bash
```

The window (here `script`, the program that provided the terminal for the
capture; on a desktop it would be `gnome-terminal` or `konsole`) and the shell
it hosts are indeed two separate processes. Close the window, the shell dies;
type `exit` in the shell, the window closes. They remain distinct.

The link between the two carries a file name, which `tty` displays:
`/dev/pts/9`. `pts` means *pseudo-terminal*, a terminal emulated by a program.
The **console** is the physical terminal of the machine, the one you see on the
screen plugged into the server before any graphical desktop even starts; it
exists independently of any window and carries another name, which
`ls -l /dev/tty1` shows to be present:
`crw--w---- 1 root tty 4, 1 juil. 14 07:50 /dev/tty1`.

That leaves the `TERM` variable, which says **which terminal model** it is. It
is used by programs that draw on the screen (colours, cursor position) to know
what they are allowed to send:

```bash
echo "$TERM" ; tput colors
```

```text
xterm-256color
256
```

> The capture session having no `TERM`, the value was set explicitly on the
> command line for this demonstration. In a real terminal, the terminal itself
> fills it in. A missing or incorrect `TERM` gives a display with no colour, or
> even stray characters.

### The habits that save time

**The Tab key completes.** Type the beginning of a command or a path then Tab:
the shell finishes the word if there is only one possibility. If there are
several, a **second** press of Tab lists them all. The `compgen` command shows
what Tab would suggest, without having to press it:

```bash
compgen -f /etc/os-
compgen -c sys | sort -u | head -5
```

```text
/etc/os-release
syscount-bpfcc
syscount.bt
sysctl
syslinux
systemctl
```

A single candidate for `/etc/os-`, so Tab completes directly; several for `sys`,
so Tab-Tab shows the list. Always complete: it is faster, and a typo in a path
becomes impossible.

**History saves retyping.** The shell keeps what you typed. The Up arrow goes
back command by command, `history` shows the numbered list and `!<number>`
replays a line:

```text
bash-5.2$ history
    1  cd /tmp/cours-l1-terminal
    2  ls atelier
    3  pwd
    4  history
bash-5.2$ !2
ls atelier
notes
```

`!2` **redisplays** the command before running it: you see what you are
relaunching. To find a line without knowing its number, **Ctrl+R** opens a
search in the history; type a few letters, the most recent match appears, Enter
runs it. After typing `atel`, the line displayed was:

```text
(reverse-i-search)`atel': ls atelier/notes
```

**The editing shortcuts save the Left arrow.** They fall into two families, and
the distinction is useful: some are handled by the **terminal** itself (they
work even when no shell is listening), the others by the bash editing library.

| Shortcut | Effect | Handled by |
|---|---|---|
| **Ctrl+A** | go to the beginning of the line | bash |
| **Ctrl+E** | go to the end of the line | bash |
| **Ctrl+U** | erase from the cursor back to the beginning | terminal and bash |
| **Ctrl+W** | erase the word before the cursor | terminal and bash |
| **Ctrl+L** | clear the screen | bash |
| **Ctrl+R** | search the history | bash |
| **Ctrl+C** | interrupt the running command | terminal |
| **Ctrl+D** | end of input; on an empty line, closes the shell | terminal |

This table is not an opinion. On the bash side, `bind -P` lists the bindings
actually in place; here are the lines that concern us:

```text
beginning-of-line can be found on "\C-a", "\eOH", "\e[1~", "\e[H".
clear-screen can be found on "\C-l".
complete can be found on "\C-i", "\e\e\000".
end-of-line can be found on "\C-e", "\eOF", "\e[4~", "\e[F".
possible-completions can be found on "\e=", "\e?".
reverse-search-history can be found on "\C-r".
unix-line-discard can be found on "\C-u".
unix-word-rubout can be found on "\C-w".
```

`\C-a` reads "Ctrl+A", and `\C-i` is the code of the Tab key: completion is
therefore a shortcut like the others. On the terminal side, `stty -a` shows the
control characters intercepted before the shell even sees them:

```text
intr = ^C; quit = ^\; erase = ^?; kill = ^U; eof = ^D; eol = <undef>;
[...]
werase = ^W; lnext = ^V; discard = ^O; min = 1; time = 0;
```

`intr = ^C` means the terminal turns that character into an interrupt signal:
this is why **Ctrl+C** works even on a program that knows nothing about bash.
Check it, with a command that lasts:

```text
bash-5.2$ sleep 30
^C
bash-5.2$ echo "code retour = $?"
code retour = 130
```

The `130` is the signature of a command killed by Ctrl+C. Finally, **Ctrl+D** on
an **empty** line closes the session: it is the keyboard equivalent of `exit`.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| the prompt shows `#` | you are root, or in a `sudo -i` | `id -u`; if it answers `0`, leave with `exit` |
| the prompt is reduced to `bash-5.2$` | the shell does not read the account configuration | restart without `--norc`, or check `~/.bashrc` |
| `echo "$SHELL"` does not match the shell in use | `$SHELL` gives the declared shell, not the running one | `ps -p $$ -o comm=` |
| Tab completes nothing | no candidate, or completion not installed | `compgen -c <beginning>` to see the candidates |
| `\$` in `PS1` always shows `$` | `PS1` was defined between **double** quotes, where `\$` becomes a literal `$` | redefine `PS1` between **single** quotes |
| display with no colour, or stray characters | `TERM` missing or incorrect | `echo "$TERM"` then `tput colors` |
| the Ctrl+something shortcuts do not respond | you are not in an interactive shell input | `tty` must answer a `/dev/pts/...` |
| Ctrl+D does not close the shell | the `IGNOREEOF` variable is set | use `exit` |

To finish, leave the disposable bash and erase the setup:

```bash
exit
rm -rf /tmp/cours-l1-terminal
```
