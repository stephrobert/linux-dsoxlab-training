# Lab — package management with dnf

## Reminder

[**dnf on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

`dnf install <pkg>` adds a package and its dependencies; `dnf remove <pkg>` takes
it out; `dnf list installed` and `rpm -q <pkg>` query what is present. `rpm -ql
<pkg>` lists the files a package owns.

## The course

The examples below work on `httpd-tools`, `nano`, `bc` and `apr`: the challenge
will ask you for other packages. The point is to learn the install / verify /
query / undo loop, not to copy a line.

Every output in this course was recorded on an **AlmaLinux 10.2** (`dnf` 4.20.0),
the same family as the lab machine.

### Where the machine stands

Before touching anything, three questions: which DNF version, which repositories
are active, how many packages are installed.

```bash
dnf --version | head -1
dnf repolist
rpm -qa | wc -l
```

On the machine used for writing:

```text
4.20.0
repo id                          repo name
appstream                        AlmaLinux 10 - AppStream
baseos                           AlmaLinux 10 - BaseOS
crb                              AlmaLinux 10 - CRB
extras                           AlmaLinux 10 - Extras
415
```

That starting count is your point of comparison: after an installation and its
cancellation, you must land back on it. It is the only serious proof that an
operation left nothing behind.

`dnf repolist` only shows the **active** repositories. A package that is
"nowhere to be found" comes nine times out of ten from a disabled repository,
and `dnf repolist all` adds the status column:

```bash
dnf repolist all
```

```text
repo id                      repo name                                  status
appstream                    AlmaLinux 10 - AppStream                   enabled
appstream-debuginfo          AlmaLinux 10 - AppStream - Debug           disabled
baseos                       AlmaLinux 10 - BaseOS                      enabled
crb                          AlmaLinux 10 - CRB                         enabled
highavailability             AlmaLinux 10 - HighAvailability            disabled
```

> **The guide presents `crb` as a repository that ships disabled, to be enabled
> with `dnf config-manager --set-enabled crb`.** On the AlmaLinux 10.2 of this
> lab, it is **already active**: `dnf repolist all` reports it `enabled` without
> anyone touching it. Check before running the enabling command, it has nothing
> to do here.

### Install a package, and prove it

`dnf` redoes the dependency resolution every time and shows you its plan before
acting. The `--assumeno` option answers "no" to the final question: you read the
summary without changing anything.

```bash
sudo dnf install --assumeno httpd-tools
```

```text
================================================================================
 Package               Arch        Version                 Repository      Size
================================================================================
Installing:
 httpd-tools           x86_64      2.4.63-13.el10_2.4      appstream       82 k
Installing dependencies:
 apr                   x86_64      1.7.5-3.el10            appstream      127 k
 apr-util              x86_64      1.6.3-23.el10_1         appstream       97 k
Installing weak dependencies:
 apr-util-lmdb         x86_64      1.6.3-23.el10_1         appstream       13 k
 apr-util-openssl      x86_64      1.6.3-23.el10_1         appstream       15 k

Transaction Summary
================================================================================
Install  5 Packages
Operation aborted.
```

One package requested, five installed: that is the whole point of a package
manager. The summary separates three blocks you must know how to read: what you
asked for (`Installing:`), what is **mandatory** to make it work (`Installing
dependencies:`), and what is **recommended without being required**
(`Installing weak dependencies:`).

Then for real:

```bash
sudo dnf install -y httpd-tools
```

```text
Installed:
  apr-1.7.5-3.el10.x86_64               apr-util-1.6.3-23.el10_1.x86_64
  apr-util-lmdb-1.6.3-23.el10_1.x86_64  apr-util-openssl-1.6.3-23.el10_1.x86_64
  httpd-tools-2.4.63-13.el10_2.4.x86_64

Complete!
```

> **`-y` has a price.** The guide is clear: the option is indispensable in
> scripts and in CI, but dangerous interactively, because you no longer read the
> summary and therefore do not see that an operation is about to **remove** a
> package. On a server, run first without `-y` (or with `--assumeno`) and read
> the `Removing` line.

`Complete!` proves nothing: it says the transaction went through, not that you
got what you wanted. The two control commands are:

```bash
rpm -q httpd-tools
dnf list installed httpd-tools
```

```text
httpd-tools-2.4.63-13.el10_2.4.x86_64
Installed Packages
httpd-tools.x86_64                 2.4.63-13.el10_2.4                 @appstream
```

`rpm -q` queries the local RPM database and returns the full **NEVRA** (name,
version, release, architecture). `dnf list installed` adds the right-hand
column: the **origin repository**, here `@appstream`. The `@` marks an installed
package, as opposed to the bare name of a package that is only available.

When the package is absent, `rpm -q` says so plainly and exits with an error:

```bash
rpm -q httpd-tools
```

```text
package httpd-tools is not installed
```

### Finding the right package

Half the work consists in finding the **exact name** of the package. The guide
insists on a point that practice confirms: `search` and `provides` do not look
in the same place.

`dnf search` digs through **names and summaries**:

```bash
dnf search apache
```

```text
======================== Name & Summary Matched: apache ========================
ant-apache-bcel.noarch : Optional apache bcel tasks for ant
apache-commons-cli-javadoc.noarch : API documentation for apache-commons-cli
```

That command has a limit you should measure yourself once. Look for the name of
a **command** with `search`:

```bash
dnf search htpasswd
```

```text
No matches found.
```

Yet `htpasswd` does exist and a package ships it. `search` does not see the
**contents** of packages. `provides` is the one that indexes files, and it is
the command that saves you in front of a `command not found`:

```bash
command -v htpasswd          # nothing, return code 1
dnf provides "*/bin/htpasswd"
```

```text
httpd-tools-2.4.63-13.el10.x86_64 : Tools for use with the Apache HTTP Server
Repo        : appstream
Matched from:
Filename    : /usr/bin/htpasswd

httpd-tools-2.4.63-13.el10_2.1.x86_64 : Tools for use with the Apache HTTP Server
Repo        : appstream
Matched from:
Filename    : /usr/bin/htpasswd
```

Two details of the output deserve attention. First it lists **several versions**
of the same package: the repository keeps the history, the highest one will be
picked. Then, if the package is already installed, one of the entries carries
`Repo : @System`, which designates the local RPM database and not a remote
repository.

The `*/bin/htpasswd` pattern is not decoration. With a partial or inexact path,
`dnf` fails and hands you the solution itself:

```text
Error: No matches found. If searching for a file, try specifying the full path
or using a wildcard prefix ("*/") at the beginning.
```

Once the name is found, `dnf info` describes the package **before** installing
it: version, size, repository, license, description.

```bash
dnf info bc
```

```text
Size         : 125 k
Source       : bc-1.07.1-23.el10.src.rpm
Repository   : baseos
Summary      : GNU's bc (a numeric processing language) and dc (a calculator)
License      : GPL-3.0-or-later
```

Remember the three questions: `search` for a keyword, `provides` for a file or a
command, `info` for a package already identified.

### Querying without installing anything

`dnf repoquery` works on the **repository metadata**. It never touches the
system, which makes it the investigation tool of choice before a risky
operation.

```bash
dnf repoquery --requires httpd-tools
```

```text
libapr-1.so.0()(64bit)
libaprutil-1.so.0()(64bit)
libcrypt.so.2()(64bit)
libssl.so.3(OPENSSL_3.0.0)(64bit)
rtld(GNU_HASH)
```

Dependencies are not expressed as package names but as **capabilities** (here
shared libraries): it is DNF that then translates each capability into a
providing package. This explains the `apr` and the `apr-util` seen in the
installation summary, which appeared nowhere in the command that was typed.

The symmetric question, to ask **before** removing a library:

```bash
dnf repoquery --whatrequires apr-util
```

```text
apr-util-devel-0:1.6.3-23.el10_1.x86_64
apr-util-ldap-0:1.6.3-23.el10_1.x86_64
apr-util-openssl-0:1.6.3-23.el10_1.x86_64
```

Finally, `dnf repoquery --userinstalled` separates what **you** asked for from
what arrived as a dependency. That distinction is not cosmetic: it changes the
behaviour of `remove`, as we are about to see.

### What a package contains, and where a file comes from

`rpm` answers the local questions, about what is already installed. Two options
are enough day to day.

`rpm -ql` lists the files **shipped** by a package:

```bash
rpm -ql httpd-tools
```

```text
/usr/bin/ab
/usr/bin/htdbm
/usr/bin/htdigest
/usr/bin/htpasswd
/usr/bin/httxt2dbm
/usr/bin/logresolve
/usr/share/doc/httpd-tools/LICENSE
/usr/share/man/man1/htpasswd.1.gz
```

`rpm -qf` does the opposite: from a file present on disk, it names the **owning**
package.

```bash
rpm -qf /usr/bin/htpasswd
```

```text
httpd-tools-2.4.63-13.el10_2.4.x86_64
```

Do not confuse it with `dnf provides`: `rpm -qf` only looks at the machine and
requires the file to actually exist; `dnf provides` queries the repositories and
answers even for a package that was never installed. The first serves to audit a
system, the second to prepare an installation.

`rpm -qi` completes the picture with the metadata, including the **signature**,
which proves the origin of the package:

```bash
rpm -qi httpd-tools | head -12
```

```text
Name        : httpd-tools
Version     : 2.4.63
Release     : 13.el10_2.4
Architecture: x86_64
Install Date: Wed 22 Jul 2026 02:37:49 PM UTC
Signature   :
              RSA/SHA256, Wed 01 Jul 2026 11:37:13 AM UTC, Key ID dee5c11cc2a1e572
Source RPM  : httpd-2.4.63-13.el10_2.4.src.rpm
```

The `Source RPM` line is instructive: `httpd-tools` is built from the `httpd`
source. A single source package often yields several binary packages.

### `dnf list installed` or `rpm -qa`?

Both list what is installed, and they are believed to be interchangeable. They
are not. Count:

```bash
dnf list installed | tail -n +2 | wc -l
rpm -qa | wc -l
```

```text
415
416
```

One package of difference. It is found with:

```bash
rpm -qa | grep gpg-pubkey
```

```text
gpg-pubkey-c2a1e572-668fe8ef
```

`gpg-pubkey` is a **pseudo-package**: the RPM database stores the imported GPG
keys there, which come from no repository and contain no file. `rpm -qa` shows
them because it reads the database as it is; `dnf list installed` does not show
them because it reasons in terms of repository packages.

To remember: `rpm -qa` is the raw view of the RPM database, `dnf list installed`
the view enriched with the origin repository. For an exhaustive audit, `rpm
-qa`. To know where a package comes from, `dnf list installed`.

### Removing: what `dnf remove` does, and what it does not

On RHEL and derivatives, `dnf remove` **cleans up dependencies that became
orphans**, because `clean_requirements_on_remove` is enabled by default. You can
read it in the configuration:

```bash
cat /etc/dnf/dnf.conf
```

```text
[main]
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
best=True
skip_if_unavailable=False
```

And verify it on the five packages installed above:

```bash
sudo dnf remove -y httpd-tools
rpm -qa | wc -l
```

```text
Removed:
  apr-1.7.5-3.el10.x86_64                 apr-util-1.6.3-23.el10_1.x86_64
  apr-util-lmdb-1.6.3-23.el10_1.x86_64    apr-util-openssl-1.6.3-23.el10_1.x86_64
  httpd-tools-2.4.63-13.el10_2.4.x86_64

Complete!
415
```

One package named, five removed, and the count comes back to its starting
point.

Now the trap, and it is a real one. Take the same installation again, but having
**explicitly** asked for `apr` beforehand:

```bash
sudo dnf install -y apr
sudo dnf install -y httpd-tools     # now installs only 4 packages
sudo dnf remove -y httpd-tools
rpm -q apr
rpm -qa | wc -l
```

```text
Removed:
  apr-util-1.6.3-23.el10_1.x86_64          apr-util-lmdb-1.6.3-23.el10_1.x86_64
  apr-util-openssl-1.6.3-23.el10_1.x86_64  httpd-tools-2.4.63-13.el10_2.4.x86_64

apr-1.7.5-3.el10.x86_64
416
```

`apr` stayed, and the machine no longer counts 415 packages but 416. DNF leaves
it in place because it is marked as **installed at the user's request**:

```bash
dnf repoquery --userinstalled | grep '^apr'
```

```text
apr-0:1.7.5-3.el10.x86_64
```

That is the lesson of this section: **`dnf remove` does not necessarily bring
the machine back to its previous state**. It removes what you name and the
orphans, but never a package you asked for yourself. `dnf autoremove` will not
change that either, for the same reason:

```bash
sudo dnf autoremove --assumeno
```

```text
Dependencies resolved.
Nothing to do.
Complete!
```

### History: inspect, then undo

DNF records **every transaction** and knows how to replay it backwards. That is
what sets it apart from a plain installer, and it is the correct tool to undo an
operation.

```bash
sudo dnf history list
```

```text
ID     | Command line             | Date and time    | Action(s)      | Altered
-------------------------------------------------------------------------------
    13 | remove -y httpd-tools    | 2026-07-22 14:38 | Removed        |    4
    12 | install -y httpd-tools   | 2026-07-22 14:38 | Install        |    4
    11 | install -y apr           | 2026-07-22 14:38 | Install        |    1
    10 | history undo -y 8        | 2026-07-22 14:38 | Removed        |    1
     9 | remove -y nano           | 2026-07-22 14:38 | Removed        |    1
     8 | install -y nano bc       | 2026-07-22 14:38 | Install        |    2
```

Each line carries an identifier, the **command line** as it was typed, the date
and the number of packages touched. Note that the undos themselves appear there
(ID 10): the history is not rewritten, it stacks up.

Before undoing, **inspect**:

```bash
sudo dnf history info 8
```

```text
Transaction ID : 8
Begin time     : Wed 22 Jul 2026 02:38:34 PM UTC
User           :  <ansible>
Return-Code    : Success
Command Line   : install -y nano bc
Packages Altered:
    Install bc-1.07.1-23.el10.x86_64 @baseos
    Install nano-8.1-3.el10.x86_64   @baseos
```

You now know **who** did what, **when**, with which return code and on exactly
which packages. That is what `dnf remove` will never tell you.

The gap between the two approaches is measured on this transaction. A `remove`
only undoes what you name:

```bash
sudo dnf remove -y nano
rpm -q nano bc
```

```text
package nano is not installed
bc-1.07.1-23.el10.x86_64
```

`bc` is still there: transaction 8 is only half undone. Whereas `undo` takes it
back in full:

```bash
sudo dnf history undo -y 8
```

```text
Removed:
  bc-1.07.1-23.el10.x86_64

Complete!
Warning, the following problems occurred while running a transaction:
  Package nevra "nano-8.1-3.el10.x86_64" not installed for action "Removed".
```

Two lessons in that single output. `undo` did remove `bc`, which had been
forgotten. And it **warns without failing** when part of the transaction has
already been undone: the command stays usable even on a partially cleaned
state.

`undo` is not limited to installations. The guide states that what has been
**upgraded is downgraded** to its previous version: that is the safety net after
an update that breaks a service. (This course did not run an update, that point
comes from the guide.)

> **Reflex: `dnf history list` before, `dnf history undo <ID>` after.** Note the
> highest identifier before your first command, and you will know exactly what
> to undo, and how far back.

### Looking at updates without applying them

A full update is an operation of its own, which restarts services and gets
planned. So you always start by **reading** before acting. Two commands do that
without changing anything:

```bash
dnf check-update
```

```text
almalinux-gpg-keys.x86_64              10.2-21.el10                    baseos
c-ares.x86_64                          1.34.6-2.el10_2                 baseos
cloud-init.noarch                      24.4-7.el10_2.1                 appstream
coreutils.x86_64                       9.5-8.el10_2                    baseos
dracut.x86_64                          107-8.el10_2                    baseos
```

```bash
dnf updateinfo summary
```

```text
Updates Information Summary: available
    31 Security notice(s)
         2 Critical Security notice(s)
        20 Important Security notice(s)
         6 Moderate Security notice(s)
         3 Low Security notice(s)
Security: kernel-core-6.12.0-211.34.1.el10_2.x86_64 is an installed security update
Security: kernel-core-6.12.0-211.7.3.el10_2.x86_64 is the currently running version
```

The last two lines say something important: a fixed kernel is **installed** but
the machine is still running on the old one. A security fix laid on disk is not
a security fix applied as long as the reboot has not happened.

According to the guide, the rest plays out in three commands this course does
**not** run (they change the whole system): `sudo dnf upgrade` updates
everything, `sudo dnf upgrade --security` restricts itself to security fixes,
and `dnf needs-restarting -r` answers the question "is a reboot needed". The
guide also points out that on DNF, **`update` and `upgrade` are two names for
the same command**, contrary to what the memory of APT suggests.

### Where DNF writes its logs

A very widespread mistake: looking for DNF traces in `journalctl`. There are
none, and the command does not say so plainly.

```bash
journalctl -u dnf
```

```text
-- No entries --
```

This is not "nothing happened", it is "this unit does not exist". The proof:

```bash
systemctl list-unit-files | grep -i dnf
```

```text
dnf-makecache.service                        static          -
dnf-system-upgrade-cleanup.service           static          -
dnf-system-upgrade.service                   disabled        disabled
dnf-makecache.timer                          enabled         enabled
```

No `dnf.service` at all: the only units concern the metadata cache and the
version upgrade. DNF logs into **flat files**:

```bash
sudo ls -l /var/log/dnf*.log
```

```text
-rw-r--r--. 1 root root  25082 Jul 22 14:39 /var/log/dnf.librepo.log
-rw-r--r--. 1 root root 108238 Jul 22 14:39 /var/log/dnf.log
-rw-r--r--. 1 root root   8432 Jul 22 14:39 /var/log/dnf.rpm.log
```

| File | Contents | When to read it |
|---|---|---|
| `/var/log/dnf.log` | DNF run, dependency resolution, plugins | A command fails or behaves strangely |
| `/var/log/dnf.rpm.log` | Real RPM actions: `Install`, `Upgrade`, `Erase` | To know what **really** changed on disk |
| `/var/log/dnf.librepo.log` | Downloads, mirrors, network errors | A repository is unreachable or slow |

`dnf.rpm.log` is the most readable for an audit: one timestamped line per
package touched.

```bash
sudo tail -4 /var/log/dnf.rpm.log
```

```text
2026-07-22T14:38:59+0000 SUBDEBUG Erase: httpd-tools-2.4.63-13.el10_2.4.x86_64
2026-07-22T14:38:59+0000 SUBDEBUG Erase: apr-util-1.6.3-23.el10_1.x86_64
2026-07-22T14:38:59+0000 SUBDEBUG Erase: apr-util-lmdb-1.6.3-23.el10_1.x86_64
2026-07-22T14:38:59+0000 SUBDEBUG Erase: apr-util-openssl-1.6.3-23.el10_1.x86_64
```

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `No match for argument: <package>` while the package exists | Stale metadata or disabled repository | `sudo dnf clean all && sudo dnf makecache`, then `dnf repolist all` |
| `dnf search <command>` finds nothing | `search` does not read package contents | `dnf provides "*/bin/<command>"` |
| `Error: No matches found. ... using a wildcard prefix` | Partial path given to `provides` | Full path, or pattern prefixed with `*/` |
| `No such command: config-manager` | Plugin missing (minimal installation) | `sudo dnf install dnf-plugins-core` |
| `journalctl -u dnf` returns nothing | No `dnf.service` unit exists | Read `/var/log/dnf.log` and `/var/log/dnf.rpm.log` |
| A package survives the `dnf remove` of what pulled it in | It is marked *userinstalled* | `dnf repoquery --userinstalled` to confirm, then `dnf history undo <ID>` |
| `rpm -qa` and `dnf list installed` do not give the same number | The `gpg-pubkey` pseudo-packages | Expected: `rpm -qa \| grep gpg-pubkey` |
| A transaction did damage | | `dnf history info <ID>` to read, `sudo dnf history undo <ID>` to undo |

### To undo everything

Note the current identifier **before** starting, and undo your transactions in
reverse order rather than chaining `remove` commands:

```bash
sudo dnf history list | head -5      # before: note the highest ID
# ... your operations ...
sudo dnf history undo -y <ID>        # one transaction, one undo
rpm -qa | wc -l                      # must find the starting count again
```

The final check is the package count. If it does not come back to its initial
value, then a transaction was not undone, or a package requested explicitly
stayed in place.
