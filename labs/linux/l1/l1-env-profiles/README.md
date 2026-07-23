# Lab — environment variables & a sourced env file

## Reminder

[**Environment variables on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/)

`NAME=value` sets a shell variable; `export NAME` publishes it so child
processes inherit it. `source file` runs a file in the *current* shell (so its
`export`s stick), unlike executing it. Prepending to `PATH` makes a local
directory win over system tools.

## The course

The examples below work on `~/demo-env`, a demonstration directory, with a file
`parametres.sh` and the variables `APPLI`, `PAGER` and `BANNIERE`: the
challenge will ask you for a different file, different variables and different
values. The goal is to learn the method, not to copy a line.

All the output reproduced here comes from an AlmaLinux 10, connected as the
`ansible` user. Your own paths will differ.

### Reading a variable, listing the environment

The `$` asks the shell to replace the name with its value. Without it, you only
get the text:

```bash
echo $HOME
echo $USER
echo HOME
```

```text
/home/ansible
ansible
HOME
```

`env` lists the whole environment. As the output is long, you filter it:

```bash
env | grep "^PATH="
```

```text
PATH=/home/ansible/.local/bin:/home/ansible/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
```

### Shell variable, or environment variable

`export` is what makes the difference, and a child process is the only reliable
judge. Set the scene:

```bash
mkdir -p ~/demo-env/outils
cd ~/demo-env
```

Without `export`, the variable does not leave the current shell:

```bash
APPLI="facturation"
echo "  shell courant : [$APPLI]"
bash -c 'echo "  enfant        : [$APPLI]"'
```

```text
  shell courant : [facturation]
  enfant        : []
```

With `export`, the child sees it:

```bash
export APPLI="facturation"
bash -c 'echo "  enfant        : [$APPLI]"'
```

```text
  enfant        : [facturation]
```

Inheritance is not limited to a single level: a grandchild process sees it too,
since each child passes its environment on in turn.

```bash
bash -c 'bash -c '\''echo "  petit-fils voit APPLI = [$APPLI]"'\'''
```

```text
  petit-fils voit APPLI = [facturation]
```

This is also the difference shown by `env`, which displays **only** exported
variables:

```bash
LOCALE_SEULE="valeur"
env | grep -E "^(APPLI|LOCALE_SEULE)="
```

```text
APPLI=facturation
```

`LOCALE_SEULE` does exist in the current shell, though: `echo $LOCALE_SEULE`
displays it. It is simply absent from the environment.

> **No space around the `=`.** `APPLI = "facturation"` is not an assignment: the
> shell sees the command `APPLI` followed by two arguments. The machine answers
> `bash: line 3: APPLI: command not found`.

`unset` goes the other way and removes the variable:

```bash
export ESSAI="bonjour"; echo "  avant : [$ESSAI]"
unset ESSAI;            echo "  apres : [$ESSAI]"
```

```text
  avant : [bonjour]
  apres : []
```

### Reusing a variable inside another

A variable can be built from another one, provided you use **double** quotes.
Single quotes prevent any substitution:

```bash
export ESSAI_DOUBLE="Session $APPLI ouverte"
export ESSAI_SIMPLE='Session $APPLI ouverte'
echo "  doubles : [$ESSAI_DOUBLE]"
echo "  simples : [$ESSAI_SIMPLE]"
```

```text
  doubles : [Session facturation ouverte]
  simples : [Session $APPLI ouverte]
```

The substitution happens **at assignment time**, not at read time: changing
`APPLI` afterwards will not modify `ESSAI_DOUBLE`.

### PATH: the order decides which command runs

`PATH` is a list of directories separated by `:`. The shell walks them **in
order** and stops at the first one that contains the requested command. Let us
build a local tool:

```bash
cat > ~/demo-env/outils/inventaire <<'EOF'
#!/bin/bash
echo "inventaire : 42 machines"
EOF
chmod +x ~/demo-env/outils/inventaire
inventaire; echo "  code retour : $?"
```

As the directory is not in `PATH`, the command stays not found:

```text
bash: line 3: inventaire: command not found
  code retour : 127
```

Exit code `127` is the signature of "command not found": remember it, it tells
a `PATH` problem apart from a real failure of the program.

Put the directory at the front:

```bash
export PATH="$HOME/demo-env/outils:$PATH"
inventaire
which inventaire
```

```text
inventaire : 42 machines
/home/ansible/demo-env/outils/inventaire
```

Prepending and appending are not equivalent at all. With a tool that carries
the name of a system command, the position settles the matter:

```bash
cat > ~/demo-env/outils/sort <<'EOF'
#!/bin/bash
echo "ceci est le sort local, pas celui du systeme"
EOF
chmod +x ~/demo-env/outils/sort
PATH="$PATH:$HOME/demo-env/outils" bash -c 'which sort'
PATH="$HOME/demo-env/outils:$PATH" bash -c 'which sort'
```

```text
/usr/bin/sort
/home/ansible/demo-env/outils/sort
```

> **Always keep `$PATH` in the new value.** `export PATH="/some/path"` without
> `:$PATH` wipes out all the system directories: no external command is found
> in that terminal any more.

### Sourcing a file, or executing it

This is the heart of the matter. Let us write a settings file:

```bash
cat > ~/demo-env/parametres.sh <<'EOF'
export APPLI="facturation"
export PAGER="less"
export BANNIERE="Session $APPLI ouverte"
export PATH="$HOME/demo-env/outils:$PATH"
EOF
chmod +x ~/demo-env/parametres.sh
```

If you **execute** it, nothing survives:

```bash
./parametres.sh
echo "  APPLI apres execution : [$APPLI]"
echo "  BANNIERE             : [$BANNIERE]"
```

```text
  APPLI apres execution : []
  BANNIERE             : []
```

If you **source** it, everything stays:

```bash
source ./parametres.sh
echo "  APPLI apres source    : [$APPLI]"
echo "  BANNIERE             : [$BANNIERE]"
echo "  1re entree de PATH    : ${PATH%%:*}"
```

```text
  APPLI apres source    : [facturation]
  BANNIERE             : [Session facturation ouverte]
  1re entree de PATH    : /home/ansible/demo-env/outils
```

The reason comes down to a process number. An executed script runs in a **child
shell**, which disappears taking its variables with it; a sourced script is
read by the **current** shell. You prove it with `$$`, the PID of the shell:

```bash
cat > ~/demo-env/qui-suis-je.sh <<'EOF'
#!/bin/bash
echo "  le script tourne dans le PID $$"
EOF
chmod +x ~/demo-env/qui-suis-je.sh
echo "  le shell courant est le PID $$"
./qui-suis-je.sh
source ./qui-suis-je.sh
```

```text
  le shell courant est le PID 11735
  le script tourne dans le PID 11751
  le script tourne dans le PID 11735
```

Executed, the script has its own PID. Sourced, it carries the one of the
calling shell: no new process was created. The shorthand for `source` is the
dot: `. ./parametres.sh` does exactly the same thing.

One last consequence, useful for diagnosis: `chmod +x` only matters for
execution. A file meant to be sourced does not need to be executable.

```bash
printf 'export TEST_SOURCE=ok\n' > /tmp/sans-droit.sh
chmod 0644 /tmp/sans-droit.sh
source /tmp/sans-droit.sh; echo "  apres source : [$TEST_SOURCE]"
/tmp/sans-droit.sh; echo "  execution : code $?"
```

```text
  apres source : [ok]
bash: line 16: /tmp/sans-droit.sh: Permission denied
  execution : code 126
```

Remember the pair: `126` means "found but not executable", `127` means "not
found at all". Confusing them makes you hunt for a `PATH` problem where there
is only a missing `chmod`.

### Which file Bash reads, and when

The companion guide *Customising your shell* gives a three-line table:
`~/.bash_profile` at login, `~/.bashrc` for every interactive terminal,
`~/.profile` as a replacement for the first. That table is broadly right, but
it does not explain the cases that waste the most time. Two questions decide,
and they are independent:

- is the shell a **login shell** (opened by a connection)?
- is the shell **interactive** (a human typing into it)?

Do not guess: ask the shell itself. `shopt -q login_shell` answers the first,
the presence of an `i` in `$-` answers the second.

```bash
echo "\$- = [$-]   login_shell = $(shopt -q login_shell && echo on || echo off)"
```

Here is what five different situations answer, measured on the machine:

| Situation | `$-` | login | interactive |
|---|---|---|---|
| `ssh host` session then typing at the keyboard | `himBHs` | on | yes |
| `ssh host 'command'` | `hBc` | off | no |
| `bash -lc 'command'` | `hBc` | on | no |
| `bash -c 'command'` | `hBc` | off | no |
| `bash -ic 'command'` | `hiBHc` | off | yes |

One detail confirms the first case: in a session opened by `ssh`, `echo $0`
displays `-bash`, with a leading dash. That dash is placed by the program
opening the connection, not by the `-l` option: `bash -lc 'echo $0'` answers
`bash` without a dash even though it is a login shell. The dash therefore gives
away a real connection, whereas `shopt -q login_shell` answers the question in
Bash's own terms. When the two diverge, `shopt` is the one that describes the
behaviour observed above.

To find out **which files** are really read, the method that does not lie
consists in dropping an `echo` line at the top of each, then observing. On this
AlmaLinux 10, the five situations give:

| Situation | Files read, in order |
|---|---|
| Interactive `ssh host` session | `/etc/profile` (and `/etc/profile.d/*.sh`), `~/.bash_profile`, `~/.bashrc` |
| `ssh host 'command'` | `~/.bashrc` **alone** |
| `bash -lc 'command'` | `/etc/profile` (and `/etc/profile.d/*.sh`), `~/.bash_profile`, `~/.bashrc` |
| `bash -c 'command'` | none |
| `bash -ic 'command'` | `~/.bashrc`, then `/etc/profile.d/*.sh` via `/etc/bashrc` |

Three things to remember from this table, and none of them is intuitive.

**A `~/.bashrc` is not read because the session is interactive.** The second
line shows it: `ssh host 'command'` is neither a login shell nor an interactive
shell, and yet `~/.bashrc` is read, it and it alone. That is the case for every
remote command, therefore for automation.

**`~/.bashrc` is never read directly by a login shell.** It is read because
`~/.bash_profile` sources it explicitly. On this machine, the file shipped by
the distribution starts with:

```bash
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
```

Remove those four lines and `~/.bashrc` stops existing for connections, with no
message to point it out. The diverted `HOME` of the next section lets you check
it in two commands: with the `if` block, the connection displays both files;
without it, it only displays `~/.bash_profile`.

**`/etc/profile.d/*.sh` is read in far more cases than it seems, but
silently.** An `echo` dropped into `/etc/profile.d/` does not show up for a
`bash -lc`, even though the script is indeed executed. The reason is in
`/etc/profile`:

```bash
for i in /etc/profile.d/*.sh /etc/profile.d/sh.local ; do
    if [ -r "$i" ]; then
        if [ "${-#*i}" != "$-" ]; then
            . "$i"
        else
            . "$i" >/dev/null
        fi
```

The test `"${-#*i}" != "$-"` asks whether `$-` contains an `i`, that is,
whether the shell is interactive. Otherwise the script's output goes to the
bin. To settle the question, do not use an `echo` but a variable, which
survives the redirection:

```bash
echo 'TRACE_PROFILED=1' | sudo tee /etc/profile.d/00-trace.sh
bash -lc 'echo "TRACE_PROFILED=[$TRACE_PROFILED]"' </dev/null
bash -c  'echo "TRACE_PROFILED=[$TRACE_PROFILED]"' </dev/null
```

```text
TRACE_PROFILED=[1]
TRACE_PROFILED=[]
```

As for the fifth line of the table, it comes as a surprise: a `bash -ic` is not
a login shell, and it still reads `/etc/profile.d/`. It is `/etc/bashrc`,
sourced by `~/.bashrc`, that takes care of it, with the comment that explains
it:

```bash
  if ! shopt -q login_shell ; then # We're not a login shell
    ...
    for i in /etc/profile.d/*.sh; do
```

In other words, on this family of distributions, `/etc/profile.d/` ends up
being read whatever the path taken, as long as the shell is either a login
shell or interactive.

### The first of the three wins

For a login shell, Bash looks for `~/.bash_profile`, then `~/.bash_login`, then
`~/.profile`, and stops **at the first one found**. The following ones are
never read. You can check it safely by diverting `HOME` to a throwaway
directory:

```bash
mkdir -p /tmp/bacasable
for f in .bash_profile .bash_login .profile; do
  printf 'echo "  lu : ~/%s"\n' "$f" > /tmp/bacasable/$f
done
HOME=/tmp/bacasable bash -lc true </dev/null
rm /tmp/bacasable/.bash_profile
HOME=/tmp/bacasable bash -lc true </dev/null
rm /tmp/bacasable/.bash_login
HOME=/tmp/bacasable bash -lc true </dev/null
```

```text
  lu : ~/.bash_profile
  lu : ~/.bash_login
  lu : ~/.profile
```

This diverted `HOME` trick is the best way to experiment on profile files: you
never touch your own.

It also explains a great classic. The file actually used depends on the ones
the distribution shipped in your `$HOME`, not on a carved-in-stone rule: on the
demonstration machine, `~/.bash_profile` is present and `~/.profile` absent, so
the first one is the one that serves. Elsewhere, it may be the other way round.
Do not assume it, observe it:

```bash
ls -la ~/.bash_profile ~/.bash_login ~/.profile
```

Writing into a file Bash never reaches produces no error: simply nothing
happens, which takes far longer to diagnose.

### Where to put a permanent `export`

The question is not one of style: it decides who will see the variable. Let us
put an `export` in each of the two files:

```bash
echo 'export DEMO_DEPUIS_BASHRC=oui'  >> ~/.bashrc
echo 'export DEMO_DEPUIS_PROFILE=oui' >> ~/.bash_profile
```

From a remote command, that is, without login and without interaction:

```text
  DEMO_DEPUIS_BASHRC  = [oui]
  DEMO_DEPUIS_PROFILE = []
```

From an interactive session opened at the keyboard:

```text
  DEMO_DEPUIS_BASHRC  = [oui]
  DEMO_DEPUIS_PROFILE = [oui]
```

A variable placed in `~/.bash_profile` alone is therefore **invisible to
commands launched remotely**, while it shows up as soon as you log in for real.
This is the most frequent cause of a script that works at the keyboard and
fails in a `cron` job or in an automation tool. On this machine, `~/.bashrc` is
the only location seen in both cases.

### Not locking yourself out

A broken profile file is expensive, because it is re-read on every connection.
Two kinds of damage, very different.

A **syntax error** is noisy but benign. The shell reports the line, gives up on
the rest of the file, and carries on:

```bash
printf 'echo "ligne 1"\nexport X="guillemet non ferme\necho "ligne 3"\n' > /tmp/bacasable/.bash_profile
HOME=/tmp/bacasable bash -lc "echo CORPS-DE-LA-COMMANDE" </dev/null
echo "  code retour : $?"
```

```text
ligne 1
/tmp/bacasable/.bash_profile: line 3: unexpected EOF while looking for matching `"'
CORPS-DE-LA-COMMANDE
  code retour : 0
```

`ligne 1` is displayed, `ligne 3` is not: everything after the error is lost.
But the requested command does run.

A stray `exit`, on the other hand, is silent and total. The body of the command
is never executed, and the exit code stays `0`:

```bash
printf 'echo "debut du fichier"\nexit\necho "apres exit"\n' > /tmp/bacasable/.bash_profile
HOME=/tmp/bacasable bash -lc "echo CORPS-DE-LA-COMMANDE" </dev/null
echo "  code retour : $?"
```

```text
debut du fichier
  code retour : 0
```

`CORPS-DE-LA-COMMANDE` appears nowhere. The same `exit` added to a real
`~/.bashrc` makes the machine mute to every remote command: `ssh` connects,
runs nothing, and hands back control with an apparent success. Even `scp` and
`sftp` fall over, with a message that points at the real culprit:

```text
Received message too long 1296126545
Ensure the remote shell produces no output for non-interactive sessions.
```

That message says two things: a profile file must never display anything in a
non-interactive session, and this is also why a simple welcome `echo` in
`~/.bashrc` breaks file transfers.

Four reflexes are enough to work without risk:

```bash
cp -a ~/.bashrc ~/.bashrc.bak          # 1. back up before writing
bash -n ~/.bashrc                      # 2. check the syntax without executing
HOME=/tmp/bacasable bash -lc true      # 3. try it in a throwaway HOME
bash -l                                # 4. try it for real, in a subshell
```

`bash -n` reads the file and reports syntax errors without executing a single
line of it. On a damaged file:

```text
/home/ansible/.bashrc: line 28: unexpected EOF while looking for matching `"'
```

The fourth reflex is the most important: `bash -l` opens a login shell **from
the session already open**. If the result is catastrophic, you type `exit` and
you are back in a healthy session, from which you restore the backup. Never
close your last connection before checking that a new one opens.

And if the worst happens anyway, the emergency exit is a **second account** on
the machine: its own profile files are intact, and if it belongs to `wheel` it
repairs those of the first.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `bash: command: command not found`, exit code `127` | the directory of the command is not in `PATH` |
| The child program does not see the variable | `export` forgotten: `NAME=value` stays local to the shell |
| `NAME = value` answers `command not found` | spaces around the `=` |
| The variable disappears after running the file | the file was executed instead of being sourced |
| The variable is there at the keyboard, absent in a remote command | the `export` is in `~/.bash_profile`, which remote commands do not read |
| Nothing changes even though `~/.profile` was modified | `~/.bash_profile` exists and wins: the following ones are not read |
| An `echo` placed in `/etc/profile.d/` does not show up | `/etc/profile` throws their output away when the shell is not interactive; probe with a variable, not with an `echo` |
| The wrong binary is the one that runs | the expected directory is at the end of `PATH` instead of the front |
| No command works in the terminal any more | `$PATH` was overwritten without being re-injected at the end |
| `ssh` connects, does nothing, and returns `0` | a stray `exit` sits in a profile file |
| `scp`/`sftp`: `Received message too long` | a profile file displays something in a non-interactive session |

To undo everything and start over:

```bash
rm -rf ~/demo-env /tmp/bacasable
sudo rm -f /etc/profile.d/00-trace.sh
cp -a ~/.bashrc.bak ~/.bashrc          # if you had modified ~/.bashrc
exec bash -l                           # reload a clean shell
```
