# Drill — SELinux

**4 tasks, 100 points, 20 minutes. No hints.** RHCSA only
(Debian → `drill-apparmor`). Contexts are checked **after a relabel**.

## Reminder

[**SELinux: understand, troubleshoot and disable**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

On top of classic access control (DAC, the `rwx` permissions), SELinux adds a
**mandatory** control (MAC): every process and every resource carries a label,
and the policy crosses those labels to allow or deny. Day-to-day work bears on
four objects: the **mode** (`enforcing`, `permissive`, `disabled`), the **file
contexts**, the **booleans** and the **port types**. For each of these four
objects, there is a **runtime** setting and a setting **in the policy**: that
distinction is what the drill measures.

## The course

The examples below work on `/opt/partage-demo`, a demonstration directory
intended for a file share, with the type `samba_share_t`, the boolean
`samba_export_all_ro` and the port `2222/tcp`. The challenge will ask you for
other paths, other types, another boolean and another port. The point is to
learn the method, not to copy a line.

All the outputs reproduced here come from an AlmaLinux 10 in `enforcing` mode,
with `policycoreutils-python-utils` installed (that is the package which
provides `semanage`, absent from a minimal installation).

### The only idea to remember: runtime against policy

SELinux has two memories. The first is that of the **running kernel**: it is
changed instantly, and it is lost at reboot. The second is the **local policy
store**, on disk: an explicit command is needed to write to it, and it is what
gets replayed at boot.

| Object | Runtime setting (lost at reboot) | Setting in the policy (persistent) |
|---|---|---|
| Mode | `setenforce 1` / `setenforce 0` | `SELINUX=` line of `/etc/selinux/config` |
| Context of a file | `chcon -t <type> <path>` | `semanage fcontext -a` then `restorecon` |
| Boolean | `setsebool <name> on` | `setsebool -P <name> on` |
| Type of a port | *(nothing: there is no runtime setting)* | `semanage port -a -t <type> -p tcp <port>` |

Every line on the left gives a system that works right away and breaks later.
That is exactly the trap of the exam.

### Reading the mode, and seeing both memories at once

`getenforce` answers in one word:

```bash
getenforce
```

```text
Enforcing
```

`sestatus` is more useful, because it shows **both** values:

```bash
sestatus
```

```text
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Memory protection checking:     actual (secure)
Max kernel policy version:      33
```

`Current mode` is the kernel, `Mode from config file` is the disk. Switch at
runtime and the gap is obvious:

```bash
sudo setenforce 0
sestatus | grep -E "Current mode|Mode from config file"
```

```text
Current mode:                   permissive
Mode from config file:          enforcing
```

```bash
grep "^SELINUX=" /etc/selinux/config
```

```text
SELINUX=enforcing
```

`setenforce` **did not touch** the configuration file: verified by the `md5sum`
of the file before and after, identical. Back to strict mode:

```bash
sudo setenforce 1
getenforce
```

```text
Enforcing
```

Two useful details, checked on the machine:

- `setenforce` also accepts words: `setenforce Permissive` and
  `setenforce Enforcing` work like `0` and `1`;
- without privilege, the command fails explicitly:
  `setenforce: security_setenforce() failed: Permission denied`. `getenforce`,
  on the other hand, is read without `sudo`.

For persistence, you edit the `SELINUX=` line of `/etc/selinux/config`. The
guide insists: **no space around the `=`**, otherwise the line is ignored.

> **Never set `SELINUX=disabled` on RHEL 9 / AlmaLinux 9 and beyond.** That
> value is no longer supported by this file there: the kernel boots with SELinux
> then switches over late. To really disable it, you go through the kernel
> command line (`grubby --update-kernel ALL --args selinux=0`), and **coming
> back from `disabled` to `enforcing` requires a full relabel**
> (`touch /.autorelabel` then reboot), because the files created without SELinux
> have no label at all. It is long, and that is the reason why you do not
> disable SELinux "just to see".

### Reading a context

A context is a four-field label, `user:role:type:level`. The field that matters
day to day is the **type**, the third one.

```bash
sudo mkdir -p /opt/partage-demo
echo "notes de service" | sudo tee /opt/partage-demo/memo.txt
ls -Zd /opt/partage-demo
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:usr_t:s0 /opt/partage-demo
unconfined_u:object_r:usr_t:s0 /opt/partage-demo/memo.txt
```

`-Z` works everywhere: on a process with `ps -eZ`, on your own session with
`id -Z`.

```bash
ps -eZ | grep sshd
```

```text
system_u:system_r:sshd_t:s0-s0:c0.c1023 1082 ?   00:00:00 sshd
system_u:system_r:sshd_session_t:s0-s0:c0.c1023 11315 ? 00:00:00 sshd-session
```

> **A brand new directory does not inherit a neutral type, it inherits its
> parent's.** The guide announces `default_t` for a directory created from
> scratch. That is true only when **no** rule of the policy covers the path.
> Here `/opt` is declared `usr_t` in the policy, so everything created in it is
> born `usr_t`. The command that answers without assuming is `matchpathcon`,
> which gives the type **expected** by the policy for a path:
>
> ```bash
> matchpathcon /opt/partage-demo
> matchpathcon /data/html
> ```
>
> ```text
> /opt/partage-demo	system_u:object_r:usr_t:s0
> /data/html	system_u:object_r:default_t:s0
> ```
>
> `/data` does not exist on this machine and is covered by no rule: it is that
> one which gives `default_t`, not `/opt`.

### `chcon`: it works, and it does not hold

`chcon` writes the label directly onto the inode. The result is immediate:

```bash
sudo chcon -t samba_share_t /opt/partage-demo/memo.txt
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:samba_share_t:s0 /opt/partage-demo/memo.txt
```

The service accesses the file, all is well. Then somebody relabels:

```bash
sudo restorecon -v /opt/partage-demo/memo.txt
ls -Z /opt/partage-demo/memo.txt
```

```text
Relabeled /opt/partage-demo/memo.txt from unconfined_u:object_r:samba_share_t:s0 to unconfined_u:object_r:usr_t:s0
unconfined_u:object_r:usr_t:s0 /opt/partage-demo/memo.txt
```

The work is wiped out. `restorecon` does not "restore" what you had set: it puts
back what **the policy** prescribes, and the policy has never heard of your
`chcon`. Keep `chcon` for tests lasting a few minutes.

### `semanage fcontext` + `restorecon`: the setting that holds

Two commands, and the order has a meaning: you **declare** the rule first, you
**apply** it afterwards.

```bash
sudo semanage fcontext -a -t samba_share_t "/opt/partage-demo(/.*)?"
sudo semanage fcontext -l -C
```

```text
SELinux fcontext                                   type               Context

/opt/partage-demo(/.*)?                            all files          system_u:object_r:samba_share_t:s0
```

The `-C` option limits the list to the **local** rules, the ones you added.
Without it, `semanage fcontext -l` unrolls the rules of the base policy: 5927
lines on this machine (`semanage fcontext -l | wc -l`).

Careful: declaring changes nothing on the disk. Right after the `semanage`, the
file still carries its old type:

```bash
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:usr_t:s0 /opt/partage-demo/memo.txt
```

It is `restorecon` that applies the rule, `-R` to go down recursively and `-v`
to say what it does:

```bash
sudo restorecon -Rv /opt/partage-demo
```

```text
Relabeled /opt/partage-demo from unconfined_u:object_r:usr_t:s0 to unconfined_u:object_r:samba_share_t:s0
Relabeled /opt/partage-demo/memo.txt from unconfined_u:object_r:usr_t:s0 to unconfined_u:object_r:samba_share_t:s0
```

And now the proof that `chcon` lacked: relabel a second time, and **nothing
moves** (`restorecon -Rv` no longer prints a single line, because it has nothing
left to fix).

```bash
sudo restorecon -Rv /opt/partage-demo
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:samba_share_t:s0 /opt/partage-demo/memo.txt
```

About the path expression: `"/opt/partage-demo(/.*)?"` is a **regular
expression**, to be put between quotes so that the shell does not touch it. It
reads "this directory, and possibly everything it contains". Without the
`(/.*)?`, only the directory itself would be covered and the files inside would
keep their type.

The rule is written in the local store, which can be read:

```bash
sudo cat /var/lib/selinux/targeted/active/file_contexts.local
```

```text
# This file is auto-generated by libsemanage
# Do not edit directly.

/opt/partage-demo(/.*)?    system_u:object_r:samba_share_t:s0
```

> **The guide places this file under `/etc/selinux/`.** On AlmaLinux 10 it is
> not there: the active store is under `/var/lib/selinux/targeted/active/`
> (`file_contexts.local`, `booleans.local`). You never edit it by hand, but
> knowing where it is lets you check at a glance what has been made persistent.

Note that the rule declares `system_u` while the file stays `unconfined_u` after
`restorecon`: by default, `restorecon` only fixes the **type**. The `-F` option
forces the whole context, user field included.

```bash
sudo restorecon -FRv /opt/partage-demo
```

```text
Relabeled /opt/partage-demo from unconfined_u:object_r:samba_share_t:s0 to system_u:object_r:samba_share_t:s0
Relabeled /opt/partage-demo/memo.txt from unconfined_u:object_r:samba_share_t:s0 to system_u:object_r:samba_share_t:s0
```

For the rules that interest you, only the type counts: do not be alarmed by an
`unconfined_u`.

### What breaks a context without warning: `mv`

Once the rule is in place, a file **created** in the directory, or **copied**
into it, takes the right type on its own. A file that is **moved** keeps its
own.

```bash
echo "source"  > /tmp/source.txt
echo "source2" > /tmp/source2.txt
echo "nouveau" | sudo tee /opt/partage-demo/nouveau.txt
sudo cp /tmp/source.txt  /opt/partage-demo/copie.txt
sudo mv /tmp/source2.txt /opt/partage-demo/deplace.txt
ls -Z /opt/partage-demo/
```

```text
unconfined_u:object_r:samba_share_t:s0 copie.txt
   unconfined_u:object_r:user_tmp_t:s0 deplace.txt
    system_u:object_r:samba_share_t:s0 memo.txt
unconfined_u:object_r:samba_share_t:s0 nouveau.txt
```

`copie.txt` and `nouveau.txt` are fine, `deplace.txt` brought back the
`user_tmp_t` of `/tmp`. `mv` does not recreate the file, it changes its name:
the context follows. Hence the reflex after any move:

```bash
sudo restorecon -Rv /opt/partage-demo
```

```text
Relabeled /opt/partage-demo/deplace.txt from unconfined_u:object_r:user_tmp_t:s0 to unconfined_u:object_r:samba_share_t:s0
```

### The booleans

A boolean is a switch provided by the policy: it turns a bundle of rules on or
off without writing a module. There are 314 of them on this AlmaLinux 10
(`getsebool -a | wc -l`).

```bash
getsebool samba_export_all_ro
```

```text
samba_export_all_ro --> off
```

`setsebool` without an option acts **only on the running kernel**:

```bash
sudo setsebool samba_export_all_rw on
sudo semanage boolean -l | grep "^samba_export_all_rw"
```

```text
samba_export_all_rw            (on   ,  off)  Allow samba to export all rw
```

This `(current, default)` pair is the best diagnostic tool in the whole lab:
**the first value is the state of the kernel, the second that of the policy**.
`(on, off)` means "active now, off at the next reboot". It is a trap that cannot
be seen with `getsebool`, which only shows the first one.

The `-P` option writes the value into the policy:

```bash
sudo setsebool -P samba_export_all_ro on
sudo semanage boolean -l | grep "^samba_export_all_ro"
```

```text
samba_export_all_ro            (on   ,   on)  Allow samba to export all ro
```

`(on, on)`: the two memories agree, the setting will survive. The shortcut to
see only what has been made persistent:

```bash
sudo semanage boolean -l -C
```

```text
SELinux boolean                State  Default Description

samba_export_all_ro            (on   ,   on)  Allow samba to export all ro
```

The boolean switched without `-P` does not appear there: this really is the list
of what is persistent. The value lives in
`/var/lib/selinux/targeted/active/booleans.local`:

```text
# This file is auto-generated by libsemanage
# Do not edit directly.

samba_export_all_ro=1
```

`setsebool -P` is slower than `setsebool` (it recompiles the store): that is
normal, let it finish.

### The ports

A service can only bind to a port whose type is allowed for its domain. Moving a
service to another port without telling SELinux means a failure at startup. You
first look at what the policy knows:

```bash
sudo semanage port -l | grep -E "^ssh_port_t"
```

```text
ssh_port_t                     tcp      22
```

You add the wanted port to the type:

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo semanage port -l | grep -E "^ssh_port_t"
```

```text
ssh_port_t                     tcp      2222, 22
```

And the list of local additions, which proves that it is indeed in the policy:

```bash
sudo semanage port -l -C
```

```text
SELinux Port Type              Proto    Port Number

ssh_port_t                     tcp      2222
```

There is **no** "runtime" equivalent for a port: `semanage port` is the only
gesture, it is persistent by construction. It is the only one of the four
objects in the table where you cannot pick the wrong memory.

To find out who already owns a port, you search for the whole number:

```bash
sudo semanage port -l | grep -w 3306
```

```text
mysqld_port_t                  tcp      1186, 3306, 63132-63164
```

> **On AlmaLinux 10, `semanage port -a` on an already taken port does not
> fail.** The guide announces a `ValueError ... already defined` that would force
> you to redo the command with `-m`. The machine, however, answers:
>
> ```bash
> sudo semanage port -a -t ssh_port_t -p tcp 3306
> ```
>
> ```text
> Port tcp/3306 already defined, modifying instead
> ```
>
> with a return code of `0`. `semanage` switches to modification on its own
> (`policycoreutils-python-utils-3.10-1.el10`, `libsemanage-3.10-1.el10`). The
> result is a port that appears under **two** types, the base entry and yours:
>
> ```text
> mysqld_port_t                  tcp      1186, 3306, 63132-63164
> ssh_port_t                     tcp      3306, 2222, 22
> ```
>
> Use `-m` anyway: it is explicit, it works on older versions that refuse `-a`,
> and it is what an exam marker expects.

You remove a local addition with `-d`, without specifying the type:

```bash
sudo semanage port -d -p tcp 3306
sudo semanage port -l -C
```

```text
SELinux Port Type              Proto    Port Number

ssh_port_t                     tcp      2222
```

Only the local entry has gone; `mysqld_port_t` keeps its original ports, which
come from the base policy and are not yours to delete.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| The mode falls back to `permissive` after a reboot | `setenforce 1` alone; the `SELINUX=` line of `/etc/selinux/config` was not changed |
| `SELINUX=` seems to be ignored | space around the `=` in `/etc/selinux/config` |
| The context of a file goes back to the old one after a `restorecon` | it was set by `chcon`; a `semanage fcontext` rule is needed |
| `semanage fcontext -a` went through, but the file has not changed | the `restorecon -Rv` that applies the rule is missing |
| The directory is fine, the files inside are not | the path expression forgets `(/.*)?` |
| A file that arrived by `mv` has the wrong type | `mv` keeps the context; run `restorecon` again |
| An active boolean falls back at reboot | `setsebool` without `-P`; `semanage boolean -l` then shows `(on, off)` |
| The service refuses to start on a non-standard port | the port is not declared in the type expected by the domain |
| `semanage: command not found` | the `policycoreutils-python-utils` package is not installed |

When an access is denied without explanation, denials are logged even in
`permissive`:

```bash
sudo ausearch -m avc --success no
sudo ausearch -m avc --success no | audit2why
```

`audit2why` translates the denial and often points out that a simple boolean
would be enough. Generating a module with `audit2allow` is the **last** resort,
after having tried to fix the label then to switch a boolean: a module written
blindly can allow a confined domain to write into system types, and most often
hides a bad labelling that a `restorecon` would have settled.

### Undoing everything

```bash
sudo semanage port -d -p tcp 2222
sudo setsebool -P samba_export_all_ro off
sudo semanage fcontext -d "/opt/partage-demo(/.*)?"
sudo restorecon -Rv /opt/partage-demo
sudo rm -rf /opt/partage-demo
sudo setenforce 1
```

The order matters: `semanage fcontext -d` removes the rule, but the files keep
their label until `restorecon` has been run again. It is the same mechanism as
on the way in, in the other direction.

```text
Relabeled /opt/partage-demo from system_u:object_r:samba_share_t:s0 to system_u:object_r:usr_t:s0
Relabeled /opt/partage-demo/memo.txt from system_u:object_r:samba_share_t:s0 to system_u:object_r:usr_t:s0
```

Check that you really are back to zero: the three lists of local customisations
must be empty, and strict mode active.

```bash
sudo semanage fcontext -l -C
sudo semanage boolean -l -C
sudo semanage port -l -C
getenforce
```

> **`setsebool -P <name> off` does not delete the customisation, it writes a new
> one.** After the `off`, `semanage boolean -l -C` still lists the boolean, as
> `(off, off)`. And unlike `semanage port` and `semanage fcontext`,
> `semanage boolean` **has no `-d` option**: the command says so itself,
> `error: one of the arguments -m/--modify -l/--list -E/--extract -D/--deleteall
> is required`. To really erase the entry, you need `semanage boolean -D`, which
> deletes **all** the boolean customisations of the machine, not only yours. To
> be kept for a workshop machine.
