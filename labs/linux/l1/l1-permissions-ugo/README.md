# Lab — file permissions with chmod

## Reminder

[**Change permissions on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/)

Every file carries three permission triads (owner, group, other) with read (4),
write (2), execute (1). `chmod` sets them in octal (`chmod 664 file`) or
symbolically (`chmod u+x,o-r file`). A directory needs the `x` bit to be
traversed. Least privilege: grant exactly what the file needs, no more.

## The course

The examples below work on `/srv/atelier-droits`, with the users `theo` and
`nadia` and the group `redaction`: the challenge will ask you for other files
and other values. The point is to learn the method, not to copy a line. Every
output reproduced here comes from an AlmaLinux 10 with SELinux in `Enforcing`.

One clarification before you start. The challenge deals with files you already
own: `chmod` is enough, `sudo` is useless. The course, on the other hand, needs
a second account to **prove** permissions instead of reading them, so it needs a
machine where you are administrator.

### The demonstration setup

```bash
sudo useradd -m theo
sudo useradd -m nadia
sudo groupadd redaction
sudo usermod -aG redaction theo
sudo mkdir -p /srv/atelier-droits
sudo chown theo:redaction /srv/atelier-droits
sudo chmod 0775 /srv/atelier-droits
sudo -u theo sh -c 'umask 002
  echo "brouillon de l article" > /srv/atelier-droits/rapport.txt
  printf "#!/usr/bin/env bash\necho inventaire\n" > /srv/atelier-droits/inventaire.sh
  mkdir /srv/atelier-droits/archives'
```

`theo` is a member of `redaction`, `nadia` is not yet: that is what will let you
test the three permission levels on the same files.

Convention for everything that follows: a command **without a prefix** is run by
`theo`, the owner of the files (in practice `sudo -u theo …`); `sudo -u nadia …`
tests third-party access; `sudo …` alone acts as root.

```bash
id theo
id nadia
```

```text
uid=1002(theo) gid=1002(theo) groups=1002(theo),1004(redaction)
uid=1003(nadia) gid=1003(nadia) groups=1003(nadia)
```

### Read the permissions before changing them

```bash
ls -l /srv/atelier-droits
```

```text
total 8
drwxrwxr-x. 2 theo theo  6 Jul 22 14:02 archives
-rw-rw-r--. 1 theo theo 36 Jul 22 14:02 inventaire.sh
-rw-rw-r--. 1 theo theo 23 Jul 22 14:02 rapport.txt
```

The first character gives the type (`-` file, `d` directory), the next nine the
three triads `u`, `g`, `o`. Note the **trailing dot** after the nine
characters: it shows up on this machine and does not exist in the guide's
examples. It is not a tenth permission, and `stat` does not see it.

`ls -l` is made for humans; to check an exact value, ask for the octal
directly:

```bash
stat -c '%A %a %U %G %n' /srv/atelier-droits /srv/atelier-droits/rapport.txt /srv/atelier-droits/archives
```

```text
drwxrwxr-x 775 theo redaction /srv/atelier-droits
-rw-rw-r-- 664 theo theo /srv/atelier-droits/rapport.txt
drwxrwxr-x 775 theo theo /srv/atelier-droits/archives
```

This is the reflex command: `%A` gives the `rwx` form, `%a` the octal, and both
read at a glance. Careful, `%a` strips leading zeros: a file with no permission
at all shows up as `0`, not `000`.

### Symbolic notation: who, which action, what

The guide sums up the three parts of a symbolic expression.

| Who | Meaning |
|-----|---------------|
| `u` | User (owner) |
| `g` | Group |
| `o` | Others |
| `a` | All (everyone) |

| Action | Meaning |
|--------|---------------|
| `+` | Add a permission |
| `-` | Remove a permission |
| `=` | Set exactly these permissions |

On the setup above, each command and its real result:

```bash
chmod u+x /srv/atelier-droits/inventaire.sh
stat -c '%A %a %n' /srv/atelier-droits/inventaire.sh
```

```text
-rwxrw-r-- 764 /srv/atelier-droits/inventaire.sh
```

```bash
chmod go-w /srv/atelier-droits/inventaire.sh
stat -c '%A %a %n' /srv/atelier-droits/inventaire.sh
```

```text
-rwxr--r-- 744 /srv/atelier-droits/inventaire.sh
```

```bash
chmod a=r /srv/atelier-droits/rapport.txt
stat -c '%A %a %n' /srv/atelier-droits/rapport.txt
```

```text
-r--r--r-- 444 /srv/atelier-droits/rapport.txt
```

### `+` adjusts, `=` resets

The difference between `+` and `=` is the first trap of symbolic notation.
Start from a file open to everyone for reading and writing:

```bash
chmod 0666 /srv/atelier-droits/rapport.txt
chmod o+r  /srv/atelier-droits/rapport.txt
stat -c '%a %n' /srv/atelier-droits/rapport.txt
```

```text
666 /srv/atelier-droits/rapport.txt
```

Nothing moved: `o+r` **adds** read, which was already there, and says nothing
about write. With `=`, the whole triad is rewritten:

```bash
chmod o=r /srv/atelier-droits/rapport.txt
stat -c '%a %n' /srv/atelier-droits/rapport.txt
```

```text
664 /srv/atelier-droits/rapport.txt
```

Remember the guide's rule: `+` or `-` when you adjust **one** permission, `=` or
the octal when you want an exact state. A statement that says "this file must be
in …" asks for an exact state, so `=` or the octal, never `+`.

### Octal notation: three digits

Each permission has a value, and you add them up per triad.

| Permission | Value |
|------------|--------|
| `r` (read) | **4** |
| `w` (write) | **2** |
| `x` (execute) | **1** |

| Permissions | Sum | Octal |
|-------------|--------|-------|
| `rwx` | 4+2+1 | **7** |
| `rw-` | 4+2+0 | **6** |
| `r-x` | 4+0+1 | **5** |
| `r--` | 4+0+0 | **4** |
| `---` | 0+0+0 | **0** |

The three digits read in the order owner, group, others. Give the draft a team
mode: the owner and the group read and write, others get nothing.

```bash
chgrp redaction /srv/atelier-droits/rapport.txt
chmod 0660 /srv/atelier-droits/rapport.txt
stat -c '%A %a %U %G %n' /srv/atelier-droits/rapport.txt
```

```text
-rw-rw---- 660 theo redaction /srv/atelier-droits/rapport.txt
```

### Prove a permission rather than read it

Reading `ls -l` proves nothing: what counts is real access. `sudo -u <account>
<command>` runs the command under another identity and gives you the kernel's
answer.

```bash
sudo -u theo cat /srv/atelier-droits/rapport.txt
```

```text
brouillon de l article
```

```bash
sudo -u nadia cat /srv/atelier-droits/rapport.txt
```

```text
cat: /srv/atelier-droits/rapport.txt: Permission denied
```

```bash
sudo -u nadia sh -c 'echo ligne-de-nadia >> /srv/atelier-droits/rapport.txt'
```

```text
sh: line 1: /srv/atelier-droits/rapport.txt: Permission denied
```

`nadia` falls into the "others" triad, which is at `---`. Let her into the
group:

```bash
sudo usermod -aG redaction nadia
id nadia
```

```text
uid=1003(nadia) gid=1003(nadia) groups=1003(nadia),1004(redaction)
```

```bash
sudo -u nadia cat /srv/atelier-droits/rapport.txt
```

```text
brouillon de l article
ligne-de-theo
```

The file has not changed by a single bit: it is `nadia`'s membership that
changed triad. `sudo -u` starts a fresh process, whose group list is read at
that moment; a session that is already open keeps the groups it had at startup,
hence the reflex of logging back in after a `usermod -aG`.

### Only one level applies, and it is not necessarily the most generous

The kernel stops at the **first** level that matches: owner, otherwise group,
otherwise others. It does not accumulate. A deliberately absurd mode shows it:

```bash
chmod 0466 /srv/atelier-droits/rapport.txt
stat -c '%A %a %U %G %n' /srv/atelier-droits/rapport.txt
```

```text
-r--rw-rw- 466 theo redaction /srv/atelier-droits/rapport.txt
```

```bash
sudo -u theo sh -c 'echo essai-de-theo >> /srv/atelier-droits/rapport.txt'
```

```text
sh: line 1: /srv/atelier-droits/rapport.txt: Permission denied
```

```bash
sudo -u nadia sh -c 'echo ligne-de-nadia >> /srv/atelier-droits/rapport.txt'
```

No message: the write went through. `theo`, the file's **owner** and a member of
the group, cannot write, whereas `nadia`, a plain member of the group, can. The
`u` triad won, and it was worth `r--`. Practical consequence: a mode more
restrictive for `u` than for `g` or `o` is never useful, it only blocks the
owner.

### On a directory, `r` and `x` do not serve the same purpose

This is the point everybody gets wrong. On a directory, `r` allows you to
**list the names**, `x` to **traverse** it and reach the content. The two are
independent, so four situations exist. The setup: a directory owned by `theo`,
containing a known file, and `nadia` who is neither the owner nor a member of
the group (so she falls into the "others" triad).

```bash
cd /srv/atelier-droits
umask 002
mkdir -p dossier-test
echo "contenu du fichier" > dossier-test/dedans.txt
```

The four attempts, with the machine's real answer:

```bash
chmod o=rx /srv/atelier-droits/dossier-test     # drwxrwxr-x 775
sudo -u nadia ls  /srv/atelier-droits/dossier-test
sudo -u nadia cat /srv/atelier-droits/dossier-test/dedans.txt
sudo -u nadia sh -c 'cd /srv/atelier-droits/dossier-test && pwd'
```

```text
dedans.txt
contenu du fichier
/srv/atelier-droits/dossier-test
```

```bash
chmod o=r /srv/atelier-droits/dossier-test      # drwxrwxr-- 774
```

```text
dedans.txt
cat: /srv/atelier-droits/dossier-test/dedans.txt: Permission denied
sh: line 1: cd: /srv/atelier-droits/dossier-test: Permission denied
```

```bash
chmod o=x /srv/atelier-droits/dossier-test      # drwxrwx--x 771
```

```text
ls: cannot open directory '/srv/atelier-droits/dossier-test': Permission denied
contenu du fichier
/srv/atelier-droits/dossier-test
```

```bash
chmod o= /srv/atelier-droits/dossier-test       # drwxrwx--- 770
```

```text
ls: cannot open directory '/srv/atelier-droits/dossier-test': Permission denied
cat: /srv/atelier-droits/dossier-test/dedans.txt: Permission denied
sh: line 1: cd: /srv/atelier-droits/dossier-test: Permission denied
```

The summary table:

| Permissions on the directory | `ls` | `cat` of a known file | `cd` |
|---|---|---|---|
| `r-x` | yes | yes | yes |
| `r--` | yes, names only | no | no |
| `--x` | no | yes | yes |
| `---` | no | no | no |

The `r--` case deserves one more look, because `ls -l` becomes talkative there
without knowing anything:

```bash
sudo -u nadia ls -l /srv/atelier-droits/dossier-test
```

```text
ls: cannot access '/srv/atelier-droits/dossier-test/dedans.txt': Permission denied
total 0
-????????? ? ? ? ?            ? dedans.txt
```

The name comes from the directory (the `r` permission), everything else comes
from the file, which `ls` cannot reach for lack of `x` on the directory.
Conversely, the `--x` case is that of a "blind" directory: impossible to know
what it contains, but any file whose name you know opens normally.

Two consequences to keep in mind:

- a directory without `x` is unusable, even with `r`: it is almost always a
  mistake;
- you need the `x` on **every** directory of the path, not only on the last
  one. A perfectly open file stays unreachable if a parent directory is closed.

### Deleting a file means modifying the directory

Counter-intuitive point: deleting does not write into the file, it removes its
name from the directory. The permissions checked are therefore those of the
**directory** (`w` and `x`), not those of the file.

```bash
mkdir /srv/atelier-droits/bac-a-sable
echo a > /srv/atelier-droits/bac-a-sable/blinde.txt
chmod 0777 /srv/atelier-droits/bac-a-sable          # drwxrwxrwx
chmod 0000 /srv/atelier-droits/bac-a-sable/blinde.txt   # ----------
sudo -u nadia rm /srv/atelier-droits/bac-a-sable/blinde.txt
```

No message: a file with no permission at all was deleted by someone who could
neither read nor write it. The opposite case:

```bash
mkdir /srv/atelier-droits/verrou
echo b > /srv/atelier-droits/verrou/ouvert.txt
chmod 0555 /srv/atelier-droits/verrou               # dr-xr-xr-x, no w
chmod 0777 /srv/atelier-droits/verrou/ouvert.txt    # -rwxrwxrwx
sudo -u nadia rm /srv/atelier-droits/verrou/ouvert.txt
```

```text
rm: cannot remove '/srv/atelier-droits/verrou/ouvert.txt': Permission denied
```

```bash
sudo -u nadia sh -c 'echo intrusion >> /srv/atelier-droits/verrou/ouvert.txt'
```

No message: she cannot delete it, but she can write into it. The file's
permissions protect its **content**, the directory's protect its **existence**.
Locking down a sensitive file therefore means looking at the directory that
holds it too.

### `chown` and `chgrp`: owner and group

Setting the right bits is useless if the file belongs to the wrong account. The
setup: a file `planning.txt` created by `theo`, so `theo:theo`.

```bash
sudo -u theo chown nadia /srv/atelier-droits/planning.txt
```

```text
chown: changing ownership of '/srv/atelier-droits/planning.txt': Operation not permitted
```

Giving a file away is reserved to root, as the guide says: otherwise anyone
could get rid of an inconvenient file by handing it to someone else. The group,
on the other hand, obeys a finer rule that the guide does not detail: the
**owner** can change it, provided he is a member of the target group.

```bash
sudo -u theo chgrp redaction /srv/atelier-droits/planning.txt   # theo is a member: accepted
sudo -u theo chgrp nadia     /srv/atelier-droits/planning.txt   # he is not
```

```text
chgrp: changing group of '/srv/atelier-droits/planning.txt': Operation not permitted
```

With root permissions, both forms from the guide work, `chown` being able to do
both at once:

```bash
sudo chown nadia:nadia /srv/atelier-droits/planning.txt   # owner and group
sudo chown :redaction  /srv/atelier-droits/planning.txt   # the group alone
stat -c '%U %G %n' /srv/atelier-droits/planning.txt
```

```text
nadia redaction /srv/atelier-droits/planning.txt
```

One last useful reminder: `chmod` also requires being the owner (or root). Once
the file has moved to `nadia`, `theo` can no longer change anything on it.

```bash
sudo -u theo chmod 0664 /srv/atelier-droits/planning.txt
```

```text
chmod: changing permissions of '/srv/atelier-droits/planning.txt': Operation not permitted
```

### Recursion, and why `-R` with an octal is almost always wrong

The setup: a small tree of directories at `775` and files at `664`, on which you
apply a well-meaning `chmod -R`.

```bash
cd /srv/atelier-droits
umask 002
mkdir -p projet/config
touch projet/lisezmoi.md projet/config/app.conf
chmod -R 775 /srv/atelier-droits/projet
find /srv/atelier-droits/projet -printf '%m %M %p\n' | sort -k3
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
775 -rwxrwxr-x /srv/atelier-droits/projet/config/app.conf
775 -rwxrwxr-x /srv/atelier-droits/projet/lisezmoi.md
```

A configuration file turned executable: the same digit does not have the same
meaning on a file and on a directory, and `-R` does not tell the difference. The
guide's workaround is to handle the two types separately:

```bash
find /srv/atelier-droits/projet -type d -exec chmod 775 {} +
find /srv/atelier-droits/projet -type f -exec chmod 664 {} +
find /srv/atelier-droits/projet -printf '%m %M %p\n' | sort -k3
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
664 -rw-rw-r-- /srv/atelier-droits/projet/config/app.conf
664 -rw-rw-r-- /srv/atelier-droits/projet/lisezmoi.md
```

`chmod` offers a second, shorter workaround, in symbolic form: the **uppercase**
`X` grants `x` only to directories and to files that already have it. Start from
a tree closed to others (`770` and `660`) and open it for reading:

```bash
chmod -R o+rx /srv/atelier-droits/projet    # lowercase x
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
665 -rw-rw-r-x /srv/atelier-droits/projet/config/app.conf
665 -rw-rw-r-x /srv/atelier-droits/projet/lisezmoi.md
```

```bash
chmod -R o+rX /srv/atelier-droits/projet    # uppercase X
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
664 -rw-rw-r-- /srv/atelier-droits/projet/config/app.conf
664 -rw-rw-r-- /srv/atelier-droits/projet/lisezmoi.md
```

The directories are traversable, the files stayed non-executable: that is the
wanted result, in one command.

One detail that misleads during checks: `find` obeys permissions too. Run by an
account that lacks `x` on the tree, it only shows the root and an error, which
looks like an empty directory.

```text
find: '/srv/atelier-droits/projet': Permission denied
770 drwxrwx--- /srv/atelier-droits/projet
```

### `umask`: the permissions of files you have not created yet

A new file is never born as `rwxrwxrwx`. A mask, the `umask`, removes bits at
creation time.

```bash
umask
```

```text
0022
```

```bash
cd /srv/atelier-droits
umask 007
touch u007.txt && mkdir u007.d
stat -c '%a %A %n' u007.txt u007.d
```

```text
660 -rw-rw---- u007.txt
770 drwxrwx--- u007.d
```

The starting point is `666` for a file and `777` for a directory: files **never**
receive the `x` bit at creation, which is why a freshly written script has to be
made executable by hand.

The `umask` is a **mask**, not a subtraction, even if the gap does not show with
the usual values:

```bash
umask 013
touch u013.txt && stat -c '%a %A %n' u013.txt
```

```text
664 -rw-rw-r-- u013.txt
```

A subtraction would give `666 - 013 = 653`; the real result is `664`. The kernel
removes **bits**: the `1` in the mask targets `x`, which the file did not have
anyway.

Finally, `umask` only applies to the current shell and does not affect existing
files. After the previous command, a new session starts back at `0022`. To make
it permanent, you have to set it in a profile file.

### The three-digit trap on a directory

A directory can carry extra bits (set-GID, sticky bit), which take a **fourth**
digit. And there, `chmod` does not behave the way you expect:

```bash
mkdir /srv/atelier-droits/partage
chmod 2775 /srv/atelier-droits/partage     # set the set-GID
chmod 775  /srv/atelier-droits/partage     # you think you are back to a plain mode
stat -c '%a %A %n' /srv/atelier-droits/partage
```

```text
2775 drwxrwsr-x /srv/atelier-droits/partage
```

The `s` is still there, and a leading `0` (`chmod 0775`) changes nothing either.
`man chmod` documents the fact: "For directories chmod preserves set-user-ID and
set-group-ID bits unless you explicitly specify otherwise". Three forms actually
clear these bits, all verified:

```bash
chmod g-s   /srv/atelier-droits/partage    # symbolic
chmod 00775 /srv/atelier-droits/partage    # two leading zeros
chmod =775  /srv/atelier-droits/partage    # equals sign
```

```text
775 drwxrwxr-x /srv/atelier-droits/partage
```

On a **file**, the rule is different: three digits are enough to clear the
set-UID.

```bash
cd /srv/atelier-droits
touch bin-demo
chmod 4755 bin-demo && stat -c '%a %A' bin-demo
chmod 755  bin-demo && stat -c '%a %A' bin-demo
```

```text
4755 -rwsr-xr-x
755 -rwxr-xr-x
```

This is exactly the kind of gap that makes an automated check fail: the command
reported nothing, and the mode you got is not the one asked for. Always check
afterwards with `stat -c '%a'`.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `chmod: … Operation not permitted` | you are neither the owner nor root |
| `chown: … Operation not permitted` | only root can give a file away |
| `chgrp: … Operation not permitted` | you are not a member of the target group |
| `Permission denied` while reading a file that is nevertheless open | the `x` is missing on a directory of the path |
| `ls` works but `cat` fails | `r` without `x` on the directory |
| `cat` works but `ls` fails | `x` without `r` on the directory |
| `ls -l` shows `?` everywhere | `r` without `x`: names are readable, metadata is not |
| The owner is blocked while the group gets through | only one level applies, and `u` is more restrictive than `g` |
| Impossible to delete a file at `777` | the directory decides (`w` and `x`) |
| Every file became executable | `chmod -R` with an octal; use `find -type f/-type d` or uppercase `X` |
| The resulting mode starts with one digit too many | set-UID or set-GID preserved; use `g-s`, `00…` or `=…` |
| A new file does not have the expected permissions | the shell's `umask`, to be checked with `umask` |

### Tearing down the setup

```bash
sudo rm -rf /srv/atelier-droits
sudo userdel -r theo
sudo userdel -r nadia
sudo groupdel redaction
```
