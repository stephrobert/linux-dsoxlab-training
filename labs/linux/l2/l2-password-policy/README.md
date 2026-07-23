# Lab — password aging & complexity

## Reminder

[**Users & groups on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`chage -M <max> -m <min> -W <warn> <user>` sets per-account aging (`chage -l`
shows it). `/etc/login.defs` holds `PASS_MAX_DAYS` and friends — the defaults
applied to newly created accounts. `/etc/security/pwquality.conf` enforces
complexity, e.g. `minlen` for the minimum length.

## The course

The examples below work on two demonstration accounts, `pwd-demo-lea` and
`pwd-demo-tom`, with different delays and different lengths from those of the
challenge: the challenge will ask you for another account and other values. The
point is to learn the method, not to copy a line.

All the outputs on this page were taken on an AlmaLinux 10.2 VM.

### Three settings, three places, three scopes

This is the point that costs the most when you mix them up:

| What you set | Where | Who it acts on |
|---|---|---|
| the aging of one specific account | `chage`, which writes into `/etc/shadow` | that account, immediately |
| the default aging | `/etc/login.defs` | accounts created **afterwards**, never the existing ones |
| the quality required of a password | `/etc/security/pwquality.conf` | every password entry, right away |

Hardening `/etc/login.defs` therefore touches **no** account already present,
and `chage` on one account changes nothing for the next ones. You need both.

### The demonstration setup

```bash
sudo useradd -m -s /bin/bash pwd-demo-lea
id pwd-demo-lea
```

```text
uid=1005(pwd-demo-lea) gid=1007(pwd-demo-lea) groups=1007(pwd-demo-lea)
```

Before setting anything, look at what the account received at birth:

```bash
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: never
Password inactive					: never
Account expires						: never
Minimum number of days between password change		: 0
Maximum number of days between password change		: 99999
Number of days of warning before password expires	: 7
```

`99999` days, about 273 years: that is the way to say "never". These values do
not come out of nowhere, they were copied from `/etc/login.defs` at `useradd`
time; we come back to it below.

The labels of `chage -l` are translatable strings, and a script that parses them
breaks as soon as the machine changes language. On this VM the question does not
arise (`locale -a | grep '^fr'` returns nothing, no French locale is installed,
and the output stays in English even with `LC_ALL=fr_FR.UTF-8`), but take up the
reflex that works everywhere: `sudo LC_ALL=C chage -l pwd-demo-lea`.

A brand new account does not have a usable password yet. The guide says so, and
`/etc/shadow` confirms it: the field contains a `!`.

```bash
sudo passwd -S pwd-demo-lea
sudo awk -F: '$1=="pwd-demo-lea" {print $1" : ["$2"]"}' /etc/shadow
```

```text
pwd-demo-lea L 2026-07-22 0 99999 7 -1
pwd-demo-lea : [!]
```

### Setting a policy on an account: `chage -M`, `-m`, `-W`

The three options are set with a single command:

```bash
sudo chage -M 45 -m 3 -W 10 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: Sep 05, 2026
Password inactive					: never
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

- **`-M`** (maximum): the password must be changed after that many days. The
  `Password expires` line is not a value you enter: it is **computed**, it is the
  date of the last change plus the maximum. Here Jul 22 + 45 days gives Sep 05.
- **`-m`** (minimum): the delay during which the person can **not** change their
  password a second time. It prevents working around a history by chaining
  changes to come back to the old password.
- **`-W`** (warning): number of warning days before the deadline.

These three settings live in `/etc/shadow`, in fields 4, 5 and 6:

```bash
sudo awk -F: '$1=="pwd-demo-lea"' /etc/shadow
```

```text
pwd-demo-lea:!:20656:3:45:10:::
```

The third field (`20656`) is the date of the last change, counted in **days
since 1 January 1970**. That is the number `chage -l` translates into a readable
date, and you can do the conversion yourself:

```bash
date -u -d "@$((20656*86400))" +%F
```

```text
2026-07-22
```

Never edit this line by hand: the guide recalls that one character out of place
in `/etc/shadow` can prevent any login, including root's, and that the tools
(`chage`, `usermod`, `passwd`) take a lock before writing.

### What `-m` really prevents

Let us give the account a password, then look at what happens if the person
wants to change it right away from their own session.

```bash
sudo passwd pwd-demo-lea
sudo passwd -S pwd-demo-lea
```

```text
New password: Retype new password: passwd: password updated successfully
pwd-demo-lea P 2026-07-22 3 45 10 -1
```

The second field went from `L` to `P`: there is now a usable password. The
attempt at an immediate change, on the other hand, is refused:

```bash
passwd                                     # in pwd-demo-lea's session
```

```text
Current password: New password: You must wait longer to change your password.
passwd: Authentication token manipulation error
passwd: password unchanged
```

`root`, on the other hand, is not subject to the minimum delay: the same
operation run with `sudo passwd pwd-demo-lea` goes through without a hitch.

```text
New password: Retype new password: passwd: password updated successfully
```

Remember the practical consequence: a high `-m` is not a wall, it is a nuisance
for the user and a non-constraint for the administrator. If you have to let
somebody change their password despite the delay, temporarily set the minimum
back to zero (`sudo chage -m 0 <account>`) rather than asking them to wait.

### The two fields people forget: `-I` and `-E`

`chage -l` shows seven lines, and the challenge covers only three of them. The
two other settings are worth knowing, if only so as not to mix them up with the
first ones.

**`-I` (inactive)** adds a delay **after** the password has expired. Its manual
defines it this way: *"Set the number of days of inactivity after a password has
expired before the account is locked"*, and states that once the account is
locked, the person must contact the administrator to get access back. So it is a
reprieve, not a warning.

```bash
sudo chage -I 5 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: Sep 05, 2026
Password inactive					: Sep 10, 2026
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

`Password inactive` is here again **computed**: Sep 05 plus 5 days.

**`-E` (expire)** closes the **account**, which has nothing to do with the
expiry of the password:

```bash
sudo chage -E 2026-11-30 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: Sep 05, 2026
Password inactive					: Sep 10, 2026
Account expires						: Nov 30, 2026
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

> **`Password expires` and `Account expires` are two different things.**
> An expired password is repaired by entering a new one. An expired account
> refuses **all** logins, including by SSH key: it is the only way, says the
> guide, to really cut an access off, where a `passwd -l` leaves the SSH key
> working. It is also the gesture that belongs in an offboarding checklist, not
> in an aging policy.

The value `-1` sets those two fields back to `never`:

```bash
sudo chage -I -1 -E -1 pwd-demo-lea
```

### A password that is already too old

Setting a `-M` on an account whose password is old does not push anything back:
the deadline is computed from the **last change**, and it can therefore fall in
the past.

```bash
sudo chage -d 2026-01-10 pwd-demo-lea     # simulates an old password
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jan 10, 2026
Password expires					: Feb 24, 2026
Password inactive					: never
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

That is the expected behaviour: hardening the policy on an existing estate
expires at once every password older than the new maximum. Warn beforehand, or
spread it out with `chage -d`.

The limit case of this mechanism is the gesture recommended by the guide for an
initial password, which must not survive the first session:

```bash
sudo chage -d 0 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: password must be changed
Password expires					: password must be changed
Password inactive					: password must be changed
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

A last-change date set to zero makes the password expired straight away: the
system will ask the person to choose a new one at their next login.

### The system default: `/etc/login.defs`

`chage` handles one account at a time. So that the **next** accounts are born
with the right policy, you set `/etc/login.defs`.

```bash
grep -E '^PASS_(MAX|MIN)_DAYS' /etc/login.defs
```

```text
PASS_MAX_DAYS	99999
PASS_MIN_DAYS	0
```

Three directives make the link with the three options of `chage`:

| `login.defs` directive | Equivalent `chage` option |
|---|---|
| `PASS_MAX_DAYS` | `-M` |
| `PASS_MIN_DAYS` | `-m` |
| `PASS_WARN_AGE` | `-W` |

Back it up before editing, it is a system file read by `useradd`:

```bash
sudo cp -a /etc/login.defs /etc/login.defs.bak
```

After the change, the file announces the new defaults:

```text
PASS_MAX_DAYS	90
PASS_MIN_DAYS	2
```

And this is where the whole section is decided. The **already existing** account
has not moved by a single day:

```bash
sudo chage -l pwd-demo-lea | grep -iE 'minimum|maximum'
```

```text
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
```

Whereas an account created **afterwards** inherits the new values:

```bash
sudo useradd -m pwd-demo-tom
sudo chage -l pwd-demo-tom | grep -iE 'minimum|maximum'
```

```text
Minimum number of days between password change		: 2
Maximum number of days between password change		: 90
```

Better: put `/etc/login.defs` back in its original state, and `pwd-demo-tom`
keeps `2` and `90`. These values are not re-read at every login, they were
**carved into `/etc/shadow`** at `useradd` time. The manual is clear on this
point:

```bash
man login.defs
```

```text
PASS_MAX_DAYS, PASS_MIN_DAYS and PASS_WARN_AGE are only used at the
time of account creation. Any changes to these settings won't affect
existing accounts.
```

> **A policy set only in `login.defs` hardens nothing today.** On a production
> server, all the accounts are already created: they will carry on with their old
> delays until a `chage` loop goes over them. That is exactly the audit finding
> the file was supposed to avoid.

A detail that misleads: `/etc/login.defs` also contains a `PASS_MIN_LEN`
directive, and it is easy to believe that it is the one enforcing the minimum
length. It does not even appear in the manual of the file
(`man login.defs | grep -c PASS_MIN_LEN` returns `0`), and the machine settles
it:

```bash
grep -E '^PASS_MIN_LEN' /etc/login.defs
grep -vE '^\s*#|^\s*$' /etc/security/pwquality.conf
echo 'Zk4-tR9' | pwscore                  # 7 characters, not in the dictionary
```

```text
PASS_MIN_LEN	8
minlen = 6
57
```

A seven-character password is accepted even though `PASS_MIN_LEN` requires
eight, because it is the `minlen` of `pwquality` that decides. The check with
`passwd`, from the account's session, confirms it:

```text
Current password: New password: Retype new password: passwd: password updated successfully
```

So it is `pwquality` that carries the minimum length, the subject of the next
section.

### Complexity: `/etc/security/pwquality.conf`

This file no longer talks about duration but about **content**. It is read by
the `libpwquality` library, itself called by the PAM module `pam_pwquality`:

```bash
grep -n pam_pwquality /etc/pam.d/system-auth /etc/pam.d/password-auth
```

```text
/etc/pam.d/system-auth:13:password    requisite                                    pam_pwquality.so
/etc/pam.d/password-auth:13:password    requisite                                    pam_pwquality.so
```

The `requisite` keyword matters. `man pam.conf` defines it this way: if the
module fails, *"control is directly returned to the application"*, without
running the rest of the stack. A password refused by `pwquality` therefore never
reaches `/etc/shadow`.

To test without changing anything, the `pwscore` command (`libpwquality`
package) reads the same configuration and scores a password from 0 to 100:

```bash
echo 'azerty'      | pwscore
echo 'motdepasse'  | pwscore
echo 'Sel-Marin-9' | pwscore
```

```text
Password quality check failed:
 The password fails the dictionary check - it is based on a dictionary word
Password quality check failed:
 The password fails the dictionary check - it is based on a dictionary word
100
```

`minlen` is therefore not the only rule: a dictionary word is rejected whatever
its length. Let us now raise the length requirement to 14, after a backup:

```bash
sudo cp -a /etc/security/pwquality.conf /etc/security/pwquality.conf.bak
sudo sed -i 's/^minlen = .*/minlen = 14/' /etc/security/pwquality.conf
grep -vE '^\s*#|^\s*$' /etc/security/pwquality.conf
```

```text
minlen = 14
```

The same eleven-character password, which used to score 100, is now refused,
while a twenty-one-character password goes through:

```bash
echo 'Sel-Marin-9'           | pwscore
echo 'Mer-Rouge-Profonde-42' | pwscore
```

```text
Password quality check failed:
 The password is shorter than 14 characters
86
```

Two remarks about this score. It is **not** an absolute security mark:
`Sel-Marin-9` was worth 100 with a requirement of 6 and no longer passes with a
requirement of 14. And a lower score (86) can correspond to a much better
password: it is the rule in force that decides, not the number.

The real effect is seen on `passwd`. From the session of the account concerned,
the change is **refused**:

```bash
passwd                                     # in pwd-demo-lea's session
```

```text
Current password: New password: BAD PASSWORD: The password is shorter than 14 characters
passwd: Authentication token manipulation error
passwd: password unchanged
```

Whereas `root` is only **warned**, and still gets the change:

```bash
sudo passwd pwd-demo-lea
```

```text
New password: BAD PASSWORD: The password is shorter than 14 characters
Retype new password: passwd: password updated successfully
```

(The `Current password:` and `New password:` prompts appear here on the same
line because the input was sent through a pipe for the purposes of the capture;
at the keyboard, they are displayed one after the other.)

> **Always check with an unprivileged account.** An administrator who tests
> their policy with `sudo passwd <account>` sees the `BAD PASSWORD` message and
> concludes that the rule applies, whereas the weak password has just been
> accepted. Only the attempt made **by** the user proves that the rule bites.

### The trap of the `pwquality.conf.d` directory

The manual announces a directory of fragments:

```bash
man pwquality.conf
```

```text
The libpwquality library also first reads all *.conf files from the
/etc/security/pwquality.conf.d directory in ASCII sorted order. The
values of the same settings are overridden in the order the files are
parsed.
```

Read the **first** carefully. Unlike the habit taken with systemd or `sysctl.d`,
where the fragment wins over the main file, here the fragments are read
**first** and the main file, parsed afterwards, overwrites what they set. Check,
with `minlen = 6` in the main file and `minlen = 30` in a fragment:

```bash
echo 'minlen = 30' | sudo tee /etc/security/pwquality.conf.d/99-demo.conf
echo 'Mer-Rouge-Profonde-42' | pwscore
```

```text
100
```

The fragment is ignored: 21 characters go through while 30 were required. Let us
comment out the line of the main file, without changing anything else:

```bash
sudo sed -i 's/^minlen = 6$/# minlen = 6/' /etc/security/pwquality.conf
echo 'Mer-Rouge-Profonde-42' | pwscore
```

```text
Password quality check failed:
 The password is shorter than 30 characters
```

So the fragment was indeed read, but was losing the arbitration. Conclusion: a
setting dropped into `pwquality.conf.d/` only takes effect if the same directive
is **absent or commented out** from the main file. An audit that finds a
compliant `minlen` in a fragment and a lax `minlen` in `pwquality.conf` must
conclude that it is the lax one that applies.

### Checking and auditing

Three commands are enough, and they do not say the same thing.

`chage -l <account>` gives the readable detail of one account. A user can run it
on **themselves** without privilege, but not on another:

```bash
chage -l pwd-demo-tom     # from pwd-demo-tom's session
```

```text
Last password change					: Jul 22, 2026
...
```

```bash
chage -l pwd-demo-lea     # from the same session, on another account
chage -M 30 pwd-demo-tom  # any modification, even on yourself
```

```text
chage: Permission denied.
chage: Permission denied.
```

`passwd -S` gives the same information on one line, and `passwd -Sa` gives it
for all the accounts, which makes it the inventory tool:

```bash
sudo passwd -Sa | grep '^pwd-demo'
```

```text
pwd-demo-lea P 2026-07-22 3 45 10 -1
pwd-demo-tom L 2026-07-22 3 45 10 -1
```

The fields, in order: account, password state, date of the last change, minimum,
maximum, warning, inactivity. The state is `P` (usable password), `L` (locked,
or never set) or `NP` (no password, to be fixed urgently).

`passwd -S` says nothing about the expiry of the **account**: the guide insists
on this point, it is `chage -l` that is authoritative to know whether an access
is really closed.

Finally, applying the same policy to several accounts fits in a loop:

```bash
for u in pwd-demo-lea pwd-demo-tom; do
  sudo chage -M 45 -m 3 -W 10 "$u"
done
sudo passwd -Sa | grep '^pwd-demo'
```

```text
pwd-demo-lea P 2026-07-22 3 45 10 -1
pwd-demo-tom L 2026-07-22 3 45 10 -1
```

It is this kind of loop that catches up the existing accounts after a change to
`/etc/login.defs`.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| The existing accounts keep `99999` after editing `login.defs` | normal: the file only serves at creation time. Go over each account again with `chage` |
| `You must wait longer to change your password.` | the minimum delay (`-m`) has not elapsed. `sudo chage -m 0 <account>` lifts it |
| `chage: Permission denied.` | `chage` on another account, or a modification, requires `sudo` |
| `Password expires` does not match the expected computation | the date is computed from `Last password change`, not from the day you set the `-M` |
| The weak password is accepted although `minlen` is set | the test was done as root: root is only warned. Redo the test with the account concerned |
| `minlen` set in `pwquality.conf.d/` has no effect | the main file is parsed after the fragments and wins: comment the directive out in `pwquality.conf` |
| All the passwords expire at once after a `chage -M` | the passwords were older than the new maximum. Spread it out with `chage -d` |
| `passwd -S` shows `P` on an account you believed closed | `passwd -S` ignores the expiry of the account: read `Account expires` in `chage -l` |

To undo everything and start over:

```bash
sudo userdel -r pwd-demo-lea
sudo userdel -r pwd-demo-tom
sudo cp -a /etc/login.defs.bak /etc/login.defs
sudo cp -a /etc/security/pwquality.conf.bak /etc/security/pwquality.conf
sudo rm -f /etc/security/pwquality.conf.d/99-demo.conf
```

These two restorations are not optional. A `minlen` left at a high value will
prevent the next `passwd` on the machine, and a forgotten `PASS_MAX_DAYS` will
be carved into every account created afterwards, long after the demonstration
files have gone. Better check twice:

```bash
grep -E '^PASS_(MAX|MIN)_DAYS' /etc/login.defs
grep -vE '^\s*#|^\s*$' /etc/security/pwquality.conf
```
