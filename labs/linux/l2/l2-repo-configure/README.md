# Lab — configure a dnf repository

## Reminder

[**dnf on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

A repository is defined by an INI `.repo` file in `/etc/yum.repos.d/`: `[id]`,
`name`, `baseurl` (or `mirrorlist`), `enabled`, `gpgcheck` and `gpgkey`. Keep
`gpgcheck=1` so that packages are verified by signature. `dnf repolist` shows
the enabled repositories, `dnf repolist --all` all the configured ones.

## The course

The examples below build then declare a **local** repository named
`demo-local`, served from `/opt/depot-demo`: the challenge will ask you for
another repository, under another name and with another source. The point is to
learn the method, not to copy a line. Every output shown was produced on an
AlmaLinux 10.2 (`dnf` 4.20.0).

### What dnf already knows, and where it is written

Before adding anything, look at what is there. `dnf repolist` shows only the
**enabled** repositories; `dnf repolist all` (or `--all`, both forms work) adds
the disabled ones and a `status` column:

```bash
dnf repolist
dnf repolist all
```

```text
repo id                repo name                            status
appstream              AlmaLinux 10 - AppStream             enabled
baseos                 AlmaLinux 10 - BaseOS                enabled
crb                    AlmaLinux 10 - CRB                   enabled
extras                 AlmaLinux 10 - Extras                enabled
highavailability       AlmaLinux 10 - HighAvailability      disabled
[...]
```

A package that is "not found" comes nine times out of ten from a `disabled`
repository, not from a package that does not exist. These repositories are
described in INI files under `/etc/yum.repos.d/` (`almalinux-baseos.repo`,
`almalinux-appstream.repo`…). One file can contain **several sections**, one per
repository: it is the name between brackets that serves as the identifier for
dnf, not the file name.

```ini
[appstream]
name=AlmaLinux $releasever - AppStream
mirrorlist=https://mirrors.almalinux.org/mirrorlist/$releasever/appstream
enabled=1
gpgcheck=1
metadata_expire=86400
[...]
```

Two variables are substituted by dnf: `$releasever` (the major version of the
distribution) and `$basearch` (the architecture). A source is declared either
with `baseurl` (a direct URL: `https://`, `http://` or `file://`), or with
`mirrorlist` (a URL that returns a list of mirrors to query). The repositories
shipped by AlmaLinux use the second form.

### Building a local repository

A repository is nothing more than a directory of RPMs together with a
`repodata/` subdirectory describing its content. `createrepo_c` produces that
`repodata/`. First fetch an RPM without installing it, with the `download`
plugin:

```bash
sudo dnf install -y createrepo_c
sudo mkdir -p /opt/depot-demo
cd /opt/depot-demo && sudo dnf download bc
sudo createrepo_c /opt/depot-demo
```

```text
Directory walk started
Directory walk done - 1 packages
Pool started (with 5 workers)
Pool finished
```

The directory now contains the RPM and a `repodata/` subdirectory:

```bash
ls /opt/depot-demo /opt/depot-demo/repodata
```

```text
/opt/depot-demo:
bc-1.07.1-23.el10.x86_64.rpm  repodata

/opt/depot-demo/repodata:
5099fc6b...-filelists.xml.zst  e63494b7...-other.xml.zst
cd8a8c61...-primary.xml.zst    repomd.xml
```

`repomd.xml` is the index dnf reads first: it points to the three other files,
including `primary` which lists the packages.

> **Why a local repository?** You control its content and the demonstration does
> not depend on the network. A remote repository is declared exactly the same
> way, with an `http(s)://` `baseurl` instead of `file://`: the guide gives an
> example of it.

### Declaring the repository and checking that dnf counts it

Create a file in `/etc/yum.repos.d/`. The `.repo` extension is mandatory
(verified: renamed to `.conf`, the repository disappears from `repolist`), the
rest of the name is free:

```ini title="/etc/yum.repos.d/demo-local.repo"
[demo-local]
name=Depot local de demonstration
baseurl=file:///opt/depot-demo
enabled=1
gpgcheck=1
```

Mind the syntax of `file://`: three slashes in total, because `file://` is the
scheme and `/opt/depot-demo` the absolute path. `dnf repolist` then lists the
new repository, but listing does not prove that dnf can use it: `-v` shows the
**number of packages** actually seen, which is the real proof.

```bash
dnf repolist
dnf repolist -v --repo demo-local
```

```text
Repo-id            : demo-local
Repo-pkgs          : 1
Repo-baseurl       : file:///opt/depot-demo
Repo-filename      : /etc/yum.repos.d/demo-local.repo
```

`Repo-pkgs : 1`: dnf has read the metadata and finds one package in it. The
nuance was verified on the machine: a repository whose `baseurl` points to a
directory with no `repodata/` **still shows up** in `dnf repolist`, and it is
only when dnf tries to read the metadata that it fails.

### The metadata cache, and why it lies

dnf does not re-read the metadata on every command, it caches it. Add a second
package to the repository and rebuild its index:

```bash
cd /opt/depot-demo && sudo dnf download dos2unix
sudo createrepo_c --update /opt/depot-demo
dnf repolist -v --repo demo-local | grep Repo-pkgs
```

```text
Repo-pkgs          : 1
```

Still 1, while the directory holds 2. You must invalidate the cache then rebuild
it:

```bash
dnf clean metadata
dnf repolist -v --repo demo-local | grep Repo-pkgs
```

```text
Cache was expired
29 files removed
Repo-pkgs          : 2
```

> **The cache of `root` and the cache of your account are two different
> caches.** Verified on the machine: after `sudo dnf clean metadata`,
> `sudo dnf repolist` announced 2 packages while the `dnf repolist` of the
> unprivileged account still announced 1. The root cache is in `/var/cache/dnf`,
> that of an ordinary user in `/var/tmp/dnf-<user>-<random>`. Clean the cache
> **of the account with which you observe the problem**.

`dnf makecache` rebuilds the cache without waiting for the next command;
`dnf clean all` goes further and also deletes the downloaded RPMs.

### The GPG signature, the real subject

`gpgcheck=1` requires each RPM to be signed by a key **present in the RPM
database**. Without that key, the installation stops. Here is the exact message,
obtained by temporarily removing the AlmaLinux key from the database:

```bash
sudo dnf install -y --repo demo-local bc
```

```text
Downloading Packages:
Public key for bc-1.07.1-23.el10.x86_64.rpm is not installed
Error: GPG check FAILED
```

The package was indeed downloaded: it is at verification time that dnf refuses.
`rpm -K` asks the same question about an RPM file, without installing anything,
and it is the diagnostic tool to know:

```bash
rpm -K /opt/depot-demo/bc-1.07.1-23.el10.x86_64.rpm
```

```text
bc-1.07.1-23.el10.x86_64.rpm: digests SIGNATURES NOT OK
```

Two ways to import the key. The first, manual, with `rpm --import`:

```bash
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-10
rpm -qa gpg-pubkey --qf '%{NAME}-%{VERSION}-%{RELEASE} : %{SUMMARY}\n'
```

```text
gpg-pubkey-e37ed158-65785fa9 : Fedora (epel10) <epel@fedora...> key
gpg-pubkey-c2a1e572-668fe8ef : AlmaLinux OS 10 <packager@alma...> key
```

Imported keys are stored in the RPM database as fake packages named
`gpg-pubkey-*`: this is how you inventory the trusted keys of a machine. After
the import, `rpm -K` answers `digests signatures OK` and the installation goes
through.

The second way is to let dnf do the work, by adding `gpgkey=` to the `.repo`
file. That directive takes a URL: `https://…` for a key published by a third
party vendor, `file://…` for a key already on disk. The keys shipped with the
system are in `/etc/pki/rpm-gpg/`:

```ini
gpgkey=<URL ou file:// de la clé publique du dépôt>
```

dnf then fetches it, displays it and imports it:

```text
Importing GPG key 0xC2A1E572:
 Userid     : "AlmaLinux OS 10 <packager@almalinux.org>"
 Fingerprint: EE6D B7B9 8F5B F5ED D9DA 0DE5 DEE5 C11C C2A1 E572
 From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-10
Key imported successfully
```

Without `-y`, dnf shows the fingerprint then **asks for confirmation** (`Is this
ok [y/N]`): that is the moment to compare it with the one published by the
vendor. Answering no gives `Didn't install any keys` then
`Error: GPG check FAILED`. In a script, outside a terminal, dnf refuses
outright: `Refusing to automatically import keys when running unattended. Use
"-y" to override.`

That leaves the bad solution, the one that works. With `gpgcheck=0`, installing
the same package succeeds while the key is still missing:

```text
Installed:
  bc-1.07.1-23.el10.x86_64
Complete!
```

Nothing was verified: as the guide says, a repository without `gpgcheck` accepts
any RPM modified in transit. `gpgcheck=0` repairs nothing, it removes the check
that would have reported the problem to you. The real fix is to import the right
key.

### Enabling, disabling, arbitrating between repositories

Editing the file by hand works, but `dnf config-manager` does the same job with
no risk of a typo. It **rewrites** the `.repo` file:

```bash
sudo dnf config-manager --set-disabled demo-local
dnf repolist all | grep demo-local
sudo dnf config-manager --set-enabled demo-local
```

```text
demo-local             Depot local de demonstration         disabled
```

`--setopt` sets any other directive. With `--save`, the value is written into
the file; without `--save`, it holds for this command only. The two answer
different needs: lasting against one-off.

```bash
sudo dnf config-manager --setopt=demo-local.priority=10 --save
dnf config-manager --dump demo-local | grep -E '^(priority|enabled) '
```

```text
enabled = 1
priority = 10
```

`priority` arbitrates between two repositories that provide **the same
package**: the **smallest** number wins, the default value is 99. The `bc`
package exists both in `baseos` and in the demonstration repository, which lets
you check it from both sides:

```bash
sudo dnf info bc | grep -E '^(Name|Repository)'      # priority=10
sudo dnf config-manager --setopt=demo-local.priority=100 --save
sudo dnf info bc | grep -E '^(Name|Repository)'      # priority=100
```

```text
Name         : bc
Repository   : demo-local
[...]
Name         : bc
Repository   : baseos
```

For a one-off need, `--disablerepo` and `--enablerepo` ignore or enable a
repository for the duration of one command, without changing anything on disk:

```bash
sudo dnf info bc --disablerepo=demo-local | grep Repository
```

```text
Repository   : baseos
```

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Warning: failed loading '/etc/.../x.repo', skipping.` then the repository has disappeared from `repolist` | INI syntax error (line before the first `[section]`, missing bracket). dnf ignores **the whole file** and still returns code 0 |
| The repository shows up in `repolist` but every command fails on `Curl error (37)` / `Cannot download repomd.xml` | wrong `baseurl`, unreachable source, or directory with no `repodata/` (run `createrepo_c`). The message names the exact path attempted: read it |
| `Public key for <package>.rpm is not installed` / `Error: GPG check FAILED` | key missing from the RPM database: `rpm --import`, or add `gpgkey=` to the `.repo` |
| A package added to the repository stays invisible | metadata cached: `createrepo_c --update` then `dnf clean metadata` (with **the same account** as the one observing the problem) |
| `No such command: config-manager` | plugin missing: `sudo dnf install dnf-plugins-core` (already present on AlmaLinux 10) |

To undo everything and start over:

```bash
sudo dnf remove -y bc
sudo rm -f /etc/yum.repos.d/demo-local.repo
sudo rm -rf /opt/depot-demo
sudo dnf clean all
```

Removing the `.repo` file is enough to make the repository disappear, but
**not** to remove the packages already installed from it, nor the imported GPG
key. A key is removed like a package, by the name noted above:
`sudo rpm -e gpg-pubkey-c2a1e572-668fe8ef`. Only do this for a key you added
yourself: removing the one from the distribution makes any later installation
fail.
