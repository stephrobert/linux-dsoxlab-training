# Lab — fix a SELinux file context persistently

## Reminder

[**SELinux on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Every file carries a SELinux **type**. A confined service only touches the files
whose type is allowed by its policy: a logging daemon writes into `var_log_t`, a
database into its own type, and so on. `chcon` sets a label but a relabel loses
it; `semanage fcontext -a -t <type> "<path-regex>"` writes a persistent rule and
`restorecon -Rv <path>` applies it. `ls -Z` shows the live type.

## The course

The examples below deliberately deal with something other than the challenge:
`rsyslog` is made to write an application log into a home-made directory,
`/opt/journaux-appli`. You learn the method and you transpose it, you do not copy
a line.

All the outputs reproduced here were obtained on an AlmaLinux 10 in enforcing
mode.

### First check: is SELinux really active?

Nothing that follows can be demonstrated if SELinux does not enforce its policy.
So it is the first command, before any diagnosis:

```bash
getenforce
```

```text
Enforcing
```

`sestatus` gives the complete view, and above all two lines that you must know
how to tell apart:

```text
SELinux status:                 enabled
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
```

`Current mode` is the **current** mode (the one `setenforce` changes);
`Mode from config file` is the one the machine will take up **at the next
boot**, read in `/etc/selinux/config`. The two can diverge, and that is exactly
what makes a server "that works" stop working after a reboot.

> `setenforce 0` switches to permissive: SELinux carries on logging but no longer
> blocks anything. It is a diagnostic tool, to be set back to `1` right after. On
> the other hand, **never** touch `SELINUX=` in `/etc/selinux/config` to work
> around a denial: you fix nothing, you disarm the machine, and on RHEL 9 and
> later coming back from `disabled` to `enforcing` imposes a complete relabel of
> the disk.

The policy loaded here is `targeted`: only the services listed in the policy are
confined, the rest runs as `unconfined_t`.

### Reading a label: four fields, only one that decides

A context is written `user:role:type:level`. It is read on three different
objects, with three commands:

```bash
ls -Zd /opt/journaux-appli      # a file or a directory
ps -eZ | grep rsyslogd          # a process
id -Z                           # your own shell
```

```text
unconfined_u:object_r:usr_t:s0 /opt/journaux-appli
system_u:system_r:syslogd_t:s0    25554 ?        00:00:00 rsyslogd
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

Let us detail the first one: `unconfined_u` is the SELinux user (unrelated to
the owning Unix user), `object_r` the role (invariably `object_r` on a file),
`usr_t` the **type**, `s0` the MLS level.

**In almost all day-to-day work, only the type counts.** It is the one the policy
crosses: here, a process in `syslogd_t` facing a directory in `usr_t`. The three
other fields, you will read without modifying them.

The third output deserves a remark: your shell is `unconfined_t`, that is to say
unconfined. You will therefore never meet a SELinux denial by typing commands
yourself, which explains why the problem always seems to come "from the service"
and never from you.

### The denial: "Permission denied" with perfect Unix permissions

Let us set the scene. A directory is created and `rsyslog` is asked to drop the
messages of the `local5` facility into it:

```bash
sudo mkdir -p /opt/journaux-appli
printf 'local5.*  /opt/journaux-appli/atelier.log\n' | sudo tee /etc/rsyslog.d/99-atelier.conf
sudo systemctl restart rsyslog
logger -p local5.info "message de test"
```

Nothing arrives in the directory. And yet the Unix permissions are beyond
reproach, and `rsyslogd` runs as root:

```bash
ls -ld /opt/journaux-appli
```

```text
drwxr-xr-x. 2 root root 6 Jul 22 15:58 /opt/journaux-appli
```

The service, for its part, complains about a permission denied:

```bash
sudo journalctl -u rsyslog --since -1min | grep -i "open error"
```

```text
rsyslogd[25441]: file '/opt/journaux-appli/atelier.log': open error: Permission denied
```

This is the baffling message par excellence: root, `drwxr-xr-x`, and yet
refused. The Unix angle being ruled out, the answer is in the audit log:

```bash
sudo ausearch -m avc --success no -ts recent
```

```text
type=AVC msg=audit(1784736057.748:15868): avc:  denied  { write } for  pid=26086
  comm=72733A6D61696E20513A526567 name="journaux-appli" dev="vda4" ino=8590658
  scontext=system_u:system_r:syslogd_t:s0
  tcontext=unconfined_u:object_r:usr_t:s0 tclass=dir permissive=0
```

Four pieces of information are enough to conclude: `denied { write }` is the
forbidden operation, `scontext=...:syslogd_t` the type of the requesting
**process**, `tcontext=...:usr_t` the type of the refused **target**, and
`tclass=dir` the nature of that target. `permissive=0` confirms that the denial
was really **enforced** and not merely logged. The `comm=` in hexadecimal is not
a bug: that is how `ausearch` encodes names containing special characters, here
the thread name `rs:main Q:Reg`.

`audit2why` translates the same line:

```bash
sudo ausearch -m avc --success no -ts recent | audit2why
```

```text
	Was caused by:
		Missing type enforcement (TE) allow rule.

		You can use audit2allow to generate a loadable module to allow this access.
```

Take that suggestion for what it is: the **last** of the three options. You first
fix the label, then you look for a boolean, and only as a last resort do you
generate a module.

> On this machine, `sealert` is not available: `rpm -q setroubleshoot-server`
> answers `package setroubleshoot-server is not installed`. That is the case of
> any minimal installation, and it is also the case in the exam. Knowing how to
> read the raw AVC is therefore not a fallback, it is the expected skill. If the
> package is installed, `journalctl -t setroubleshoot` repeats the same denials
> in plain language.

### What type should this path carry?

Faced with a denial, the real question is not "which type to set" but "which type
does the policy expect here". `matchpathcon` answers without modifying anything:

```bash
matchpathcon /opt/journaux-appli /var/log/messages
```

```text
/opt/journaux-appli	system_u:object_r:usr_t:s0
/var/log/messages	system_u:object_r:var_log_t:s0
```

The verdict is clear: our directory inherits `usr_t` (the default type under
`/opt`), whereas a log file is filed under `var_log_t`. That is the exact gap the
AVC was reporting.

Second method, useful when you are looking for a precedent: query the context
database, which here holds close to six thousand rules (`grep` is
indispensable).

```bash
sudo semanage fcontext -l | grep -w var_log_t | head -2
```

```text
/nsr/logs(/.*)?                                    all files          system_u:object_r:var_log_t:s0
/opt/zimbra/log(/.*)?                              all files          system_u:object_r:var_log_t:s0
```

These lines show in passing the shape of a rule: a path **regular expression**, a
file class, a context.

### `chcon`: correct straight away, lost at the first `restorecon`

`chcon` writes the label directly onto the inode. The effect is immediate:

```bash
sudo chcon -t var_log_t /opt/journaux-appli
sudo systemctl restart rsyslog
logger -p local5.info "premier essai"
sudo ls -lZ /opt/journaux-appli/
```

```text
-rw-------. 1 root root system_u:object_r:var_log_t:s0 68 Jul 22 16:00 atelier.log
```

The log is written, the created file inherits the type of the directory.
Everything seems settled. Now, the check that counts:

```bash
sudo restorecon -Rv /opt/journaux-appli
```

```text
Relabeled /opt/journaux-appli from unconfined_u:object_r:var_log_t:s0 to unconfined_u:object_r:usr_t:s0
Relabeled /opt/journaux-appli/atelier.log from system_u:object_r:var_log_t:s0 to system_u:object_r:usr_t:s0
```

Everything is undone. And the service breaks down again:

```text
rsyslogd[25902]: file '/opt/journaux-appli/atelier.log': open error: Permission denied
```

**The reason fits in one sentence: `chcon` does not modify the policy.** It sets
a label on an object, without writing anywhere that this path deserves it. As
soon as something consults the reference, the label is judged wrong and
corrected. And that "something" comes along on its own: a `restorecon` launched
by a package or a script, a `/.autorelabel` at boot, a restore after a backup.
The service holds for weeks, then falls over at a reboot without anybody having
changed a thing. So keep `chcon` for the quick test that confirms a diagnosis,
as was just done.

### `semanage fcontext` + `restorecon`: the fix that holds

The lasting fix is done in two stages, and both are indispensable:
`semanage fcontext -a` **writes the rule**, `restorecon` **applies it** to the
files already present.

```bash
sudo semanage fcontext -a -t var_log_t "/opt/journaux-appli(/.*)?"
```

Nothing is displayed, but the reference has changed. `matchpathcon` confirms it
before a single file has moved:

```text
/opt/journaux-appli/atelier.log	system_u:object_r:var_log_t:s0
```

Note the shape of the path: `"/opt/journaux-appli(/.*)?"` is a regular
expression, between quotes so that the shell does not touch it. The final
`(/.*)?` means "this directory, and possibly everything below it". Without it,
the rule would only cover the directory itself.

Apply it:

```bash
sudo restorecon -Rv /opt/journaux-appli
```

```text
Relabeled /opt/journaux-appli from unconfined_u:object_r:usr_t:s0 to unconfined_u:object_r:var_log_t:s0
```

The service writes again. And this time, the test that killed the `chcon` no
longer changes anything:

```bash
sudo restorecon -Rv /opt/journaux-appli   # no line: nothing to fix
sudo ls -ldZ /opt/journaux-appli
```

```text
drwxr-xr-x. 2 root root unconfined_u:object_r:var_log_t:s0 25 Jul 22 16:00 /opt/journaux-appli
```

Two commands prove that the rule really is in the policy, and not only on the
disk. `-C` restricts the output to the **local** rules, the ones you added:

```bash
sudo semanage fcontext -l -C
```

```text
SELinux fcontext                                   type               Context

/opt/journaux-appli(/.*)?                          all files          system_u:object_r:var_log_t:s0
```

It is stored in a file that you never modify by hand:

```text
# /etc/selinux/targeted/contexts/files/file_contexts.local
# This file is auto-generated by libsemanage
# Do not edit directly.

/opt/journaux-appli(/.*)?    system_u:object_r:var_log_t:s0
```

That is the whole difference: `chcon` was writing onto the inode,
`semanage fcontext` writes here. A full relabel re-reads this file, so the fix
survives.

### Undoing cleanly

A local rule is removed with `-d`, by repeating **exactly** the expression used
when adding it. The removal relabels nothing: you have to run `restorecon`
again, which then applies the default type found back.

```bash
sudo semanage fcontext -d "/opt/journaux-appli(/.*)?"
sudo restorecon -Rv /opt/journaux-appli
```

```text
Relabeled /opt/journaux-appli from unconfined_u:object_r:var_log_t:s0 to unconfined_u:object_r:usr_t:s0
```

Two checks to close: the list of local rules must be empty, and SELinux still in
enforcing.

```bash
sudo semanage fcontext -l -C   # no line
getenforce                     # Enforcing
```

**The reflex to keep.** Faced with a service that refuses a file although `ls -l`
looks correct:

1. `getenforce`: is SELinux involved?
2. `ausearch -m avc --success no -ts recent`: read `scontext`, `tcontext`, the
   operation and `permissive=`.
3. `matchpathcon <path>`: which type does the policy expect?
4. If the live type is wrong but the policy right: `restorecon -Rv`.
5. If the policy itself ignores this path:
   `semanage fcontext -a -t <type> "<path>(/.*)?"` then `restorecon -Rv`.
6. `chcon` only to confirm a hypothesis, never as a fix.
