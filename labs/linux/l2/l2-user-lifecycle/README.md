# Lab — create a local account

## Reminder

[**Users & groups on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`useradd -u <uid> -m -d <home> -s <shell> -g <primary> -G <supplementary> <name>`
creates an account with a full identity. A user has **one single primary group**
(`-g`) and any number of **supplementary groups** (`-G`). Later,
`usermod -aG <group> <user>` appends a group: the `-a` is vital, without it you
replace all supplementary groups. `id` and `getent passwd` inspect the result.

## The course

The examples below create the accounts `lucien` and `hector` in the groups
`bureau`, `archives` and `impression`: the challenge will ask you for another
account, another UID and other groups. The point is to learn the method and to
know how to check it, not to copy a line.

Every output on this page was produced on an **AlmaLinux 10** VM. On Debian and
Ubuntu, a few paths and a few defaults differ: they are pointed out along the
way.

### Where `useradd` default values come from

`useradd` decides almost nothing on its own. It reads two files. The first is
**`/etc/default/useradd`**, which `useradd -D` merely reads back:

```bash
sudo useradd -D
```

```plaintext
HOME=/home
SHELL=/bin/bash
SKEL=/etc/skel
CREATE_MAIL_SPOOL=yes
[...]
```

The rest of the policy lives in **`/etc/login.defs`**:

```bash
grep -E '^(UID_MIN|UID_MAX|HOME_MODE|UMASK|USERGROUPS_ENAB|CREATE_HOME)' /etc/login.defs
```

```plaintext
UMASK		022
HOME_MODE	0700
UID_MIN                  1000
UID_MAX                 60000
USERGROUPS_ENAB yes
CREATE_HOME	yes
```

Four lines to remember:

- **`UID_MIN 1000`**: this is the border between system accounts and human
  accounts. A UID chosen by hand must stay above it, otherwise the account gets
  mixed in with the service accounts.
- **`HOME_MODE 0700`**: the mode of the home directory created.
- **`USERGROUPS_ENAB yes`**: `useradd` creates a **private group with the same
  name** as the account, unless you impose a primary group with `-g`.
- **`CREATE_HOME yes`**: see just below, it is a trap.

> **On AlmaLinux 10, `-m` changes nothing.** The online guide says that `useradd`
> alone does not create the home directory. That is not true here: with
> `CREATE_HOME yes` in `/etc/login.defs`, `sudo useradd lucien` with no option at
> all already produces `/home/lucien` populated from `/etc/skel`. Do not rely on
> that default though: it is not the same everywhere, and a statement asking you
> for a created home expects the explicit `-m` from you.

`/etc/skel` is the template copied into every new home; `ls -A /etc/skel` shows
`.bash_logout`, `.bash_profile` and `.bashrc` here. A file you drop in it appears
in the home of **every** account created afterwards, and in none of those that
already exist.

### Create an account with imposed attributes

This is the central move. The groups must exist **first**, `useradd` does not
create them:

```bash
sudo groupadd bureau
sudo groupadd archives
sudo useradd -u 2400 -m -d /home/hector -s /bin/bash \
             -g bureau -G archives -c "Hector, poste 42" hector
```

- **`-u`** sets the UID. It must be free, otherwise the command fails.
- **`-m`** creates the home, **`-d`** says which one.
- **`-s`** sets the login shell.
- **`-g`** sets the **primary** group, **`-G`** the list of **supplementary**
  groups.
- **`-c`** fills the comment field, purely descriptive.

Two commands check the result, and they do not say the same thing:

```bash
getent passwd hector
id hector
```

```plaintext
hector:x:2400:1003:Hector, poste 42:/home/hector:/bin/bash
uid=2400(hector) gid=1003(bureau) groups=1003(bureau),1004(archives)
```

`getent passwd` gives the seven fields of `/etc/passwd`: name, the `x` that
points to `/etc/shadow`, UID, **primary GID**, comment, home, shell. It is the
only one of the two that shows the **home** and the **shell**. `id` translates
the numeric identifiers into names and adds the **supplementary groups**, which
`/etc/passwd` knows nothing about.

That split explains a frequent confusion:

```bash
getent group bureau archives
```

```plaintext
bureau:x:1003:
archives:x:1004:hector
```

`bureau` looks empty although it is `hector`'s primary group. That is normal: **a
primary membership is written in `/etc/passwd`** (the 4th field), **a
supplementary membership in `/etc/group`**. Looking for a member in `getent
group` alone will make you miss every account for which it is the primary group.

Two side effects of the `-g`: no group with the same name was created (`getent
group hector` exits with an error), and the home belongs to the account and its
primary group, in `0700` as `HOME_MODE` announced:

```plaintext
$ ls -ld /home/hector
drwx------. 2 hector bureau 62 Jul 22 14:57 /home/hector
```

### `-aG` or `-G`: the most expensive mistake

`usermod -aG` **adds** a supplementary group. Let us make `lucien` a member of
`bureau` and `archives`, then add `impression` **without the `-a`**:

```plaintext
$ sudo usermod -aG archives lucien ; sudo usermod -aG bureau lucien ; id lucien
uid=1002(lucien) gid=1002(lucien) groups=1002(lucien),1003(bureau),1004(archives)
$ sudo usermod -G impression lucien ; id lucien
uid=1002(lucien) gid=1002(lucien) groups=1002(lucien),1005(impression)
```

`bureau` and `archives` are gone. The command displayed **no warning, no error,
no non-zero exit code**: `-G` replaces the whole list with the one you give. The
file confirms the loss:

```bash
grep -E '^(bureau|archives|impression):' /etc/group
```

```plaintext
bureau:x:1003:
archives:x:1004:hector
impression:x:1005:lucien
```

`hector` stayed in `archives`: only the account named by the command was
rewritten. On a real server, the same mistake removes the user from `wheel` (or
`sudo` on Debian) and cuts off their administrator access on the spot.

Two reflexes: record the state with `id` **before** touching the groups, and use
`-G` alone only when you deliberately want to impose the complete list. To remove
a single membership, `gpasswd -d <user> <group>` is safer than recomposing the
list by hand.

> A **session that is already open** keeps the groups it had at login. After an
> addition, the user has to log back in, and the check with `id` is done in the
> **new** session.

### Four ways to make an account unusable

These four states are easily confused, they stack, and they do not block the same
things. They are read in two files only.

**1. No usable password.** This is the state of a new account: the password field
of `/etc/shadow` contains `!` **with no hash behind it**. After
`echo 'lucien:<secret>' | sudo chpasswd`, it carries a real hash:

```plaintext
$ sudo getent shadow lucien ; sudo passwd -S lucien     # new account
lucien:!:20656:0:99999:7:::
lucien L 2026-07-22 0 99999 7 -1
$ sudo getent shadow lucien ; sudo passwd -S lucien     # after chpasswd
lucien:$y$j9T$dAMR20K0L1tMxzejKPxtR/$NfkS8E1[...]:20656:0:99999:7:::
lucien P 2026-07-22 0 99999 7 -1
```

Careful, on the new account `passwd -S` announces `L` although nothing was
locked: there simply never was a password.

**2. Locked password.** `usermod -L` (or `passwd -l`, strictly identical)
prefixes the existing hash with a `!`:

```plaintext
$ sudo usermod -L lucien ; sudo getent shadow lucien
lucien:!$y$j9T$dAMR20K0L1tMxzejKPxtR/$NfkS8E1[...]:20656:0:99999:7:::
```

The hash is **kept**, hence the immediate rollback with `passwd -u`. And this is
where the trap is: locking concerns **only** the password. With a key in
`~/.ssh/authorized_keys`, the connection still goes through. Verified on the VM,
account locked, `passwd -S` showing `L`:

```plaintext
$ ssh -i cle_lucien lucien@atelier.lab 'id -un'
lucien
```

**3. Expired account.** This is the only state that really closes the door. It is
written in the **8th field** of `/etc/shadow`, in days since 1 January 1970:

```plaintext
$ sudo chage -E 1970-01-02 lucien
$ sudo chage -l lucien | grep -i 'account expires'
Account expires						: Jan 02, 1970
$ sudo getent shadow lucien | awk -F: '{print "champ 8 =", $8}'
champ 8 = 1
```

Let us then unlock the password to isolate the effect, leaving the expiry in
place:

```plaintext
$ sudo passwd -u lucien ; sudo passwd -S lucien
lucien P 2026-07-22 0 99999 7 -1
```

`passwd -S` shows `P`, all is well from its point of view. And yet:

```plaintext
$ ssh -i cle_lucien lucien@atelier.lab
Your account has expired; please contact your system administrator.
Connection closed by 10.10.30.14 port 22
```

**An unlocked account can therefore be perfectly unusable.** Remember the
practical consequence: `passwd -S` says nothing about expiry, only `chage -l` is
authoritative. You lift the expiry with `chage -E -1` (field 8 becomes empty
again), or with `usermod --expiredate ""`.

**4. Login shell refusing the session.** Nothing in `/etc/shadow` this time,
everything is in the **7th field of `/etc/passwd`**:

```plaintext
$ sudo usermod -s /sbin/nologin lucien ; getent passwd lucien
lucien:x:1002:1002::/home/lucien:/sbin/nologin
```

The account is neither locked (`P`) nor expired (`never`), and the connection
fails all the same, including for a plain remote command:

```plaintext
$ ssh -i cle_lucien lucien@atelier.lab 'id -un'
This account is currently not available.
```

This is the normal state of a service account, which has no reason to open an
interactive session. On AlmaLinux 10, `/sbin` is a link to `usr/sbin`: the two
paths `/sbin/nologin` and `/usr/sbin/nologin` designate the same binary. On
Debian and Ubuntu, only `/usr/sbin/nologin` exists.

The reading table, all states together:

| What you see | Where | What it blocks |
|---|---|---|
| `!` alone in `/etc/shadow` | field 2 | password never set; SSH key untouched |
| `!` in front of a hash | field 2 | password locked; **SSH key untouched** |
| field 2 **empty** (`passwd -S` = `NP`) | field 2 | nothing at all: login without a password, to be fixed urgently |
| a past date in field 8 | `/etc/shadow` | **everything**, SSH key included |
| `/sbin/nologin` in field 7 | `/etc/passwd` | any session, including `ssh <machine> <command>` |

A deactivation that really holds combines the expiry, the lock and the closing of
sessions already open: `sudo chage -E 0 <user>`, then `sudo passwd -l <user>`,
then `sudo pkill -KILL -u <user>`.

### Delete an account, and what is left afterwards

Record the UID **first**: once the account is gone, the name no longer exists and
you will not be able to search by name.

```bash
id -u hector          # 2400
sudo userdel -r hector
```

`-r` has an exact and narrow scope: the **home directory** and the **local
mailbox**. Check afterwards:

```plaintext
$ grep -c '^hector:' /etc/passwd /etc/group ; sudo grep -c '^hector:' /etc/shadow
/etc/passwd:0
/etc/group:0
0
$ ls -ld /home/hector /var/spool/mail/hector
ls: cannot access '/home/hector': No such file or directory
ls: cannot access '/var/spool/mail/hector': No such file or directory
```

On the other hand, everything the account owned elsewhere stays, with a UID that
no longer matches anybody, displayed as a **raw number**. And searching by name
now fails:

```plaintext
$ ls -l /srv/demo/rapport.txt
-rw-r--r--. 1 2400 bureau 0 Jul 22 14:58 /srv/demo/rapport.txt
$ sudo find /srv -user hector
find: invalid user name or UID argument to -user: ‘hector’
```

Two methods work: the UID recorded beforehand, or `-nouser`, which asks for
nothing.

```bash
sudo find / -xdev -uid 2400 -ls
sudo find / -xdev -nouser -ls
```

The `bureau` group, for its part, survived: `userdel` only deletes the private
group with the same name. A `groupadd` done by hand is undone by hand, and
`groupdel` refuses as long as it is somebody's primary group.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `useradd: UID 2400 is not unique` | the requested UID is already taken; `getent passwd <uid>` says by whom |
| `groupdel: cannot remove the primary group of user '<name>'` | change that primary group first (`usermod -g`) |
| The home does not exist after `useradd` | `CREATE_HOME` is at `no` and you forgot the `-m` |
| `getent group <g>` does not show a member you just added | it is their **primary** group: it is in `/etc/passwd`, not in `/etc/group` |
| The new group has no effect | the session predates the addition; log out, log in, then `id` |
| The user lost all their supplementary groups | `usermod -G` was typed without `-a`; nothing warns you, only `id` shows it |
| A locked account still logs in | locking only acts on the password; you have to expire the account |
| `passwd -S` says `P` but the login is refused | account expired, or `nologin` shell; look at `chage -l` and `getent passwd` |
| `ls -l` shows a number instead of a name | orphan file; `sudo find / -xdev -nouser -ls` |
