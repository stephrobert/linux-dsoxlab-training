# Lab — tar, gzip, bzip2

## Reminder

[**Archives & compression on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/)

`tar` groups files into a single archive; the compression is a separate option:
`z` for gzip, `j` for bzip2. Common verbs: `c` create, `t` list, `x` extract.
`-f` names the file, `-C` sets the extraction directory, and naming a member
extracts only that one.

## The course

The examples below work on an `inventaire/` directory containing `stock.csv`,
`fournisseurs.json` and `historique.log`: the challenge, for its part, will ask
you for other files, other archives and other names. The point is to learn the
method, not to copy a line. All the output reproduced here comes from an
AlmaLinux 10 with GNU tar 1.35.

### Archiving is not compressing

The guide draws the distinction: **archiving** groups several files into one,
**compressing** reduces the size. These are two different operations, and `tar`
alone only does the first. The demonstration takes four commands:

```bash
du -sb inventaire
tar cf stock.tar inventaire
tar czf stock.tar.gz inventaire
ls -l stock.tar stock.tar.gz
```

```text
162	inventaire
-rw-r--r--. 1 ansible ansible 10240 Jul 22 14:20 stock.tar
-rw-r--r--. 1 ansible ansible   338 Jul 22 14:20 stock.tar.gz
```

162 bytes of data give a `tar` archive of **10,240 bytes**. It is sixty times
bigger than its content: `tar` writes a 512-byte header per member, then pads
with blocks of zeros. The final size always rounds up to a multiple of 10,240
bytes, which you can check by archiving directories of increasing size:

```text
  1 file      -> 10240 bytes
  5 files     -> 10240 bytes
 30 files     -> 40960 bytes
```

Add `z` and the file drops back to 338 bytes: it is the compression, not the
archiving, that makes things smaller.

The same surprise happens on a single file:

```bash
ls -l historique.log
gzip -k historique.log
ls -l historique.log.gz
```

```text
-rw-r--r--. 1 ansible ansible 55 Jul 22 14:16 historique.log
-rw-r--r--. 1 ansible ansible 78 Jul 22 14:16 historique.log.gz
```

55 bytes compressed into 78. On a tiny content, the header of the `gzip` format
costs more than what it saves. Compression only becomes worthwhile from a few
kilobytes upwards.

`gzip -k` keeps the original; **without `-k`, `gzip` replaces the file** and the
original disappears. That is the point the guide stresses, and it also holds for
`bzip2`, `xz` and `zstd`. To go back: `gunzip fichier.gz`, or `gzip -d
fichier.gz`.

### The three verbs, and what the archive really contains

`c` creates, `t` lists, `x` extracts. These three verbs are mutually exclusive:
a `tar` command contains exactly one. `-f` names the archive file and must be
followed immediately by that name.

Listing is the operation to perform **before** any extraction, because it
touches nothing on the disk:

```bash
tar tf stock.tar
```

```text
inventaire/
inventaire/stock.csv
inventaire/fournisseurs.json
inventaire/historique.log
```

With `v`, the listing becomes detailed and looks like an `ls -l`:

```bash
tar tvf stock.tar.gz
```

```text
drwxr-xr-x ansible/ansible   0 2026-07-22 14:20 inventaire/
-rw-r--r-- ansible/ansible  57 2026-07-22 14:20 inventaire/stock.csv
-rw-r--r-- ansible/ansible  50 2026-07-22 14:20 inventaire/fournisseurs.json
-rw-r--r-- ansible/ansible  55 2026-07-22 14:20 inventaire/historique.log
```

The listing goes to standard output: it is ordinary text, which you can redirect
to a file or filter with `grep`.

Two behaviours of GNU tar that cannot be guessed. First, the command above read
a gzip archive **without `z` being written**: when reading, `tar` recognises the
compressor on its own, and `z`, `j` or `J` are optional there. When creating, on
the other hand, it guesses nothing:

```bash
tar cf archive.tar.gz inventaire && file archive.tar.gz
```

```text
archive.tar.gz: POSIX tar archive (GNU)
```

Here is an **uncompressed** tar bearing a `.gz` name, an excellent way to
mislead the entire world, yourself included. Either you name the compressor, or
you use `-a` (`--auto-compress`), which deduces it from the extension:

```bash
tar caf archive.tar.gz inventaire && file archive.tar.gz
```

```text
archive.tar.gz: gzip compressed data, from Unix, original size modulo 2^32 10240
```

### The absolute path trap

This is what tells a usable archive from a treacherous one. `tar` records paths
**as they are given to it**. Give it an absolute path and it warns you:

```bash
tar czf absolu.tar.gz /srv/inventaire
```

```text
tar: Removing leading `/' from member names
```

The warning is not decorative: `tar` has removed the leading `/` and stored
**relative** paths.

```bash
tar tf absolu.tar.gz
```

```text
srv/inventaire/
srv/inventaire/fournisseurs.json
srv/inventaire/historique.log
srv/inventaire/stock.csv
```

The consequence, and this is where restores go wrong: the extraction recreates
that tree **in the current directory**, not at the original location.

```bash
mkdir -p restauration
tar xzf absolu.tar.gz -C restauration
find restauration | sort
```

```text
restauration
restauration/srv
restauration/srv/inventaire
restauration/srv/inventaire/fournisseurs.json
restauration/srv/inventaire/historique.log
restauration/srv/inventaire/stock.csv
```

A stray `srv/` has appeared. The data is there, but not where it was expected,
and the administrator who believes they restored `/srv/inventaire` has in fact
filled up their working directory.

**The countermeasure takes one option.** `-C` also serves at **creation** time:
it moves `tar` into the given directory before reading the files, which allows
archiving relative names only.

```bash
tar czf propre.tar.gz -C /srv inventaire
tar tf propre.tar.gz
```

```text
inventaire/
inventaire/fournisseurs.json
inventaire/historique.log
inventaire/stock.csv
```

No more warning, and paths that start at the right place. The restore becomes
explicit again: you choose the root with `-C`.

```bash
sudo tar xzf propre.tar.gz -C /srv
ls -l /srv/inventaire
```

```text
-rw-r--r--. 1 root root 50 Jul 22 14:20 fournisseurs.json
-rw-r--r--. 1 root root 55 Jul 22 14:20 historique.log
-rw-r--r--. 1 root root 57 Jul 22 14:20 stock.csv
```

> **The `-P` option exists, and it is precisely the one not to take.** `-P`
> (`--absolute-names`) asks `tar` to keep the `/`. Creation becomes silent, but
> the problem moves: it is now the **listing** that warns, because `tar`
> announces what it will do at extraction time.
>
> ```bash
> tar cPzf absolu-P.tar.gz /srv/inventaire   # no message
> tar tf absolu-P.tar.gz
> ```
>
> ```text
> tar: Removing leading `/' from member names
> /srv/inventaire/
> /srv/inventaire/fournisseurs.json
> /srv/inventaire/historique.log
> /srv/inventaire/stock.csv
> ```
>
> Hence the reading rule: **a `Removing leading '/'` warning at creation** means
> the archive will be relative; **the same warning at listing** means the
> archive contains real absolute paths, and that extracting such an archive with
> `-P` would write straight into the filesystem, at the location chosen by
> whoever built it. Never do that on an archive you did not write yourself.

### What tar preserves, and what it loses

The guide states that `tar` keeps "the tree, the permissions and the dates".
That is true, but incomplete: what is actually restored depends on the options
**and on the identity of whoever extracts**. Let us check rather than assume, on
a deliberately awkward set of files:

```bash
ls -l src
```

```text
-rwxr-x---. 1 root    root     7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-rw-rw-. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

A root-owned file in `0750`, a file in `0600` dated 2020, a lax file in `0666`,
a symbolic link and a hard link.

**First lesson, before extracting anything: an incomplete archive is created
without a sound.** Run by the ordinary user `ansible`, who cannot read
`deploie.sh`:

```bash
tar cf src.tar src
```

```text
tar: src/deploie.sh: Cannot open: Permission denied
tar: Exiting with failure status due to previous errors
```

`tar` returns a non-zero exit code but **writes the archive anyway**, minus the
unreadable file. A backup launched without checking its exit code may therefore
be unusable the day it is needed. Hence the rule: a backup of a system tree is
taken as `root`, and you test `$?`.

Let us start again with `sudo tar cf src.tar src`, then read what the archive
kept:

```bash
tar tvf src.tar
```

```text
drwxr-xr-x ansible/ansible   0 2026-07-22 14:17 src/
-rw------- ansible/ansible  16 2020-01-15 08:30 src/secret.conf
-rwxr-x--- root/root         7 2026-07-22 14:17 src/deploie.sh
lrwxrwxrwx ansible/ansible   0 2026-07-22 14:17 src/lien-sym -> secret.conf
hrw------- ansible/ansible   0 2020-01-15 08:30 src/lien-dur link to src/secret.conf
-rw-rw-rw- ansible/ansible   8 2026-07-22 14:17 src/partage.txt
```

Everything is there, including the nature of the links: `l` for the symbolic
link with its target, `h` for the hard link with the `link to` mention. A hard
link is **not** stored twice: `tar` records the content once and notes the
relation.

That leaves the three ways of extracting this same archive.

**Ordinary user, without `-p`**:

```bash
tar xf src.tar -C sans-p && ls -l sans-p/src
```

```text
-rwxr-x---. 1 ansible ansible  7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-r--r--. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

`partage.txt` went from `0666` to `0644`: the permissions were filtered by the
session `umask`, `0022` here. And the owners have all become `ansible`.

**Ordinary user, with `-p`**:

```bash
tar xpf src.tar -C avec-p && ls -l avec-p/src
```

```text
-rwxr-x---. 1 ansible ansible  7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-rw-rw-. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

`0666` is back: `-p` (`--preserve-permissions`) bypasses the `umask`. On the
other hand **the owners are still not restored**: `deploie.sh` stays
`ansible:ansible` while the archive says `root/root`. This is not a weakness of
`tar`, it is the kernel: an ordinary user cannot give a file away to someone
else.

**As root**:

```bash
sudo tar xf src.tar -C as-root && ls -l as-root/src
```

```text
-rwxr-x---. 1 root    root     7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-rw-rw-. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

Without writing `-p`, `root` gets the exact permissions **and** the original
owners: for root, `-p` is the default behaviour, and so is restoring owners.

In all three cases, the 2020 timestamps came back and the symbolic link stayed a
link. So did the hard link, which an `ls -li` confirms after extraction, both
names sharing the same inode number:

```text
25672526 -rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
25672526 -rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

| What is restored | user, without `-p` | user, with `-p` | root |
|---|---|---|---|
| Tree and content | yes | yes | yes |
| Modification date | yes | yes | yes |
| Symbolic and hard links | yes | yes | yes |
| Exact permissions | no, filtered by the `umask` | yes | yes, by default |
| Owner and group | no | no | yes, by default |

**What the guide does not say: the SELinux context is lost by default.** On this
AlmaLinux in `Enforcing`, a file labelled `etc_t` comes out of the tar labelled
according to the destination directory:

```bash
ls -Z src/secret.conf                     # unconfined_u:object_r:etc_t:s0
tar cf ctx.tar src
tar xf ctx.tar -C ctx-defaut
ls -Z ctx-defaut/src/secret.conf
```

```text
unconfined_u:object_r:user_home_t:s0 ctx-defaut/src/secret.conf
```

For a system backup on a distribution with SELinux, you have to ask for it
explicitly, **on both sides**:

```bash
sudo tar --selinux --xattrs -cf ctx2.tar src
sudo tar --selinux --xattrs -xf ctx2.tar -C ctx-selinux
ls -Z ctx-selinux/src/secret.conf
```

```text
unconfined_u:object_r:etc_t:s0 ctx-selinux/src/secret.conf
```

### Choosing a compressor: measure rather than copy a table

`z` calls `gzip`, `j` calls `bzip2`, `J` (uppercase) calls `xz`, and `--zstd`
calls `zstd`. First reflex: check which ones **exist** on the machine, because
`tar` only invokes them.

```bash
for c in gzip bzip2 xz zstd; do printf "%-6s " $c; command -v $c || echo ABSENT; done
```

```text
gzip   /usr/bin/gzip
bzip2  ABSENT
xz     /usr/bin/xz
zstd   ABSENT
```

On an AlmaLinux 10 installed as minimal, **`bzip2` and `zstd` are not there**,
and neither are `zip`/`unzip`. Which gives, if you ask for `j` anyway:

```bash
tar cjf essai.tar.bz2 inventaire ; echo "rc=$?"
```

```text
/bin/sh: line 1: bzip2: command not found
tar: essai.tar.bz2: Cannot write: Broken pipe
tar: Child returned status 127
tar: Error is not recoverable: exiting now
rc=2
```

An obscure message, and an `essai.tar.bz2` file of **0 bytes** left on the disk.
The fix is a `sudo dnf install bzip2` (or `sudo apt install bzip2` on Debian and
Ubuntu).

Once the four tools are present, the comparison takes one loop. Here are the
measurements obtained on a 600,000-line web log (uncompressed `tar` archive:
50,636,800 bytes), with each compressor's default options, on a 1 vCPU VM:

| Option | File | Size | Share of the tar | Time |
|---|---|---|---|---|
| `-z` (gzip) | `.tar.gz` | 8,215,406 | 16.2% | 0.92 s |
| `-j` (bzip2) | `.tar.bz2` | 4,713,638 | 9.3% | 3.82 s |
| `-J` (xz) | `.tar.xz` | 5,979,348 | 11.8% | 22.92 s |
| `--zstd` | `.tar.zst` | 8,878,856 | 17.5% | 0.15 s |

And on a completely different data set, a copy of `/usr/share/doc` (`tar`
archive: 24,033,280 bytes), that is thousands of small documentation files:

| Option | Size | Share of the tar | Time |
|---|---|---|---|
| `-z` (gzip) | 8,299,696 | 34.5% | 0.72 s |
| `-j` (bzip2) | 7,063,641 | 29.4% | 1.24 s |
| `-J` (xz) | 6,273,336 | 26.1% | 8.76 s |
| `--zstd` | 8,044,571 | 33.5% | 0.10 s |

Three lessons these figures establish, and that no table learned by heart gives:

1. **The ranking depends on the data.** On the log, `bzip2` beats `xz` by two
   and a half points; on the documentation, `xz` takes the lead again. The
   "gzip, then bzip2, then xz" hierarchy you read everywhere is a tendency, not
   a law.
2. **The time gap is out of all proportion with the size gap.** On the log, `xz`
   takes twenty-five times longer than `gzip` to gain four points of size. On a
   nightly backup the trade-off holds, on an interactive transfer much less so.
3. **`zstd` changes the terms of the problem.** Here it compresses six times
   faster than `gzip` for a comparable size, which explains its rapid adoption.
   The packages of this AlmaLinux already use it:
   `rpm -q --qf '%{PAYLOADCOMPRESSOR}\n' bash tar gzip` answers `zstd` three
   times.

Decompression follows the same logic, measured on the log: 0.17 s for gzip,
0.97 s for bzip2, 0.24 s for xz, 0.06 s for zstd. Note that `xz`, very slow to
compress, decompresses almost as fast as `gzip`. For an archive written once and
read often, that is an argument.

Each compressor brings its own reading utilities, which avoid decompressing
before searching:

```bash
zgrep -c " 500 " frontal.log.gz
```

```text
100030
```

`zcat`, `zgrep` and `zless` come with `gzip`; `bzcat` with `bzip2`, `xzcat` with
`xz`, `zstdcat` with `zstd` (an `rpm -qf` on each one confirms it). On a 50 MiB
compressed log, that is the difference between an immediate command and a
detour through the disk.

### Pulling a single file out of an archive

A real restore almost always consists of recovering one file, not the whole
tree. Naming a member after the archive name limits the operation to that
member:

```bash
tar xzf propre.tar.gz -C cible inventaire/stock.csv
find cible | sort
```

```text
cible
cible/inventaire
cible/inventaire/stock.csv
```

Three points to note. The member is designated **exactly as `tar tf` displays
it**, here `inventaire/stock.csv` and not `stock.csv`. The stored tree is
recreated under the target, hence the intermediate `cible/inventaire/`. And the
directory given to `-C` must exist beforehand, otherwise:

```text
tar: /tmp/pas-la: Cannot open: No such file or directory
tar: Error is not recoverable: exiting now
```

Getting a member name wrong does not go unnoticed, which is good news:

```bash
tar xzf propre.tar.gz -C cible inventaire/absent.txt ; echo "rc=$?"
```

```text
tar: inventaire/absent.txt: Not found in archive
tar: Exiting with failure status due to previous errors
rc=2
```

Three options complete the toolkit:

```bash
tar xzf propre.tar.gz -C cible2 --wildcards "inventaire/*.json"
tar xzf propre.tar.gz -C cible3 --strip-components=1
tar cf sans-log.tar -C /srv --exclude="*.log" inventaire
```

`--wildcards` pulls out only the matching files: the pattern must be quoted so
that it is `tar`, and not the shell, that interprets it. `--strip-components=1`
removes the first path level, which puts the three files directly in `cible3/`,
without the intermediate `inventaire/`. `--exclude` is used at creation as well
as at extraction; here, at creation:

```text
inventaire/
inventaire/stock.csv
inventaire/fournisseurs.json
```

> **An extraction overwrites without asking.** A member bearing the name of an
> existing file replaces it, silently. The `-k` option (`--keep-old-files`)
> reverses that behaviour: `tar` then refuses the member and exits with an
> error, but the local file stays intact.
>
> ```text
> tar: marqueur.txt: Cannot open: File exists
> tar: Exiting with failure status due to previous errors
> ```
>
> That is why you list before extracting, and why you extract into an empty
> directory when in doubt.

### Checking an archive

`tar df` (`--diff`, or `--compare`) re-reads the archive and compares it with
the disk. Silence and exit code 0 mean everything matches:

```bash
tar df propre.tar.gz -C /srv ; echo "rc=$?"
```

```text
rc=0
```

Let us modify an original file and start again:

```bash
sudo sh -c 'echo modif >> /srv/inventaire/stock.csv'
tar df propre.tar.gz -C /srv ; echo "rc=$?"
```

```text
inventaire/stock.csv: Mod time differs
inventaire/stock.csv: Size differs
rc=1
```

This is the check most backup scripts lack: it proves the archive is re-readable
and faithful, without writing anything to the disk.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `tar: Removing leading '/' from member names` at creation | an absolute path was given; the archive will be relative, plan for `-C` at extraction, or archive with `-C` |
| The same message at **listing** time | the archive contains real absolute paths (created with `-P`): extract with care, never with `-P` |
| The extraction creates a stray `srv/`, `home/` or `etc/` | the archive had been created from an absolute path; move to the right root with `-C` |
| `Cannot open: Permission denied` then `Exiting with failure status` | archive created without read permissions; it exists but is **incomplete**, redo it as root |
| `bzip2: command not found` then `Child returned status 127` | the compressor is not installed; `sudo dnf install bzip2` (or `zstd`, `xz`) |
| `gzip: stdin: not in gzip format` | wrong compressor requested (`z` on a bzip2 archive); leave it out, GNU tar detects it on its own |
| An archive named `.tar.gz` that `file` reports as uncompressed | `tar cf` does not guess from the extension: write `tar czf` or `tar caf` |
| Binary dumped into the terminal | `-f` forgotten: `tar` wrote to standard output |
| `Not found in archive` | the member is not named as `tar tf` displays it (full path expected) |
| `Cannot open: No such file or directory` on the `-C` target | the directory does not exist, `tar` does not create it |
| A local file replaced after extraction | normal behaviour; `-k` to forbid it |
| The permissions are not those of the archive | extraction as an ordinary user without `-p`: the `umask` filtered them |
| The owner is not restored despite `-p` | only `root` can restore owners |
| The SELinux context changed after the restore | `--selinux --xattrs` are needed at creation **and** at extraction |
| `gzip: fichier already has .gz suffix -- unchanged` | the file is already compressed |
| The original file disappeared after `gzip` | `gzip` replaces; `gzip -k` to keep it |

To undo everything and start over:

```bash
rm -rf ~/cours
sudo rm -rf /srv/inventaire
```
