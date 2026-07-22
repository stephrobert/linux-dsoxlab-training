# Lab — Debian package management (apt/dpkg)

## Reminder

[**apt on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/)

`apt-get install|remove` manages packages and their dependencies; `apt-mark hold`
freezes a version so that `apt upgrade` skips it (`apt-mark showhold` lists the
holds); `dpkg -l <package>` shows the installation state; `dpkg -S <file>` says
which package owns a file. These are the Debian counterparts to `dnf` /
`rpm -qf`.

## The course

The examples below work on `cowsay`, `cowsay-off`, `sl` and `gzip`: the
challenge will ask you for another package. Learn the install / check / mark /
undo loop, do not copy a line.

### Where the machine stands

Three questions before touching anything: which tool versions, how many packages
installed, and how they are marked.

```bash
lsb_release -a | grep -E 'Description|Codename'
apt --version ; dpkg --version | head -1 ; dpkg -l | grep -c '^ii'
apt-mark showmanual | wc -l ; apt-mark showauto | wc -l ; apt-mark showhold
```

```text
Description:	Ubuntu 24.04.4 LTS
Codename:	noble
apt 2.8.3 (amd64)
Debian 'dpkg' package management program version 1.22.6 (amd64).
672
50
622
```

Always state your versions: the repository format, the error messages and even
the existence of some sub-commands change from one APT version to the next. All
the outputs in this course come from that machine.

`showhold` returns nothing: no package is frozen to start with. Remember these
three numbers, they are your points of comparison: after an installation and its
undoing, you must land back exactly on them, markings included.

### Three tools, one hierarchy: dpkg, apt-get, apt

`dpkg` installs **a `.deb` file** and nothing else: it knows nothing about
repositories and fetches no dependency. Get hold of a package that depends on
another one, absent from the machine:

```bash
cd /tmp && apt-get download cowsay-off
sudo dpkg -i /tmp/cowsay-off_3.03+dfsg2-8_all.deb
```

```text
Unpacking cowsay-off (3.03+dfsg2-8) ...
dpkg: dependency problems prevent configuration of cowsay-off:
 cowsay-off depends on cowsay (>= 3.03+dfsg2-3); however:
  Package cowsay is not installed.
dpkg: error processing package cowsay-off (--install):
 dependency problems - leaving unconfigured
```

`dpkg` exits with an error (code 1), but the package is nevertheless **unpacked**
on the disk, simply not **configured**. `dpkg -l cowsay-off` says so in its state
column:

```text
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
||/ Name           Version      Architecture Description
+++-==============-============-============-==========================
iU  cowsay-off     3.03+dfsg2-8 all          configurable talking cow
```

The two letters are read with the legend printed just above: `i` = **desired**
state *Install*, `U` = **actual** state *Unpacked*. `iU` is a half-installed
package, and an upper-case letter in the second column always signals a problem.
It is `apt` that knows how to repair it, because it knows the repositories:

```bash
sudo apt-get install -f -y
```

```text
Correcting dependencies... Done
The following additional packages will be installed:
  cowsay
0 upgraded, 1 newly installed, 0 to remove and 44 not upgraded.
1 not fully installed or removed.
[...]
```

That leaves the third command. **`apt` and `apt-get` are not the same thing**:
`apt` is the interactive interface, `apt-get` the stable interface for scripts,
and APT reminds you of it as soon as its output is no longer a terminal.

```bash
apt policy bash              # in a terminal: no warning
apt policy bash | cat        # redirected output
```

```text
WARNING: apt does not have a stable CLI interface. Use with caution in scripts.
[...]
```

The warning only appears in the second case: APT detects that it is being read
by a program and warns that its display may change without notice. In a script,
write `apt-get install -y` and `apt-cache policy`, which never print it.

### The cache and the repositories

`apt update` updates **no software** at all: it downloads the **indexes** of the
repositories. On a machine whose indexes are stale, a perfectly existing package
becomes untraceable:

```bash
ls -l --time-style=+%F /var/lib/apt/lists/*noble_main*Packages
sudo apt-get install -y sl
apt policy sl
```

```text
-rw-r--r-- 1 root root 7165069 2024-04-24 [...]noble_main_binary-amd64_Packages
E: Unable to locate package sl
```

`apt policy sl` returns nothing at all: APT has never heard of that package. The
reflex is the same in both cases, refresh the indexes:

```bash
sudo apt-get update
```

```text
Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease
Get:3 http://archive.ubuntu.com/ubuntu noble-updates InRelease [126 kB]
Get:12 http://archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages [1676 kB]
[...]
Fetched 7740 kB in 1s (6620 kB/s)
```

`Hit` signals an unchanged index, `Get` an actual download. The repositories
queried are declared in `/etc/apt/sources.list.d/`. On Ubuntu 24.04, the old
`/etc/apt/sources.list` file only contains a pointer: "*Ubuntu sources have moved
to the /etc/apt/sources.list.d/ubuntu.sources file, which uses the deb822
format*". That format replaces the historical single line with a block of named
fields, in a `.sources` file:

```text
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: noble noble-updates noble-backports
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

`Signed-By` is the security field: it ties the repository to its signing key and
replaces the old `apt-key`, removed since Debian 12.

Once the indexes are up to date, `apt-cache policy` answers the question "where
would this package come from":

```bash
apt-cache policy cowsay
```

```text
cowsay:
  Installed: 3.03+dfsg2-8
  Candidate: 3.03+dfsg2-8
  Version table:
 *** 3.03+dfsg2-8 500
        500 http://archive.ubuntu.com/ubuntu noble/universe amd64 Packages
        100 /var/lib/dpkg/status
```

`Installed` is the version present, `Candidate` the one that would be installed,
and the table gives the origin with its **priority** (500 for a repository, 100
for the local `dpkg` database). The package comes from the `universe` component,
which explains the earlier failure: the `universe` index had never been
downloaded.

To see what is pending without applying anything:

```bash
apt list --upgradable 2>/dev/null | tail -n +2 | wc -l
sudo apt-get -s upgrade | grep -E '^[0-9]+ upgraded'
sudo apt-get -s full-upgrade | grep -E '^[0-9]+ upgraded'
```

```text
44
40 upgraded, 0 newly installed, 0 to remove and 4 not upgraded.
44 upgraded, 6 newly installed, 0 to remove and 0 not upgraded.
```

`-s` is a simulation and changes nothing. `upgrade` leaves four packages aside,
listed under `The following packages have been kept back`: those that would
require **adding** packages, which `upgrade` refuses to do. `full-upgrade`
accepts, and installs six more packages.

### Querying dpkg: contents, owner, state

`dpkg` answers the **local** questions. Three options cover daily use.

```bash
dpkg -s cowsay | head -2        # state and metadata
dpkg -L cowsay | sed -n '3,4p'  # files shipped by the package
dpkg -S /usr/games/cowsay       # which package owns this file
```

```text
Package: cowsay
Status: install ok installed
/usr/games
/usr/games/cowsay
cowsay: /usr/games/cowsay
```

`dpkg -S` answers "where does this binary come from". Mind its limit: it only
knows the files **shipped by a package**. A file created by the system or by you
has no owner, and the command exits with an error: `dpkg -S /etc/hostname`
answers `dpkg-query: no path found matching pattern /etc/hostname`.

### Manual, automatic, frozen: the APT markings

APT remembers **why** each package is there. Take the installation done above:
`apt-mark showmanual cowsay cowsay-off` returns only `cowsay-off`, put in place
by hand, and `apt-mark showauto cowsay cowsay-off` returns only `cowsay`, which
came in as a dependency.

This distinction drives the behaviour of removal, and it is **the** difference to
know with `dnf`:

```bash
sudo apt-get remove -y cowsay-off && dpkg -l cowsay | tail -1
```

```text
The following package was automatically installed and is no longer required:
  cowsay
Use 'sudo apt autoremove' to remove it.
[...]
Removing cowsay-off (3.03+dfsg2-8) ...
ii  cowsay         3.03+dfsg2-8 all          configurable talking cow
```

`cowsay` stayed. Unlike `dnf remove`, **`apt remove` does not clean up the
dependencies that became orphaned**: it reports them and waits for a second
command, `sudo apt-get autoremove --dry-run | grep '^Remv'` then printing
`Remv cowsay [3.03+dfsg2-8]`.

The third marking is the **freeze**: `apt-mark hold` prevents an update from
touching a package.

```bash
sudo apt-mark hold sl && apt-mark showhold && dpkg -l sl | tail -1
```

```text
sl set on hold.
sl
hi  sl             5.02-1       amd64        Correct you if you type `sl' by mistake
```

`hi` replaces `ii`: the desired state is no longer *Install* but *Hold*. The
freeze also shows in `dpkg --get-selections sl`, which returns `sl hold`.

A point the guide does not spell out: **the freeze blocks the automatic update,
not an explicit request**. On a frozen package with a pending update, compare the
two simulations:

```bash
sudo apt-get -s upgrade | grep -A1 'kept back'
sudo apt-get -s install gzip | grep -A1 'held packages'
```

```text
The following packages have been kept back:
  gzip [...]
The following held packages will be changed:
  gzip
```

`upgrade` sets the package aside; `install <package>` warns and then goes ahead.
A hold protects you from a mass update, it does not protect you from yourself.
`sudo apt-mark unhold <package>` cancels the freeze.

### What APT records, and what it cannot undo

This is the most striking gap with RHEL: **there is no equivalent of
`dnf history undo`**. The sub-command does not exist, `apt history` answers
`E: Invalid operation history`. What does exist is two plain-text logs:
`/var/log/apt/history.log` records the APT transactions with the command typed
and its author, `/var/log/dpkg.log` goes one level down and records every
**state change**.

```bash
sudo tail -5 /var/log/apt/history.log
sudo grep cowsay-off /var/log/dpkg.log | head -3
```

```text
Start-Date: 2026-07-22  17:37:29
Commandline: apt-get remove -y cowsay-off
Requested-By: ansible (1001)
Remove: cowsay-off:amd64 (3.03+dfsg2-8)
End-Date: 2026-07-22  17:37:29
2026-07-22 17:36:57 install cowsay-off:all <none> 3.03+dfsg2-8
2026-07-22 17:36:57 status half-installed cowsay-off:all 3.03+dfsg2-8
2026-07-22 17:36:57 status unpacked cowsay-off:all 3.03+dfsg2-8
```

Compare the timestamps: the `dpkg -i` of 17:36:57 appears in `dpkg.log` but
**not** in `history.log`, whose first entry for the session is the
`apt-get install -f` of 17:37:05. An audit run on the APT log alone therefore
misses everything put in place by hand. Lacking an `undo`, the restoration is
done with the markings: `apt-mark showmanual` says what you asked for,
`apt autoremove` removes the rest.

### Troubleshooting and return to the initial state

| Symptom | Likely cause | Fix |
|---|---|---|
| `E: Unable to locate package <p>`, or `apt policy <p>` silent | Index missing or stale | `sudo apt-get update`, then `apt-cache policy <p>` |
| `dependency problems - leaving unconfigured` | `dpkg -i` without the dependencies | `sudo apt-get install -f` |
| `iU` state in `dpkg -l` | Package unpacked, not configured | `sudo apt-get install -f` |
| `WARNING: apt does not have a stable CLI interface` | `apt` used in a script | `apt-get` / `apt-cache` |
| A package remains after `apt remove` | It is marked *auto* and was not requested | `sudo apt autoremove` |
| A package refuses to be updated | It is frozen | `apt-mark showhold`, then `unhold` |
| `dpkg was interrupted` (per the guide) | Installation interrupted | `sudo dpkg --configure -a` |

To undo everything, note your three numbers **before** starting, then:

```bash
sudo apt-mark unhold <package>         # unfreeze first
sudo apt-get purge -y <package>        # purge = package + configuration
sudo apt-get autoremove --purge -y     # the orphans
dpkg -l | grep -c '^ii' ; apt-mark showhold   # initial count, empty holds
```

Safer still, compare lists rather than counts: keep the output of
`dpkg -l | grep '^ii' | awk '{print $2}' | sort` before and after, then `diff`.
Two equal counts can hide one package added and another one removed.
