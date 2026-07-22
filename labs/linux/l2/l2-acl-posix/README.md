# Lab — POSIX ACLs

## Reminder

[**ACLs on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/)

`setfacl -m u:<user>:<perms> <path>` adds a named-user entry, `g:<group>:` a
named-group one. On a directory, `d:` (or `-d`) sets a **default** ACL that new
files inherit. `getfacl <path>` prints all entries; `setfacl -b` removes them;
`ls -l` shows a trailing `+` on ACL-bearing files.

## The course

The examples below work on `/srv/atelier`, a demonstration directory, with the
user `bruno` and the group `relecteurs`: the challenge, for its part, will ask
you for other paths, other accounts and other permissions. The point is to learn
the method, not to copy a line.

### Check that ACLs are available

Two conditions: the tools, and a filesystem that knows how to store them.

```bash
command -v setfacl getfacl      # nothing is displayed if the package is missing
sudo dnf -y install acl         # on a minimal AlmaLinux image, it is missing
findmnt -no FSTYPE,OPTIONS /
```

On the VM of this lab, `findmnt` answers:

```text
xfs rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

Note that **no `acl` option appears**, and yet everything that follows works: on
**XFS** ACLs are always active, there is nothing extra to mount. So do not look
for an `acl` option in `/etc/fstab`: its absence proves nothing. The VM of this
lab only has XFS (`lsblk -f` confirms it), so the question does not arise here;
on old **ext3**, on the other hand, the `acl` mount option was necessary.

### The demonstration setup

```bash
sudo useradd -m bruno
sudo groupadd relecteurs
sudo mkdir -p /srv/atelier
echo "compte rendu de la reunion" | sudo tee /srv/atelier/notes.md
sudo chown -R root:root /srv/atelier
sudo chmod 0750 /srv/atelier
sudo chmod 0640 /srv/atelier/notes.md
```

The file belongs to `root:root`, the directory is in `0750`: `bruno` has
strictly no access. This is the typical starting point of a need for ACLs: you
want to open an access **without** changing the owner, the group, or the ugo
permissions.

### Set a user ACL, and the first surprise

```bash
sudo setfacl -m u:bruno:r /srv/atelier/notes.md
sudo getfacl -p /srv/atelier/notes.md
```

`-m` means *modify*: it adds the entry if it does not exist, replaces it
otherwise. `-p` asks `getfacl` to keep the leading `/` of the path, which avoids
an ambiguity we will come back to. Output:

```text
# file: /srv/atelier/notes.md
# owner: root
# group: root
user::rw-
user:bruno:r--
group::r--
mask::r--
other::---
```

`ls -l` signals the presence of an ACL with a trailing `+`:

```text
-rw-r-----+ 1 root root 27 Jul 22 12:01 /srv/atelier/notes.md
```

And yet, `bruno` still reads nothing:

```bash
sudo -u bruno cat /srv/atelier/notes.md
# cat: /srv/atelier/notes.md: Permission denied
```

This is the trap the theory forgets: an ACL on a file gives no right on the
**path** that leads to it. To open a file, you need the `x` (traversal) right on
**each** directory of the path. Here `/srv/atelier` is in `0750 root:root`:
`bruno` cannot even enter.

### Open the path with a group ACL on the directory

```bash
sudo usermod -aG relecteurs bruno
sudo setfacl -m g:relecteurs:rwx /srv/atelier
sudo getfacl -p /srv/atelier
```

```text
# file: /srv/atelier
# owner: root
# group: root
user::rwx
group::r-x
group:relecteurs:rwx
mask::rwx
other::---
```

This time the read goes through:

```bash
sudo -u bruno cat /srv/atelier/notes.md
# compte rendu de la reunion
id bruno
# uid=1003(bruno) gid=1004(bruno) groups=1004(bruno),1005(relecteurs)
```

`sudo -u bruno` starts a new process, whose group list is re-read at that
moment: the addition is therefore taken into account straight away. A process
already running, on the other hand, keeps the groups it had when it started,
hence the reflex of logging back in after a `usermod -aG` when the test is done
from an open session.

### The mask: a ceiling that a plain `chmod` moves

Let us give `bruno` write access, and check that he really writes:

```bash
sudo setfacl -m u:bruno:rw /srv/atelier/notes.md
sudo -u bruno sh -c 'echo ligne-ajoutee >> /srv/atelier/notes.md'   # OK
```

Now, the classic accident: someone "tidies up" the file permissions.

```bash
sudo chmod g=r /srv/atelier/notes.md
sudo getfacl -p /srv/atelier/notes.md
```

```text
user::rw-
user:bruno:rw-	#effective:r--
group::r--
mask::r--
other::---
```

```bash
sudo -u bruno sh -c 'echo deuxieme-ligne >> /srv/atelier/notes.md'
# sh: line 1: /srv/atelier/notes.md: Permission denied
```

`bruno`'s entry has not moved, it still displays `rw-`. It is the **mask** that
dropped to `r--`, and the mask is a **ceiling** applied to all named entries
(`user:<name>:`, `group:<name>:`) as well as to the owning group. The
`#effective:` column gives the permission actually obtained. On an ACL-bearing
file, `chmod g=…` does not touch the owning group: it rewrites the mask.

You raise it explicitly:

```bash
sudo setfacl -m m::rw /srv/atelier/notes.md
```

A corollary to know: **`ls -l` displays the mask, not `group::`**. After the
repair, `getfacl` says `group::r--` while `ls -l` displays:

```text
-rw-rw----+ 1 root root 57 Jul 22 12:01 /srv/atelier/notes.md
```

The `rw` in the middle is the mask. As soon as there is a `+`, stop reading the
group permissions in `ls -l`: read `getfacl`.

### The default ACL, so that new files inherit

A default ACL gives no right on the directory itself: it is a **template**
copied into everything that will be created inside it afterwards.

```bash
sudo setfacl -d -m g:relecteurs:rw /srv/atelier
sudo getfacl -p /srv/atelier
```

```text
user::rwx
group::r-x
group:relecteurs:rwx
mask::rwx
other::---
default:user::rwx
default:group::r-x
default:group:relecteurs:rw-
default:mask::rwx
default:other::---
```

A single entry asked for, five `default:` lines created: a set of default ACLs
must be complete, the kernel fills in the mandatory entries from the ugo
permissions of the directory. `-d -m g:…` and `-m d:g:…` are two ways of writing
the same thing.

Let us check the inheritance on a brand new file, then on a subdirectory:

```bash
sudo touch /srv/atelier/herite.txt
sudo getfacl -p /srv/atelier/herite.txt
```

```text
user::rw-
group::r-x	#effective:r--
group:relecteurs:rw-
mask::rw-
other::---
```

The `relecteurs` entry is indeed there. Note in passing an `#effective:` on an
entry nobody set by hand: `group::` inherited `r-x`, capped by a `rw-` mask
computed at creation time. An `#effective:` is therefore not always the sign of
a mistake.

```bash
sudo mkdir /srv/atelier/sous-dossier
sudo getfacl -p /srv/atelier/sous-dossier
```

A subdirectory inherits both sets at once: the access ACL **and** the default
ACL, which therefore propagates step by step.

Two limits to remember:

```bash
sudo setfacl -d -m g:relecteurs:r /srv/atelier/notes.md
# setfacl: /srv/atelier/notes.md: Only directories can have default ACLs
```

And above all: a default ACL applies **only to the future**. Files already
present do not move. To catch up with the existing ones, a recursive pass is
needed:

```bash
sudo setfacl -R -m u:bruno:rX /srv/atelier
```

The **uppercase** `X` grants `x` only on directories and on files that already
have it. On the demonstration tree, the same command gives `user:bruno:r-x` to
the directory, `user:bruno:r--` to `notes.md` and `user:bruno:r-x` to the
subdirectory. With a lowercase `x`, all the files would have become executable.

### Remove, audit, back up

```bash
sudo setfacl -x u:bruno /srv/atelier/notes.md   # one named entry
sudo setfacl -k /srv/atelier                    # the default ACLs only
sudo setfacl -b /srv/atelier                    # everything, back to ugo permissions
```

After `setfacl -b`, `getfacl` only shows `user::`, `group::` and `other::`, and
the `+` disappears from `ls -l`. Careful: removing an entry with `-x`
recalculates the mask, which often goes back down. Check the remaining entries.

For the audit, list the named entries only across a whole tree, default entries
included:

```bash
sudo getfacl -pR /srv/atelier 2>/dev/null | grep -E '^(default:)?(user|group):[^:]+:'
```

The pattern discards `user::`, `group::`, `mask::` and `other::`, which are only
the translation of the ugo permissions, and keeps only what has been granted by
name.

For the backup, `-p` is not a detail:

```bash
sudo sh -c 'getfacl -pR /srv/atelier > /root/acl-atelier.bak'
sudo setfacl --restore=/root/acl-atelier.bak
```

Without `-p`, `getfacl` warns (`Removing leading '/' from absolute path names`)
and writes `# file: srv/atelier`. The restore then becomes relative to the
current directory, and from anywhere other than `/` it fails:

```text
setfacl: srv/atelier: No such file or directory
```

One last point of vigilance, copying: `cp` without options loses the ACLs
silently (no more `+` on the copy), `cp -a` keeps them. Same logic with `rsync`,
which needs `-A`.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `command -v setfacl` returns nothing | the `acl` package is not installed |
| `setfacl: Option -m: Invalid argument near character 3` | the named user or group does not exist |
| `Only directories can have default ACLs` | `-d` (or `d:`) applied to a file |
| `Permission denied` although the file ACL is right | the `x` right is missing on a directory of the path |
| `Permission denied` and an entry marked `#effective:` | the mask is capping; raise it with `setfacl -m m::rw <path>` |
| The permissions changed without the ACL being touched | a `chmod` went through and rewrote the mask |
| The new files do not have the expected ACL | no default ACL on the parent directory |
| The files already present do not have the expected ACL | the default ACL only applies to the future, run `setfacl -R -m` |
| `setfacl: srv/…: No such file or directory` on the `--restore` | backup taken without `-p`; move to `/` or redo it with `-p` |
| `Permission denied` with correct ACL and mask | check the MAC layer: `sudo ausearch -m AVC -ts recent` (SELinux is `Enforcing` on this VM) |

To undo everything and start over:

```bash
sudo rm -rf /srv/atelier
sudo userdel -r bruno
sudo groupdel relecteurs
```
