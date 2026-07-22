# Lab — hard and symbolic links

## Reminder

[**Navigating files on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/)

A **hard link** (`ln target name`) is another name for the same inode: same data,
link count goes up, and it survives deleting the original. A **symbolic link**
(`ln -s target name`) stores a path to the target; it can cross filesystems and
point at directories, but breaks if the target moves. `ls -li` reveals the inode
and the link count.

## The course

The examples below work in `~/atelier-liens`, on a file `rapport.log` and a
directory `stock/archives`: the challenge will ask you for other names in
another directory. The point is to learn how to observe, not to copy a line.

Every output on this page was recorded on an AlmaLinux 10 (`coreutils 9.5`,
**XFS** filesystem). The inode numbers will differ on your machine: what matters
is that they are **equal** or **different** where the text says so.

### The demonstration setup

```bash
mkdir -p ~/atelier-liens
cd ~/atelier-liens
printf "ligne 1 du rapport\nligne 2 du rapport\n" > rapport.log
ls -li
```

```text
total 4
309333 -rw-r--r--. 1 ansible ansible 38 Jul 22 13:58 rapport.log
```

The **`-i`** option of `ls` adds a first column: the **inode number**. This is
the real identifier of the file on the filesystem. The name `rapport.log` is
only a directory entry pointing at that inode.

The column right after the permissions (`1` here) is the **link count**, as the
`ls -l` legend in the guide recalls. Remember those two columns: this whole lab
fits inside them.

### A hard link: a second name for the same inode

```bash
ln rapport.log journal-dur.log
ls -li
```

```text
total 8
309333 -rw-r--r--. 2 ansible ansible 38 Jul 22 13:58 journal-dur.log
309333 -rw-r--r--. 2 ansible ansible 38 Jul 22 13:58 rapport.log
```

Two lines, **a single inode number**: `309333` on both sides. And the count went
from `1` to `2`. Nothing was copied: there are now two names designating the
same file. `stat` says it even more clearly:

```bash
stat rapport.log journal-dur.log
```

```text
  File: rapport.log
  Size: 38        	Blocks: 8          IO Block: 4096   regular file
Device: 252,4	Inode: 309333      Links: 2
Access: (0644/-rw-r--r--)  Uid: ( 1001/ ansible)   Gid: ( 1001/ ansible)
...
  File: journal-dur.log
  Size: 38        	Blocks: 8          IO Block: 4096   regular file
Device: 252,4	Inode: 309333      Links: 2
Access: (0644/-rw-r--r--)  Uid: ( 1001/ ansible)   Gid: ( 1001/ ansible)
```

Same `Device`, same `Inode`, same `Links`, same permissions, same owner. Only
the `File` field differs, because it is the only one not stored in the inode.

Direct consequence: what you write through one name is read through the other,
and what you change through one name changes for the other.

```bash
echo "ligne 3 ajoutee par le lien" >> journal-dur.log
cat rapport.log
```

```text
ligne 1 du rapport
ligne 2 du rapport
ligne 3 ajoutee par le lien
```

```bash
chmod 640 journal-dur.log
ls -l rapport.log journal-dur.log
```

```text
-rw-r-----. 2 ansible ansible 66 Jul 22 13:58 journal-dur.log
-rw-r-----. 2 ansible ansible 66 Jul 22 13:58 rapport.log
```

The `chmod` was requested on one name only, and both changed: permissions live
in the inode, not in the name.

### The link count, and the survival of data

Removing a name does not remove the file: it **decrements** the count. The
contents are freed only when the count drops to zero.

```bash
rm rapport.log
ls -li
cat journal-dur.log
```

```text
total 4
309333 -rw-r-----. 1 ansible ansible 66 Jul 22 13:58 journal-dur.log
ligne 1 du rapport
ligne 2 du rapport
ligne 3 ajoutee par le lien
```

The original name is gone, the inode `309333` is still there with its three
lines, and the count went back down to `1`. This is the property that really
distinguishes a hard link from a simple pointer: there is no main name and no
secondary name, there are **two names of strictly equal rank**.

You can even recreate the lost name from the surviving one, then remove the
other:

```bash
ln journal-dur.log rapport.log
ls -li
```

```text
total 8
309333 -rw-r-----. 2 ansible ansible 66 Jul 22 13:58 journal-dur.log
309333 -rw-r-----. 2 ansible ansible 66 Jul 22 13:58 rapport.log
```

```bash
rm journal-dur.log
ls -li
```

```text
total 4
309333 -rw-r-----. 1 ansible ansible 66 Jul 22 13:58 rapport.log
```

The count goes up, goes down, and the inode does not move.

### The symbolic link: a path, not an inode

```bash
ln -s rapport.log courant.log
ls -li
```

```text
total 4
309334 lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
309333 -rw-r-----. 1 ansible ansible 66 Jul 22 13:58 rapport.log
```

Four differences from the hard link stand out:

1. **different inode** (`309334` against `309333`): it is a file in its own
   right, of a type in its own right;
2. the first character of the line is **`l`** and not `-`: the file type is
   "symbolic link";
3. the permissions shown are `rwxrwxrwx`, always, for everyone;
4. `ls -l` shows the **target** after an arrow, and the **size is 11**, whereas
   the file it points at is 66.

Eleven is exactly the number of characters in the string `rapport.log`. A
symbolic link contains nothing but that text:

```bash
ln -s /home/ansible/atelier-liens/rapport.log absolu.log
ls -l courant.log absolu.log
```

```text
lrwxrwxrwx. 1 ansible ansible 39 Jul 22 13:58 absolu.log -> /home/ansible/atelier-liens/rapport.log
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
```

39 characters for `/home/ansible/atelier-liens/rapport.log`, 11 for
`rapport.log`. The size of a symbolic link **is** the length of the path it
stores.

To read that path without going through `ls`, two complementary commands:

```bash
readlink courant.log        # the path as it is stored
readlink -f courant.log     # the final path, once everything is resolved
```

```text
rapport.log
/home/ansible/atelier-liens/rapport.log
```

And to see both sides of the link, `stat` without then with `-L`:

```bash
stat -c  "%N | type=%F | taille=%s | inode=%i" courant.log
stat -Lc "%N | type=%F | taille=%s | inode=%i" courant.log
```

```text
'courant.log' -> 'rapport.log' | type=symbolic link | taille=11 | inode=309334
'courant.log' | type=regular file | taille=66 | inode=309333
```

Without `-L`, `stat` describes the **link**. With `-L`, it describes the
**target**. Most commands (`cat`, `cp`, `grep`, `chmod`) follow the link by
default, like `stat -L`.

Precisely, the `rwxrwxrwx` of the link is useless: it is the rights of the
target that decide.

```bash
chmod 600 courant.log
ls -l courant.log rapport.log
```

```text
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
-rw-------. 1 ansible ansible 66 Jul 22 13:58 rapport.log
```

The `chmod` went through the link and modified `rapport.log`, the link did not
move. And `chmod -h`, which exists to target the link itself, changes nothing
either under Linux: it exits successfully with no effect.

```bash
chmod -h 777 courant.log ; echo "rc=$?"
ls -l courant.log
```

```text
rc=0
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
```

So do not try to "secure" a symbolic link through its permissions: they are
decorative.

### The dangling link, and how to spot it

Since the link contains only a path, it is enough for that path to stop being
valid for the link to point into the void. This is the **dangling link**.

```bash
mv rapport.log rapport-2026.log
ls -l
```

```text
total 4
lrwxrwxrwx. 1 ansible ansible 39 Jul 22 13:58 absolu.log -> /home/ansible/atelier-liens/rapport.log
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
-rw-------. 1 ansible ansible 66 Jul 22 13:58 rapport-2026.log
```

Nothing in this output signals the break: both links still proudly show their
target. It shows up in use:

```bash
cat courant.log ; echo "rc=$?"
```

```text
cat: courant.log: No such file or directory
rc=1
```

The message is misleading: it is not `courant.log` that is missing, it is its
target. The shell tests do tell the difference:

```bash
test -e courant.log && echo "-e vrai" || echo "-e faux"
test -L courant.log && echo "-L vrai" || echo "-L faux"
```

```text
-e faux
-L vrai
```

**`-e`** tests what is **at the end** of the link, **`-L`** tests the link
itself. A file can therefore be both "nonexistent" and "present".

To sweep a tree, `find` has the right option:

```bash
find . -type l                       # all symbolic links
find . -xtype l                      # only the dangling ones
find . -xtype l -printf "%p -> %l\n" # with the path they store
```

```text
./courant.log
./absolu.log
./courant.log -> rapport.log
./absolu.log -> /home/ansible/atelier-liens/rapport.log
```

`-xtype l` is the command to remember for an audit: it reports only broken
links. Once the target is put back, it shows nothing any more:

```bash
mv rapport-2026.log rapport.log
find . -xtype l
```

```text
```

### Relative or absolute: what breaks, and when

A relative link is interpreted **from the directory where the link is**, not
from the one you run the command in. Moving the link is therefore enough to
break it, whereas an absolute link survives.

```bash
mkdir -p sous-dossier
mv courant.log absolu.log sous-dossier/
cd sous-dossier
ls -l
```

```text
total 0
lrwxrwxrwx. 1 ansible ansible 39 Jul 22 13:58 absolu.log -> /home/ansible/atelier-liens/rapport.log
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
```

```bash
cat courant.log  >/dev/null ; echo "courant rc=$?"
cat absolu.log   >/dev/null ; echo "absolu  rc=$?"
```

```text
cat: courant.log: No such file or directory
courant rc=1
absolu  rc=0
```

Each has its own domain:

- the **relative** link survives moving **the whole set** (link and target
  together, a tree copied elsewhere, a mount point that changes);
- the **absolute** link survives moving **the link alone**, but breaks if the
  whole tree is remounted elsewhere.

### The limits of the hard link

This is where the two tools stop being interchangeable. A hard link is a
directory entry pointing at an inode: it can therefore only exist where that
inode is addressable.

**First limit: no hard link to a directory.**

```bash
mkdir -p stock/archives
ln stock/archives archives-dur ; echo "rc=$?"
sudo ln stock/archives archives-dur ; echo "rc=$?"
```

```text
ln: stock/archives: hard link not allowed for directory
rc=1
ln: stock/archives: hard link not allowed for directory
rc=1
```

The refusal comes from the kernel, and `sudo` changes nothing. The reason shows
in the link count of a directory, which is already used by the system:

```bash
mkdir -p stock/archives/2025 stock/archives/2026
stat -c "%n : %h liens, inode %i" stock/archives stock/archives/. stock/archives/2025/..
```

```text
stock/archives : 4 liens, inode 25672520
stock/archives/. : 4 liens, inode 25672520
stock/archives/2025/.. : 4 liens, inode 25672520
```

One single inode, three paths. A directory has **2 base links** (its name in the
parent, and its own `.`), **plus one per subdirectory** (the `..` of each one):
here 2 + 2 = 4. Allowing arbitrary hard links to directories would make it
possible to build loops that no traversal could get out of.

**Second limit: no hard link between two filesystems.** An inode number only
makes sense inside a filesystem; two unrelated files, on two disks, can
perfectly well carry the same number.

> The commands that follow **erase** the contents of `/dev/vdb`. Check with
> `lsblk` that this disk is indeed empty and has no mount point before running
> them.

```bash
sudo mkfs.xfs -q -L ANNEXE /dev/vdb
sudo mkdir -p /mnt/annexe
sudo mount /dev/vdb /mnt/annexe
sudo chown "$USER":"$USER" /mnt/annexe
df -hT /mnt/annexe /
```

```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/vdb       xfs   2.0G   71M  1.9G   4% /mnt/annexe
/dev/vda4      xfs   8.8G  1.1G  7.7G  13% /
```

Two mounted filesystems, each with its own inode table. Trying to hard link
from one to the other fails, with a message you must be able to recognise:

```bash
cd ~/atelier-liens
ln rapport.log /mnt/annexe/rapport-dur.log ; echo "rc=$?"
```

```text
ln: failed to create hard link '/mnt/annexe/rapport-dur.log' => 'rapport.log': Invalid cross-device link
rc=1
```

**`Invalid cross-device link`**: the exact translation of "these two paths are
not on the same filesystem". The symbolic link goes through without a
complaint, since it only stores text:

```bash
ln -s /home/ansible/atelier-liens/rapport.log /mnt/annexe/rapport-lien.log
cat /mnt/annexe/rapport-lien.log
```

```text
ligne 1 du rapport
ligne 2 du rapport
ligne 3 ajoutee par le lien
```

The word "device" in the message refers to a number that `stat` displays:

```bash
cp ~/atelier-liens/rapport.log /mnt/annexe/rapport-copie.log
stat -c "%n : device %D, inode %i, liens %h" ~/atelier-liens/rapport.log /mnt/annexe/rapport-copie.log
```

```text
/home/ansible/atelier-liens/rapport.log : device fc04, inode 309333, liens 1
/mnt/annexe/rapport-copie.log : device fc10, inode 132, liens 1
```

Two different `device` numbers: no hard link is possible between these two
files. The same boundary explains the behaviour of `mv`, which merely renames a
directory entry as long as it stays in place, and has to copy then delete as
soon as it leaves:

```bash
echo x > f.txt ; stat -c "avant    : inode %i" f.txt
mv f.txt g.txt ; stat -c "meme fs  : inode %i" g.txt
mv g.txt /mnt/annexe/h.txt ; stat -c "autre fs : inode %i" /mnt/annexe/h.txt
```

```text
avant    : inode 17458674
meme fs  : inode 17458674
autre fs : inode 134
```

Renaming keeps the inode, crossing over makes a new one.

**Third limit, less well known: the kernel protects hard links.** On a modern
distribution, you cannot create a hard link to a file you neither own nor have
write access to.

```bash
sysctl fs.protected_hardlinks fs.protected_symlinks
ln /etc/hostname /tmp/hostname-dur ; echo "rc=$?"
```

```text
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
ln: failed to create hard link '/tmp/hostname-dur' => '/etc/hostname': Operation not permitted
rc=1
```

`Operation not permitted` on a `ln` while the destination directory is
writable: think of this setting before looking elsewhere.

**Finally, a hard link requires the target to already exist**, whereas a
symbolic link does not care whether its own exists:

```bash
ln absent.log copie.log ; echo "rc=$?"
ln -s absent.log futur.log ; echo "rc=$?"
ls -l futur.log
```

```text
ln: failed to access 'absent.log': No such file or directory
rc=1
rc=0
lrwxrwxrwx. 1 ansible ansible 10 Jul 22 13:59 futur.log -> absent.log
```

This is useful: you can lay down a link to a file that will be produced later,
but it is also how you build a dangling link without noticing, by getting one
character wrong in the target name.

### A symbolic link to a directory

The symbolic link has none of the three previous limits. In particular, it
points at a directory just fine:

```bash
echo "sauvegarde du 22" > stock/archives/backup-22.txt
ln -s stock/archives dernier
ls -l dernier
```

```text
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 13:59 dernier -> stock/archives
```

From there, `dernier` is used like the directory it points at. Beware however of
the behaviour of `ls`, which depends on the presence of a **trailing slash**:

```bash
ls dernier          # lists the contents
ls -l dernier       # describes the link
ls -l dernier/      # lists the contents, long format
```

```text
2025
2026
backup-22.txt
```

```text
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 13:59 dernier -> stock/archives
```

```text
total 4
drwxr-xr-x. 2 ansible ansible  6 Jul 22 13:59 2025
drwxr-xr-x. 2 ansible ansible  6 Jul 22 13:59 2026
-rw-r--r--. 1 ansible ansible 17 Jul 22 13:59 backup-22.txt
```

The rule: **the trailing slash forces the link to be traversed**. `dernier`
designates the link, `dernier/` designates the directory at the end. This
distinction comes back further down, and there it does damage.

The shell, for its part, remembers the path you came through:

```bash
cd dernier
pwd        # logical path, the one you typed
pwd -P     # physical path, after links are resolved
cd ..
pwd
```

```text
/home/ansible/atelier-liens/dernier
/home/ansible/atelier-liens/stock/archives
/home/ansible/atelier-liens
```

The `cd ..` did not go up to `stock`, the real parent, but to `~/atelier-liens`,
the parent of the **link**. This is the default behaviour of `cd`, and it is a
source of mistakes when you chain relative commands. `cd -P` asks for immediate
traversal:

```bash
cd ~/atelier-liens
cd -P dernier
pwd
cd ..
pwd
```

```text
/home/ansible/atelier-liens/stock/archives
/home/ansible/atelier-liens/stock
```

This time `cd ..` does go up into `stock`.

### Repointing a symbolic link without getting trapped

Repointing a link at another target is the most common use of the symbolic link
(`dernier` following the latest backup, for example). It is also the move that
traps you the most, as soon as the link points at a directory.

The experiment that follows was run in a fresh directory, to keep the outputs
readable:

```bash
mkdir -p /tmp/essai/stock/archives /tmp/essai/stock/archives-2025
cd /tmp/essai
ln -s stock/archives dernier
ls -l
```

```text
total 0
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 14:00 dernier -> stock/archives
drwxr-xr-x. 4 ansible ansible 43 Jul 22 14:00 stock
```

Now let us repoint `dernier` at `stock/archives-2025` with the usual `-f`:

```bash
ln -sf stock/archives-2025 dernier ; echo "rc=$?"
ls -l dernier
```

```text
rc=0
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 14:00 dernier -> stock/archives
```

Success announced, and yet `dernier` still points at the same place. Where did
the request go?

```bash
ls -l stock/archives
```

```text
total 0
lrwxrwxrwx. 1 ansible ansible 19 Jul 22 14:00 archives-2025 -> stock/archives-2025
```

`ln` traversed the link, considered `dernier` to be the destination directory,
and created a new link **inside it**. The `-f` only served to allow overwriting
that inner link. The result is doubly bad: the expected link has not moved, and
a stray link, dangling on top of that, has appeared in the tree.

The option that fixes this is **`-n`** (`--no-dereference`): it asks for a
destination that is a link to a directory to be treated as an ordinary file.

```bash
rm -f stock/archives/archives-2025
ln -sfn stock/archives-2025 dernier ; echo "rc=$?"
ls -l dernier
```

```text
rc=0
lrwxrwxrwx. 1 ansible ansible 19 Jul 22 14:00 dernier -> stock/archives-2025
```

**`ln -sfn`** is therefore the reflex for repointing a link to a directory. The
alternative, just as safe, is to delete the link then recreate it.

### Deleting a link: the trailing slash is a trap

On a symbolic link to a directory, `rm` has four behaviours depending on whether
you write `-r` or not, and whether you add a trailing slash or not. The four
tries that follow each start again from the **same** structure:

```text
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
./lien          (lien -> cible)
```

**`rm lien`**: the normal case, and the right one.

```bash
rm lien ; echo "rc=$?" ; find .
```

```text
rc=0
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
```

Only the link disappears, the target and all its contents are intact.

**`rm -r lien`**: strictly identical. Without a trailing slash, `rm` does not
traverse the link, even with `-r`.

```text
rc=0
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
```

**`rm lien/`**: a flat refusal, nothing is touched.

```bash
rm lien/ ; echo "rc=$?" ; find .
```

```text
rm: cannot remove 'lien/': Is a directory
rc=1
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
./lien
```

**`rm -r lien/`**: the trap.

```bash
rm -r lien/ ; echo "rc=$?" ; find .
```

```text
rm: cannot remove 'lien/': Not a directory
rc=1
.
./cible
./lien
```

Read that last output twice. `rm` reported an **error** and returned an exit
code of **1**, but it had first recursively emptied `cible/`: `a.txt`, `sous/`
and `b.txt` are gone. The link is still there, and the target directory still
exists, empty. So the command failed to do what it was asked, and succeeded in
destroying what you did not want to lose.

The explanation lies in the rule seen above: the trailing slash forces the link
to be traversed. The `-r` therefore applies to the **directory at the end**,
whose contents it erases; then `rm` tries to remove the entry `lien/`, which is
not a directory, and fails.

> Never put a trailing slash on a symbolic link you want to delete. The guide
> recalls that `rm` is irreversible: here, a single extra character
> demonstrates it.

One command removes all doubt, because it can only do one thing, remove a
directory entry, and it refuses directories:

```bash
unlink lien ; echo "rc=$?"
unlink cible ; echo "rc=$?"
```

```text
rc=0
unlink: cannot unlink 'cible': Is a directory
rc=1
```

### Finding all the names of a file

A symbolic link is visible in `ls -l`. A hard link is not: nothing tells the two
names apart. Only the count betrays that another one exists, without saying
where. Three commands answer the question.

```bash
cd ~/atelier-liens
ln rapport.log stock/archives/backup-rapport.log
ls -li rapport.log stock/archives/backup-rapport.log
```

```text
309333 -rw-------. 2 ansible ansible 66 Jul 22 13:58 rapport.log
309333 -rw-------. 2 ansible ansible 66 Jul 22 13:58 stock/archives/backup-rapport.log
```

```bash
find ~/atelier-liens -samefile rapport.log         # by file comparison
find ~/atelier-liens -xdev -inum 309333            # by inode number
find ~/atelier-liens -type f -links +1 -printf "%n %p\n"   # all multi-name files
```

```text
/home/ansible/atelier-liens/rapport.log
/home/ansible/atelier-liens/stock/archives/backup-rapport.log
/home/ansible/atelier-liens/rapport.log
/home/ansible/atelier-liens/stock/archives/backup-rapport.log
2 /home/ansible/atelier-liens/rapport.log
2 /home/ansible/atelier-liens/stock/archives/backup-rapport.log
```

`-samefile` is the safest: it does not require knowing the number. `-inum`
assumes you stay on the same filesystem, hence the `-xdev`.

The count has a practical consequence on space accounting: `du` counts an inode
**only once**, even if it meets it under several names.

```bash
du -ch  --apparent-size rapport.log stock/archives/backup-rapport.log
du -clh --apparent-size rapport.log stock/archives/backup-rapport.log
```

```text
66	rapport.log
66	total
```

```text
66	rapport.log
66	stock/archives/backup-rapport.log
132	total
```

Without `-l`, `du` does not even show the second name, and the total stays at
66: that is the space actually occupied. With `-l`, it counts each name and
announces 132, which is wrong in terms of disk usage. This is how backups made
of hard links can contain ten "copies" of a tree without taking up ten times the
space.

### Copying: what follows the link and what preserves it

Once the links are in place, the way you copy them decides what you get on
arrival.

```bash
mkdir -p /tmp/essai-copie && cd /tmp/essai-copie
echo contenu > source.txt
ln -s source.txt lien.txt
cp    lien.txt clone-defaut.txt     # follows the link: copies the CONTENTS
cp -P lien.txt clone-P.txt          # preserves the link
cp -a lien.txt clone-a.txt          # archive: preserves it too
cp -l source.txt clone-dur.txt      # creates a HARD LINK, not a copy
ls -li
```

```text
total 12
17458672 lrwxrwxrwx. 1 ansible ansible 10 Jul 22 14:01 clone-a.txt -> source.txt
17458670 -rw-r--r--. 1 ansible ansible  8 Jul 22 14:01 clone-defaut.txt
17458668 -rw-r--r--. 2 ansible ansible  8 Jul 22 14:01 clone-dur.txt
17458671 lrwxrwxrwx. 1 ansible ansible 10 Jul 22 14:01 clone-P.txt -> source.txt
17458669 lrwxrwxrwx. 1 ansible ansible 10 Jul 22 14:01 lien.txt -> source.txt
17458668 -rw-r--r--. 2 ansible ansible  8 Jul 22 14:01 source.txt
```

Four different results for four commands:

- `clone-defaut.txt` is an **ordinary file**, with a new inode: `cp` followed
  the link and copied the contents;
- `clone-P.txt` and `clone-a.txt` are **symbolic links**, with their own inodes
  and the same target;
- `clone-dur.txt` shares inode `17458668` with `source.txt`, whose count went to
  `2`: `cp -l` copied nothing at all.

Remember `cp -a` to copy a tree without distorting its links, and `cp -l` when
you explicitly want a second name.

### Links everywhere in the system

These two mechanisms are not exercise curiosities: the system is full of them.

```bash
ls -l /etc/localtime
readlink -f /etc/localtime
ls -l /usr/bin/python3
```

```text
lrwxrwxrwx. 1 root root 25 May 26 15:21 /etc/localtime -> ../usr/share/zoneinfo/UTC
/usr/share/zoneinfo/UTC
lrwxrwxrwx. 1 root root 10 Apr 16 00:00 /usr/bin/python3 -> python3.12
```

The time zone is a **relative** symbolic link to a file of the `zoneinfo`
database: changing time zone means repointing that link. `/usr/bin/python3` is a
link to the version actually installed, which lets scripts never name a version
number.

`namei -l` unrolls a whole path, link by link:

```bash
namei -l /etc/localtime
```

```text
f: /etc/localtime
dr-xr-xr-x root root /
drwxr-xr-x root root etc
lrwxrwxrwx root root localtime -> ../usr/share/zoneinfo/UTC
dr-xr-xr-x root root   ..
drwxr-xr-x root root   usr
drwxr-xr-x root root   share
drwxr-xr-x root root   zoneinfo
-rw-r--r-- root root   UTC
```

Hard links are more discreet, but present as well, often so that one binary
answers to several names:

```bash
find /usr/bin -maxdepth 1 -type f -links +1 -printf "%n %i %p\n" | sort -k2
```

```text
2 17458311 /usr/bin/named-checkzone
2 17458311 /usr/bin/named-compilezone
```

Two commands, one single program on the disk. And it really does adapt its
behaviour to the name it is called under:

```bash
named-checkzone   2>&1 | head -1 | cut -c1-40
named-compilezone 2>&1 | head -2 | tail -1 | cut -c1-40
```

```text
usage: named-checkzone [-djqvD] [-c clas
usage: named-compilezone [-djqvD] [-c cl
```

One accepts to run without `-o`, the other answers first with
`output file required, but not specified`. Same inode, two interfaces.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `hard link not allowed for directory` | `ln` without `-s` on a directory; only the symbolic link allows it |
| `Invalid cross-device link` | source and destination are not on the same filesystem; check it with `df` or `stat -c %D` |
| `failed to access '…': No such file or directory` on `ln` | a hard link requires an existing target; `ln -s` accepts a missing one |
| `Operation not permitted` on `ln` although the directory is writable | `fs.protected_hardlinks = 1`: you do not link a file you do not own |
| `cat: …: No such file or directory` on a file that `ls` lists fine | dangling link; confirm it with `test -L`, find them with `find -xtype l` |
| The link stopped working after a move | relative link moved without its target; redo it, or switch it to absolute |
| `ln -sf` on a link to a directory changes nothing | the link was traversed, the new link was created inside it; use `ln -sfn` |
| `rm: cannot remove 'lien/': Not a directory` | trailing slash on a link; **the contents of the target have just been erased** |
| `rm: cannot remove 'lien/': Is a directory` | trailing slash without `-r`; nothing was deleted, remove the slash |
| The link count of a directory is not 1 | normal: 2 plus one per subdirectory, because of `.` and `..` |
| `du` reports less than the sum of the files | hard links share the same inode, counted only once |
| The copy lost the symbolic links | `cp` follows them by default; use `cp -a` (or `cp -P`) |

### Undoing the demonstration

```bash
cd ~
rm -rf ~/atelier-liens /tmp/essai /tmp/essai-copie
sudo umount /mnt/annexe
sudo rmdir /mnt/annexe
sudo wipefs -a /dev/vdb
```

Check that nothing is left: `lsblk` must no longer show a mount point for
`vdb`, and `find ~ -xtype l` must return nothing.
