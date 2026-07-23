# Lab — delegate limited sudo

## Reminder

[**sudo on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/)

Put sudo policy in `/etc/sudoers.d/` drop-ins (mode `0440`). A rule reads
`who where=(as-whom) commands`; `%group` targets a group, `NOPASSWD:` drops the
password prompt, and listing explicit commands is least privilege. **Always**
validate with `visudo -cf <file>` — a syntax error can break all sudo.
`sudo -l -U <user>` shows the effective policy.

## The course

The examples below delegate backup commands to the `sauvegarde` group and to the
user `nadia`, in the `/etc/sudoers.d/30-sauvegarde` drop-in: the challenge, for
its part, will ask you for another group, another account, another file and
other commands. The point is to learn the method and to know how to prove it,
not to copy a line.

All the output comes from an AlmaLinux 10.2 with `sudo 1.9.17p2`. The hostname
displayed will be your own.

> Before your first change, open a **second SSH session** and leave it open. A
> broken sudoers configuration is repaired from an already authenticated shell,
> not from a terminal that has just lost `sudo`.

### The demonstration setup

```bash
sudo groupadd sauvegarde
sudo useradd -m -G sauvegarde nadia
id nadia
sudo -l -U nadia
```

```text
uid=1002(nadia) gid=1003(nadia) groups=1003(nadia),1002(sauvegarde)
User nadia is not allowed to run sudo on atelier.
```

Belonging to a group gives nothing as long as no rule names that group. Also
take note of what is already in place, so as not to overwrite it:

```bash
sudo ls -l /etc/sudoers.d/ ; sudo grep -n includedir /etc/sudoers
```

```text
-r--r-----. 1 root root 188 Jul 22 13:30 90-cloud-init-users
120:#includedir /etc/sudoers.d
```

That `90-cloud-init-users` file carries the sudo policy of the VM's
administration accounts: do not touch it, always write into **your** file. Note
that AlmaLinux 10 still uses the historical `#includedir` form, not
`@includedir`: both work.

### Write the rule, validate it, and check that it is really read

A rule fits on one line, `who host=(target) commands`, the commands as
**absolute paths**. Write the file somewhere other than `/etc/sudoers.d/` first,
and validate it before installing it:

```bash
cat -n /tmp/30-sauvegarde.bad
sudo visudo -c -f /tmp/30-sauvegarde.bad ; echo "rc=$?"
```

```text
     1	# Delegation sauvegarde
     2	Cmnd_Alias TAILLES = /usr/bin/du
     3	%sauvegarde ALL=(root) NOPASSWD /usr/bin/du

/tmp/30-sauvegarde.bad:3:44: syntax error
%sauvegarde ALL=(root) NOPASSWD /usr/bin/du
                                           ^
rc=1
```

The message gives the **file**, the **line**, the **column** and a cursor. Here,
the colon of `NOPASSWD:` is missing. As long as `rc` is 1, that file has no
business in `/etc/sudoers.d/`.

Once fixed, it is installed with `visudo -f`, which edits in place and validates
on save:

```bash
sudo visudo -f /etc/sudoers.d/30-sauvegarde
sudo ls -l /etc/sudoers.d/30-sauvegarde
sudo visudo -c ; echo "rc=$?"
```

```text
-rw-r-----. 1 root root 77 Jul 22 14:57 /etc/sudoers.d/30-sauvegarde

/etc/sudoers.d/30-sauvegarde: bad permissions, should be mode 0440
/etc/sudoers: parsed OK
/etc/sudoers.d/90-cloud-init-users: parsed OK
rc=1
```

First trap, counter-intuitive: `visudo -f` set `0640`, not `0440`. sudo makes do
with it and applies the rule, but `visudo -c` refuses to validate: the offending
file does **not** get its `parsed OK` and the exit code goes to 1. A
`chmod 0440` is enough, and the three files go back to green:

```bash
sudo chmod 0440 /etc/sudoers.d/30-sauvegarde
sudo visudo -c ; echo "rc=$?"
```

```text
/etc/sudoers: parsed OK
/etc/sudoers.d/30-sauvegarde: parsed OK
/etc/sudoers.d/90-cloud-init-users: parsed OK
rc=0
```

Second trap, nastier: a drop-in can be **ignored silently**. The same file,
named `30-sauvegarde.conf`:

```bash
sudo visudo -c ; echo "rc=$?" ; sudo -l -U nadia
```

```text
/etc/sudoers: parsed OK
/etc/sudoers.d/90-cloud-init-users: parsed OK
rc=0
User nadia is not allowed to run sudo on atelier.
```

`visudo -c` returns 0 and does not even mention the file: a name containing a
dot, or ending with `~`, is skipped without the slightest warning. Renamed
without a dot, it reappears in the list and the rule takes effect. A file left
in `0666` is discarded the same way, but for a message
(`sudo: /etc/sudoers.d/30-sauvegarde is world writable`).

Hence the reflex: after dropping each file, assume nothing, ask sudo what it
understood with `sudo -l -U <user>`.

### NOPASSWD, and the refusal when nothing matches

Without the `NOPASSWD:` tag, the rule requires the caller's password:

```text title="/etc/sudoers.d/30-sauvegarde"
Cmnd_Alias TAILLES = /usr/bin/du -sh /var/log
%sauvegarde ALL=(root) TAILLES
```

```bash
sudo -u nadia sudo -n du -sh /var/log
```

```text
sudo: a password is required
```

`sudo -n` (*non interactive*) refuses to ask for anything: it is the way to
prove that a password **would** be requested. Add the tag
(`%sauvegarde ALL=(root) NOPASSWD: TAILLES`):

```bash
sudo -l -U nadia | tail -2 ; sudo -u nadia sudo -n du -sh /var/log
```

```text
    (root) NOPASSWD: /usr/bin/du -sh /var/log
5.7M	/var/log
```

The alias has been **resolved**: sudo displays the real command, not the label.
The delegation is indeed narrow, the slightest different argument no longer
matches: `sudo -u nadia sudo -n du -sh /var/log/dnf` answers `sudo: a password
is required`, and an unrelated path such as `du -sh /etc` gives exactly the same
answer.

**That message is misleading.** You would expect an explicit refusal; sudo asks
for the password first, because `NOPASSWD:` only applies to the commands that
are **actually matched**. Once the user is authenticated on that second
attempt, the real verdict comes:

```text
Sorry, user nadia is not allowed to execute '/bin/du -sh /etc' as root on atelier.lab.
```

Remember that `sudo: a password is required` says **nothing** about your rights:
only `sudo -l -U` answers that question. Note in passing `/bin/du` where the
rule says `/usr/bin/du`: on this distribution `/bin` is a symbolic link to
`usr/bin`, and sudo works on the resolved path.

### The last rule that matches wins

Unlike the "first match" reflex of firewalls, sudo applies the **last** match.
Two files differing only in the order:

```text title="Order A: deny then allow"
%sauvegarde ALL=(root) NOPASSWD: !/usr/bin/find
%sauvegarde ALL=(root) NOPASSWD: /usr/bin/du, /usr/bin/find
```

`sudo -u nadia sudo -n find /var/log -maxdepth 0` displays `/var/log`: the
denial is **cancelled** by the permissive rule that follows it. Swap the two
lines, changing nothing else:

```text title="Order B: allow then deny"
%sauvegarde ALL=(root) NOPASSWD: /usr/bin/du, /usr/bin/find
%sauvegarde ALL=(root) NOPASSWD: !/usr/bin/find
```

```text
Sorry, user nadia is not allowed to execute '/bin/find /var/log -maxdepth 0' as root on atelier.lab.
```

The same written policy, the opposite result. This also holds **between files**
of `/etc/sudoers.d/`, read in lexical order: hence the convention of the numeric
prefix (`30-`, `90-`) to control that order.

### What delegating a binary really gives

A rule can look restrictive and still give root. Delegate `find` bare:

```text
%sauvegarde ALL=(root) NOPASSWD: /usr/bin/du, /usr/bin/find
```

```bash
sudo -u nadia sudo -n find /var/log -maxdepth 0 -exec id \;
```

```text
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:...
```

`find` knows how to launch other programs: delegating a search command amounts
to delegating **root entirely**. `vim`, `less`, `awk` and `tar` share that flaw.
Imposing the arguments closes the door again: with the rule
`/usr/bin/find /var/log -name *.log`, the intended search goes through and the
`-exec id \;` falls back to `sudo: a password is required`, for want of a match.

The editor case deserves its own demonstration, because it is the most frequent.
With `/usr/bin/vi` delegated, the editor runs as root, and so does its `:!`
escape:

```bash
sudo -u nadia sudo -n vi -es -c ':!id > /tmp/preuve-vi.txt' -c ':q!' /etc/motd
cat /tmp/preuve-vi.txt
```

```text
uid=0(root) gid=0(root) groups=0(root) [...]
```

`sudoedit` reverses the mechanism: only the final replacement of the file is
privileged, the editor itself runs under **your** identity. With the rule
`%sauvegarde ALL=(root) NOPASSWD: sudoedit /etc/motd` and a fake editor that
merely writes the output of `id` into a file:

```bash
sudo -u nadia env SUDO_EDITOR=/tmp/faux-editeur.sh sudoedit -n /etc/motd
cat /tmp/preuve-editeur.txt
```

```text
uid=1002(nadia) gid=1003(nadia) groups=1003(nadia),1002(sauvegarde) [...]
```

Two rules that look alike, two opposite privilege levels. To let someone modify
a file, it is always `sudoedit`, never `sudo <editor>`.

### Defaults: the password that does not come back, and the trace

sudo does not ask for the password again for a few minutes: it keeps a
**timestamp** of the authenticated session. Two calls in a row in the same
shell, with a rule **without** `NOPASSWD:`:

```text
uid=0(root)                            <- 1st call, password entered
--- 2nd call, no password ---
uid=0(root)
```

That delay is set by a `Defaults`, which can target a single user:

```text title="/etc/sudoers.d/30-sauvegarde"
Defaults:nadia timestamp_timeout=0
Defaults:nadia logfile=/var/log/sudo-sauvegarde.log
%sauvegarde ALL=(root) /usr/bin/id
```

```bash
sudo -l -U nadia | head -3
```

```text
Matching Defaults entries for nadia on atelier:
    !visiblepw, always_set_home, [...] secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin,
    timestamp_timeout=0, logfile=/var/log/sudo-sauvegarde.log
```

With `timestamp_timeout=0`, the second call asks for the password again
(`sudo: a password is required`). And `logfile` diverts the journal to a
dedicated file, authorisations as well as refusals:

```bash
sudo cat /var/log/sudo-sauvegarde.log
```

```text
Jul 22 15:00:22 : nadia : PWD=/home/ansible ; USER=root ; COMMAND=/usr/bin/id
Jul 22 15:00:22 : nadia : a password is required ; PWD=/home/ansible ; USER=root
    ; COMMAND=/usr/bin/id
```

Without that `Defaults`, everything goes to the system journal, where the
verdict reads just as well: `sudo journalctl -t sudo --no-pager | tail -2`
displays there, for instance, `nadia : command not allowed ; ... ;
COMMAND=/bin/du -sh /etc`.

One last `Defaults` is worth knowing: `requiretty`, which forbids sudo from
running without a terminal. It does **not** appear in the `Matching Defaults`
above, and that is precisely why all the commands of this course were able to
run through `ssh <host> 'command'`, with no tty.

### Troubleshooting and reset

| Symptom | Likely cause |
|---|---|
| `X is not allowed to run sudo` although the file exists | name containing a `.` or ending with `~`: the file is skipped silently |
| `bad permissions, should be mode 0440`, `visudo -c` with `rc=1` | drop-in permissions; `visudo -f` leaves `0640`, fix with `chmod 0440` |
| `is world writable` | drop-in in `0666`: sudo ignores it completely |
| `sudo: a password is required` despite a `NOPASSWD:` rule | the command typed does not match the rule (extra argument, different path) |
| `Sorry, user ... is not allowed to execute ...` | the rule does not cover that command; compare with `sudo -l -U <user>` |
| A `!` denial has no effect | a permissive rule matches **after** it: the last one wins |
| `syntax error` with line and column | re-read the character pointed at by the cursor (often the `:` of `NOPASSWD:`) |
| The rule looks right but nothing changes | path not absolute, or different from the real one: check with `command -v <binary>` |

To undo everything and start over:

```bash
sudo rm -f /etc/sudoers.d/30-sauvegarde /var/log/sudo-sauvegarde.log
sudo userdel -r nadia
sudo groupdel sauvegarde
sudo visudo -c
sudo -l
```

The last two commands are not optional: they prove that the sudoers
configuration is sound again and that **your** administrator access is intact.
