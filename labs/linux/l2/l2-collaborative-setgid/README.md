# Lab — collaborative directory with set-GID

## Reminder

[**Permissions & ownership on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/)

On a directory, the **set-GID** bit (`chmod g+s`, or the leading `2` of a
four-digit octal mode) makes new files inherit the directory's group. Combined
with the right group and `g+w`, that is a collaborative folder: the guide makes
it the natural companion of a well-tuned UMASK, because it is what makes group
work on a shared directory actually functional. `ls -ld` shows an `s` in place
of the group execute bit.

## The course

The examples below work on `/srv/chantier`, a demonstration directory, with the
`redaction` group and the `nadia` and `pierre` accounts: the challenge will ask
you for another path, another group and other accounts. The goal is to learn the
method, not to copy a line.

### The demonstration setup

```bash
sudo groupadd redaction
sudo useradd -m -G redaction nadia
sudo useradd -m -G redaction pierre
sudo mkdir -p /srv/chantier
sudo chown root:root /srv/chantier
sudo chmod 0755 /srv/chantier
```

Before touching the permissions, look at what you have:

```bash
ls -ld /srv/chantier
stat -c '%n %a %U:%G' /srv/chantier
id nadia
```

```text
drwxr-xr-x. 2 root root 6 Jul 22 12:20 /srv/chantier
/srv/chantier 755 root:root
uid=1005(nadia) gid=1008(nadia) groups=1008(nadia),1007(redaction)
```

Two things to read in the `id` output: `nadia` has a **primary group** named
after her (`gid=1008(nadia)`), and `redaction` is only a **secondary** group.
That is where the whole problem below comes from.

The trailing dot in `drwxr-xr-x.` has nothing to do with permissions: it signals
a SELinux context, active on this VM (`getenforce` answers `Enforcing`).

### The problem: every file keeps its author's group

Give the directory the right group and write access for the group, but
**without** the set-GID bit:

```bash
sudo chgrp redaction /srv/chantier
sudo chmod 0770 /srv/chantier
ls -ld /srv/chantier
```

```text
drwxrwx---. 2 root redaction 6 Jul 22 12:20 /srv/chantier
```

The directory is in the right group, both accounts can write in it. And yet
collaboration does not work:

```bash
sudo -u nadia touch /srv/chantier/plan.md
sudo ls -l /srv/chantier/plan.md
```

```text
-rw-r--r--. 1 nadia nadia 0 Jul 22 12:20 /srv/chantier/plan.md
```

The file was born with the **`nadia`** group, not `redaction`: by default, a new
file takes the **primary group of its creator**. The consequence is immediate:

```bash
sudo -u pierre sh -c 'echo revision >> /srv/chantier/plan.md'
```

```text
sh: line 1: /srv/chantier/plan.md: Permission denied
```

`pierre` is a member of `redaction`, but the file does not belong to
`redaction`. A shared folder where nobody can pick up someone else's work is not
a collaborative folder.

Note in passing that on a directory in `0770`, your own administration account
is not a member of the group: a plain `ls -l /srv/chantier` fails with
`Permission denied`. You have to type `sudo ls -l`, otherwise you wrongly
believe the directory is broken.

### Setting the set-GID bit

```bash
sudo chmod g+s /srv/chantier
sudo ls -ld /srv/chantier
sudo stat -c '%a' /srv/chantier
```

```text
drwxrws---. 2 root redaction 21 Jul 22 12:20 /srv/chantier
2770
```

The group `x` became an **`s`**, and the octal mode gained a leading digit:
`770` became `2770`. The two notations are equivalent:

```bash
sudo chmod g+s /srv/chantier      # symbolic
sudo chmod 2770 /srv/chantier     # octal, the leading 2 is the set-GID
```

The new file then inherits the directory's group:

```bash
sudo -u nadia touch /srv/chantier/note.md
sudo ls -l /srv/chantier
```

```text
-rw-r--r--. 1 nadia redaction 0 Jul 22 12:20 note.md
-rw-r--r--. 1 nadia nadia     0 Jul 22 12:20 plan.md
```

`note.md`, created after the bit was set, is in the `redaction` group.
`plan.md`, created before, did not move: we will come back to it.

### The lowercase `s`, and the uppercase `S` that betrays a mistake

The set-GID bit is displayed in place of the group `x`. If that `x` does not
exist, `ls` reports it with an **uppercase letter**:

```bash
sudo chmod g-x /srv/chantier
sudo stat -c '%a %A' /srv/chantier
```

```text
2760 drwxrwS---
```

The bit is indeed set (the `2` is there), but the group can no longer
**traverse** the directory: nobody will enter it, so the inheritance will never
be used. An uppercase `S` is almost always the sign of a forgotten `g+x`.

```bash
sudo chmod g+x /srv/chantier
sudo stat -c '%a %A' /srv/chantier
```

```text
2770 drwxrws---
```

### The numeric `chmod` trap

On a **directory**, `chmod` does not remove the set-GID when you give it an
ordinary numeric mode, even a four-digit one:

```bash
sudo chmod g+s /srv/chantier  ; sudo stat -c '%a %A' /srv/chantier
sudo chmod 755 /srv/chantier  ; sudo stat -c '%a %A' /srv/chantier
sudo chmod 0755 /srv/chantier ; sudo stat -c '%a %A' /srv/chantier
```

```text
2755 drwxr-sr-x
2755 drwxr-sr-x
2755 drwxr-sr-x
```

The bit survives both "resets". This is not an accident, it is documented in
`man chmod`, section *SETUID AND SETGID BITS*:

> For directories chmod preserves set-user-ID and set-group-ID bits unless you
> explicitly specify otherwise. You can set or clear the bits with symbolic
> modes like u+s and g-s. To clear these bits for directories with a numeric
> mode requires an additional leading zero like 00755, leading minus like
> -6000, or leading equals like =755.

The three announced forms do work, as checked:

```bash
sudo chmod g-s /srv/chantier   ; sudo stat -c '%a %A' /srv/chantier   # 755 drwxr-xr-x
sudo chmod 00755 /srv/chantier ; sudo stat -c '%a %A' /srv/chantier   # 755 drwxr-xr-x
sudo chmod =755 /srv/chantier  ; sudo stat -c '%a %A' /srv/chantier   # 755 drwxr-xr-x
```

Remember the **`g-s`** reflex to remove a set-GID. And if an audit reports a
directory still set-GID after a numeric `chmod`, it is not the audit that is
wrong.

### Inheriting the group is not enough: the UMASK

Put the directory back to `2770` and look at the file inherited earlier. It is
in the `redaction` group, and yet:

```bash
sudo -u pierre sh -c 'echo revision >> /srv/chantier/note.md'
```

```text
sh: line 1: /srv/chantier/note.md: Permission denied
```

The reason is in the file mode, `-rw-r--r--`: the group **reads** it but does
not **write** it. The set-GID gives the right group, it gives no permission. The
permissions of a new file come from the **UMASK** of its creator, which the
guide describes as "defining the permissions removed from new files" and which
is **022** by default:

```bash
sudo -u nadia sh -c 'umask'
```

```text
0022
```

`022` removes write access for the group, hence the `-rw-r--r--`. With a UMASK
that removes nothing from the group, the file is born usable by two people:

```bash
sudo -u nadia sh -c 'umask 007; touch /srv/chantier/agenda.md'
sudo ls -l /srv/chantier/agenda.md
sudo -u pierre sh -c 'echo revision >> /srv/chantier/agenda.md'
sudo ls -l /srv/chantier/agenda.md
```

```text
-rw-rw----. 1 nadia redaction 0 Jul 22 12:20 /srv/chantier/agenda.md
-rw-rw----. 1 nadia redaction 9 Jul 22 12:20 /srv/chantier/agenda.md
```

This time `pierre` writes: the file grew. `007` removes everything from
"others" and removes nothing from the group. `002` does the same while leaving
read access to everyone, which shows in the resulting mode:

```bash
sudo -u nadia sh -c 'umask 002; touch /srv/chantier/essai-002.md'
sudo ls -l /srv/chantier/essai-002.md
```

```text
-rw-rw-r--. 1 nadia redaction 0 Jul 22 12:23 /srv/chantier/essai-002.md
```

> **Beware of `027`, the hardening value recommended by the guide.** The guide
> describes it as "nothing for others, read for the group", and that is exactly
> what it does:
>
> ```bash
> sudo -u nadia sh -c 'umask 027; touch /srv/chantier/essai-027.md'
> sudo ls -l /srv/chantier/essai-027.md
> sudo -u pierre sh -c 'echo x >> /srv/chantier/essai-027.md'
> ```
>
> ```text
> -rw-r-----. 1 nadia redaction 0 Jul 22 12:20 /srv/chantier/essai-027.md
> sh: line 1: /srv/chantier/essai-027.md: Permission denied
> ```
>
> Under `027`, the group **reads** and does not modify. For a directory where
> people co-edit, you need `007` (or `002`). Global hardening and the need of a
> service are therefore settled in two different places, not one against the
> other.

A `umask` typed in a shell disappears with it. The guide indicates where to make
it persistent: `/etc/login.defs` (used by `useradd` and `pam_umask`) and a
dedicated file in `/etc/profile.d/` for interactive shells. The effect of the
second can be checked straight away, in a login shell:

```bash
sudo -u nadia bash -lc 'umask'                                    # 0022
echo 'umask 007' | sudo tee /etc/profile.d/99-chantier-demo.sh
sudo -u nadia bash -lc 'umask'                                    # 0007
sudo rm -f /etc/profile.d/99-chantier-demo.sh
sudo -u nadia bash -lc 'umask'                                    # 0022
```

Measure the reach of the gesture before making it: a file dropped in
`/etc/profile.d/` applies to **every** account that opens a login shell, not
only to the members of the group.

### Subdirectories inherit the bit too

This is what makes the setup durable: the set-GID propagates step by step,
without having to go back over each creation.

```bash
sudo -u nadia sh -c 'umask 007; mkdir /srv/chantier/brouillons'
sudo stat -c '%n %a %A %U:%G' /srv/chantier/brouillons
```

```text
/srv/chantier/brouillons 2770 drwxrws--- nadia:redaction
```

The subdirectory inherited the group **and** the set-GID bit itself. Whatever is
created inside it will inherit in turn.

### Catching up with what already existed

Inheritance only applies to the future. Earlier files keep their group, and you
have to go and get them:

```bash
sudo chgrp -R redaction /srv/chantier
sudo chmod -R g+w /srv/chantier
sudo ls -l /srv/chantier
```

```text
-rw-rw----. 1 nadia redaction 9 Jul 22 12:20 agenda.md
-rw-rw----. 1 nadia redaction 0 Jul 22 12:20 essai-027.md
-rw-rw-r--. 1 nadia redaction 0 Jul 22 12:20 note.md
-rw-rw-r--. 1 nadia redaction 0 Jul 22 12:20 plan.md
```

(excerpt: only the regular files are shown here.)

You really need **both** commands: `chgrp -R` alone fixes the group and leaves
the files in `-rw-r--r--`, so still closed to group writes.

And use the symbolic mode. A `chmod -R 770` on the same tree gives this:

```bash
sudo chmod -R 770 /srv/chantier
sudo ls -l /srv/chantier
sudo stat -c '%n %a %A' /srv/chantier /srv/chantier/brouillons
```

```text
-rwxrwx---. 1 nadia redaction 9 Jul 22 12:20 agenda.md
drwxrws---. 2 nadia redaction 6 Jul 22 12:20 brouillons
-rwxrwx---. 1 nadia redaction 0 Jul 22 12:23 essai-002.md
...
/srv/chantier 2770 drwxrws---
/srv/chantier/brouillons 2770 drwxrws---
```

Every regular file became **executable**, which nobody asked for, while the
set-GID of the directories survived, as seen above. The recursive numeric form
therefore gives the exact opposite of what you expect from it.

### `cp` inherits, `mv` does not

The most expensive trap in production: moving a file into the directory does
**not** change its group.

```bash
sudo -u nadia sh -c 'umask 007; touch /home/nadia/source-a.md /home/nadia/source-b.md'
sudo -u nadia cp /home/nadia/source-a.md /srv/chantier/copie.md
sudo -u nadia mv /home/nadia/source-b.md /srv/chantier/deplace.md
sudo ls -l /srv/chantier/copie.md /srv/chantier/deplace.md
```

```text
-rw-r-----. 1 nadia redaction 0 Jul 22 12:21 /srv/chantier/copie.md
-rw-rw----. 1 nadia nadia     0 Jul 22 12:21 /srv/chantier/deplace.md
```

`cp` **creates** a file in the directory: the set-GID applies, and so does the
UMASK of the moment (hence the `-rw-r-----`, the UMASK being `022` in that
shell). `mv` inside the same file system creates nothing, it renames: the file
arrives with its original group, `nadia`, and nobody else will be able to pick
it up.

Same result with `cp -p`, which explicitly **preserves** ownership:

```bash
sudo -u nadia sh -c 'umask 007; touch /home/nadia/source-c.md'
sudo -u nadia cp -p /home/nadia/source-c.md /srv/chantier/copie-p.md
sudo ls -l /srv/chantier/copie-p.md
```

```text
-rw-rw----. 1 nadia nadia 0 Jul 22 12:21 /srv/chantier/copie-p.md
```

After a `mv` or a `cp -p` into a collaborative directory, run a `chgrp` again.

The `root` account does not escape the rule either: a file it creates in the
directory inherits the group like any other.

```bash
sudo touch /srv/chantier/rapport-root.md
sudo ls -l /srv/chantier/rapport-root.md
```

```text
-rw-r--r--. 1 root redaction 0 Jul 22 12:21 /srv/chantier/rapport-root.md
```

### Preventing cross deletions: the sticky bit

A directory writable by the group lets every member delete other people's
files, including those they cannot modify:

```bash
sudo -u pierre rm /srv/chantier/note.md      # goes through without a complaint
```

Deleting a file is a write permission on the **directory**, not on the file. The
guide covers this case for writable directories and gives the remedy, the
**sticky bit** (`chmod a+t`, or the leading `1`), which it illustrates with
`/tmp` and `/var/tmp` in `1777`, checked here:

```bash
ls -ld /tmp /var/tmp
```

```text
drwxrwxrwt.  9 root root 4096 Jul 22 12:20 /tmp
drwxrwxrwt. 10 root root 4096 Jul 22 12:20 /var/tmp
```

It combines with the set-GID without any difficulty:

```bash
sudo chmod +t /srv/chantier
sudo stat -c '%a %A' /srv/chantier
sudo -u pierre rm /srv/chantier/plan.md
```

```text
3770 drwxrws--T
rm: cannot remove '/srv/chantier/plan.md': Operation not permitted
```

The mode moved to `3770`: `2` for the set-GID, plus `1` for the sticky bit.
`man chmod` calls the latter the *restricted deletion flag* and defines it as
follows: it prevents unprivileged users from removing or renaming a file in the
directory unless they own the file or the directory. Everybody therefore stays
in charge of their own files:

```bash
sudo -u pierre sh -c 'umask 007; touch /srv/chantier/relecture.md'
sudo -u pierre rm /srv/chantier/relecture.md      # goes through: it is his own file
```

The **uppercase** `T` in `drwxrws--T` obeys the same rule as the `S`: the sticky
bit is displayed in place of the `x` of "others", and it is uppercase because
here "others" do not have that `x`. On `/tmp`, open to everyone, it is a
lowercase `t`.

One last detail, consistent with what we saw about numeric `chmod`: run the
`chmod -R 770` seen above on this directory now in `3770`, and the mode falls
back to `2770`. The sticky bit is indeed **cleared** by a numeric mode, where
the set-GID survives. The two bits are not treated the same way.

### Taking inventory of the bits that are set

The guide gives the search for setuid and setgid binaries, to be compared to a
reference list:

```bash
sudo find / -xdev -type f \( -perm -4000 -o -perm -2000 \) | sort
```

On this AlmaLinux 10 VM, it returns a short and legitimate list:

```text
/usr/bin/chage
/usr/bin/chfn
/usr/bin/chsh
/usr/bin/crontab
/usr/bin/gpasswd
/usr/bin/mount
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/pkexec
/usr/bin/su
/usr/bin/sudo
/usr/bin/umount
/usr/bin/write
/usr/lib/polkit-1/polkit-agent-helper-1
/usr/libexec/utempter/utempter
/usr/sbin/grub2-set-bootflag
/usr/sbin/mount.nfs
/usr/sbin/pam_timestamp_check
/usr/sbin/unix_chkpwd
```

Do not confuse the two uses of the same bit: this command targets `-type f`, so
**executables**, where the setgid runs the program with the privileges of its
group. It will never see your collaborative directories. For those, it is
`-type d`:

```bash
sudo find /srv -xdev -type d -perm -2000
```

```text
/srv/chantier
/srv/chantier/brouillons
```

One bit, two meanings: on an executable, it is a privilege escalation to watch;
on a directory, a simple group inheritance. The guide reminds you that you never
remove a setuid or setgid bit in bulk: you inventory, you document, you compare
to a reference list.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| New files are not in the right group | the set-GID bit is not set on the directory, or it was set after they were created |
| `ls -ld` shows an uppercase `S` | the group does not have the `x` permission on the directory: `chmod g+x` |
| The set-GID bit is still there after a `chmod 0755` | on a directory, a numeric `chmod` preserves it: use `g-s`, `00755` or `=755` |
| The group is right but a member gets `Permission denied` on write | the creator's UMASK removed `g+w`: `022` and `027` remove it, `007` and `002` do not |
| A file that arrived through `mv` keeps its old group | `mv` renames, it does not create: the set-GID does not apply. Same with `cp -p` |
| Older files did not change group | inheritance only applies to the future: `chgrp -R`, then `chmod -R g+w` |
| Every file became executable | a numeric `chmod -R` went through: use the symbolic form |
| A member deletes other people's files | that is a write permission on the directory: set the sticky bit (`chmod +t`) |
| `Permission denied` on a plain `ls` of the directory | your account is not a member of the group and the directory is in `0770`: use `sudo` |

To undo everything and start over:

```bash
sudo rm -rf /srv/chantier
sudo userdel -r nadia
sudo userdel -r pierre
sudo groupdel redaction
sudo rm -f /etc/profile.d/99-chantier-demo.sh
```

The last `rm` is not a detail: a file left in `/etc/profile.d/` keeps changing
the UMASK of **every** account on the machine, long after the demonstration
directory has disappeared.
