# Lab — persistent SMB/CIFS mount

## Reminder

[**SMB on the companion guide**](https://blog.stephane-robert.info/docs/services/stockage/smb/)

A CIFS mount needs the `cifs-utils` package and an authenticated share:
`mount -t cifs //<server>/<share> <mountpoint> -o credentials=<file>`.

Two things make it production-grade:

- **`_netdev`** in `/etc/fstab`: the mount is classified as a network mount;
- a **credentials file** (`username=` / `password=` lines) in `0600`, because
  `/etc/fstab` is world-readable and must never hold a password.

## The course

The examples below mount a `documents` share on `/mnt/documents`, with an SMB
account `archiviste`: the challenge will be about another share, another mount
point and another account. Learn the sequence, do not copy a line. All the output
comes from an **Ubuntu 24.04.4** VM (kernel **6.8.0-134-generic**), with **Samba
4.19.5** and **cifs-utils 2:7.0**, the same image as the lab.

### The setting: server and client on the same machine

To learn, a single machine is enough: you set up a small Samba server on it and
connect to it through `127.0.0.1`. The `samba` package provides the server,
`cifs-utils` the client (it brings the `/sbin/mount.cifs` helper, without which
`mount -t cifs` fails on a misleading message, measured here: `cannot mount
//127.0.0.1/documents read-only.`), and `smbclient` the exploration tool.

```bash
sudo apt-get install -y samba cifs-utils smbclient
sudo mkdir -p /srv/documents-demo/rapports
echo "inventaire des documents de l atelier" | sudo tee /srv/documents-demo/note.txt
sudo useradd --system --no-create-home --shell /usr/sbin/nologin archiviste
sudo chown -R archiviste:archiviste /srv/documents-demo   # uid 999, gid 987
```

```ini title="/etc/samba/smb.conf"
[global]
   workgroup = ATELIER
   security = user
   server min protocol = SMB3
   restrict anonymous = 2
[documents]
   path = /srv/documents-demo
   read only = no
   valid users = archiviste
```

An SMB account is not a Unix account: the password lives in the Samba database,
set by `smbpasswd`, not in `/etc/shadow`.

```bash
(echo "Demo-Cifs-2026"; echo "Demo-Cifs-2026") | sudo smbpasswd -a -s archiviste
sudo systemctl restart smbd && ss -tlnp | grep :445
```

```text
Added user archiviste.
LISTEN 0      50           0.0.0.0:445       0.0.0.0:*
```

> **Does a mount on yourself go through the network?** Yes: with the share
> mounted, `ss -tn state established '( sport = :445 or dport = :445 )'` shows a
> real TCP connection, `127.0.0.1:445` facing `127.0.0.1:51892`. Everything that
> follows therefore holds for a remote server. One limit only: on a single machine
> the network is always ready at boot, so this setting cannot prove what `_netdev`
> is good for. We will read that in the systemd dependencies.

### See the share, then mount it by hand

`smbclient -L` lists a server's shares. It is the first command to run when a
mount fails: if it does not answer, the problem is on the server or the network
side, no point looking in `fstab`.

```bash
smbclient -L //127.0.0.1 -U archiviste
```

```text
	Sharename       Type      Comment
	---------       ----      -------
	documents       Disk
	IPC$            IPC       IPC Service (Samba 4.19.5-Ubuntu)
```

Now let us mount. Remember the shape of the first argument:
**`//server/share`**, with two slashes and **no** system path (CIFS only knows the
share name, unlike NFS where you write `server:/exported/path`).

```bash
sudo mkdir -p /mnt/documents
sudo mount -t cifs //127.0.0.1/documents /mnt/documents \
  -o username=archiviste,password=Demo-Cifs-2026
findmnt /mnt/documents
```

```text
TARGET         SOURCE                FSTYPE OPTIONS
/mnt/documents //127.0.0.1/documents cifs   rw,relatime,vers=3.1.1,[...],username=archiviste,
uid=0,noforceuid,gid=0,noforcegid,addr=127.0.0.1,file_mode=0755,dir_mode=0755,soft,nounix,[...]
```

This options line holds three answers: the negotiated version (`vers=3.1.1`), the
identity imposed on the files (`uid=0`, `gid=0`) and the displayed permissions
(`file_mode=0755`). We come back to them below.

### The password has no business being in `/etc/fstab`

This is the security point of the subject, and it fits in one command:
`stat -c "%a %U:%G" /etc/fstab` answers **`644 root:root`**.

`/etc/fstab` is readable by **everyone**, and it has to be: `mount`, `findmnt` and
the system tools read it without privilege. A line written with `password=`
therefore exposes the SMB account password to every user of the machine. Checked
from an ordinary account:

```bash
sudo -u stagiaire grep -o 'password=[^,]*' /etc/fstab
```

```text
password=Demo-Cifs-2026 0 0
```

Good practice, and what the exam expects: a **credentials file** whose format is
given by `man mount.cifs` (`username=`, `password=`, and optionally `domain=`),
protected in `0600`.

```bash
printf 'username=archiviste\npassword=Demo-Cifs-2026\ndomain=ATELIER\n' \
  | sudo tee /etc/atelier-smb.cred > /dev/null
sudo chmod 0600 /etc/atelier-smb.cred && ls -l /etc/atelier-smb.cred
sudo -u stagiaire cat /etc/atelier-smb.cred
```

```text
-rw------- 1 root root 59 Jul 22 18:30 /etc/atelier-smb.cred
cat: /etc/atelier-smb.cred: Permission denied
```

`/etc/fstab` then only carries `credentials=/etc/atelier-smb.cred`: the path is
public, the content is not. Two writing traps: **no quotes** around the value
(`password="Demo-Cifs-2026"` makes the mount fail with `mount error(13):
Permission denied`, the quotes being taken as characters of the password), and
**no space** around the `=` sign.

### Who owns the files? `uid`, `gid`, `file_mode`, `dir_mode`

Here is what is most confusing, and what really separates CIFS from NFS. Let us
compare the same file seen from the server and seen through the mount set up
above:

```bash
ls -ln /srv/documents-demo      # server side
ls -ln /mnt/documents           # through the mount
```

```text
-rw-r--r-- 1 999 987   38 Jul 22 18:30 note.txt      <- server
-rwxr-xr-x 1   0   0   38 Jul 22 18:30 note.txt      <- client
```

The owner (999) has become `root`, and the `0644` permissions have become `0755`.
Nothing moved on the server: it is the client-side display that is **made up from
scratch**. Immediate consequence, an unprivileged user cannot write anything:
`touch: cannot touch '/mnt/documents/essai-ansible.txt': Permission denied`.

**Why.** The SMB protocol does not carry POSIX identities. The client opens an
**authenticated session** with an SMB account, and the server applies its own
permissions to that account; it has nothing to say about the UID the client should
display. The CIFS client therefore invents a local identity, whose default is
`uid=0` (`man mount.cifs`: "*sets the uid that will own all files [...] when the
server does not provide ownership information. [...] the default is uid 0*"). NFS
does the opposite: it carries numeric UIDs and GIDs, which produces the opposite
symptoms (files owned by `nobody` through `root_squash`). Hence the `uid=` /
`gid=` / `file_mode=` / `dir_mode=` options specific to CIFS, with no NFS
equivalent.

Let us mount again, choosing the displayed identity:

```bash
sudo umount /mnt/documents
sudo mount -t cifs //127.0.0.1/documents /mnt/documents \
  -o credentials=/etc/atelier-smb.cred,uid=ansible,gid=ansible
ls -l /mnt/documents ; touch /mnt/documents/essai-ansible.txt ; echo "rc=$?"
```

```text
-rwxr-xr-x 1 ansible ansible 38 Jul 22 18:30 note.txt
rc=0
```

The write goes through. But look at the same file **on the server side**:

```text
-rwxr--r-- 1 999 987 0 Jul 22 18:30 /srv/documents-demo/essai-ansible.txt
```

It belongs to `archiviste`, the account of the SMB session, not to `ansible`.
Remember the rule: **`uid=` only changes the client's view; on the server side,
everything is done under the authenticated account.** This is not access control,
it is a costume, and `findmnt` says so, the option going from `uid=0,noforceuid`
to `uid=1001,forceuid`. `file_mode=` and `dir_mode=` dress up the permissions the
same way:

```bash
sudo mount -t cifs //127.0.0.1/documents /mnt/documents \
  -o credentials=/etc/atelier-smb.cred,uid=ansible,gid=ansible,file_mode=0640,dir_mode=0750
ls -l /mnt/documents ; chmod 0600 /mnt/documents/note.txt ; echo "rc=$?"
ls -l /mnt/documents/note.txt
```

```text
-rw-r----- 1 ansible ansible 38 Jul 22 18:30 note.txt
drwxr-x--- 2 ansible ansible  0 Jul 22 18:30 rapports
rc=0
-rw-r----- 1 ansible ansible 38 Jul 22 18:30 note.txt      <- unchanged
```

The `chmod` **returns 0 and changes nothing**: without the Unix extensions (the
mount is in `nounix`), the displayed mode stays the one from `file_mode`, on the
client as well as on the server. A silent failure you have to know about before
losing an hour on it.

### Making the mount persistent: `_netdev` and `nofail`

**Back up `/etc/fstab` before editing it** (`sudo cp -a /etc/fstab
/root/fstab.avant-cifs`): a mistake here is paid for at the next boot.

```text title="/etc/fstab"
//127.0.0.1/documents /mnt/documents cifs _netdev,nofail,credentials=/etc/atelier-smb.cred,uid=ansible,gid=ansible,file_mode=0640,dir_mode=0750 0 0
```

Six fields, as for a local disk: source `//server/share`, mount point, type
`cifs`, options, then `0 0` (a network share is neither backed up nor checked
locally). Then, in this order:

```bash
sudo systemctl daemon-reload    # systemd re-reads fstab
sudo findmnt --verify           # syntax check
sudo mount -a                   # apply without rebooting
findmnt -no SOURCE,TARGET,FSTYPE /mnt/documents
```

```text
Success, no errors or warnings detected
//127.0.0.1/documents /mnt/documents cifs
```

`mount -a` is replayable: run again while the share is already mounted, it does
nothing and returns 0.

> **Never test an `fstab` line with a reboot.** `findmnt --verify` reads the
> syntax, `mount -a` proves that the line really mounts, and
> `systemctl show <unit>.mount` proves the rest. A reboot on a doubtful line costs
> a minute and a half of waiting per unreachable entry, and hands back a degraded
> machine if the entry has no `nofail`.

**What `nofail` changes**, read through `systemctl show remote-fs.target -p Requires
-p Wants` with and then without the option:

```text
with nofail:     Requires=                       Wants=mnt-documents.mount
without nofail:  Requires=mnt-documents.mount    Wants=
```

The mount moves from `Requires` to `Wants`: its failure no longer drags the target
down with it, so no more degraded boot. The wait itself remains, but stays bounded
(`systemctl show mnt-documents.mount -p TimeoutUSec` answers
`TimeoutUSec=1min 30s`).

**What `_netdev` changes**, on this machine: nothing measurable. The same
`systemctl show -p Wants -p After` with and without the option return exactly
`Wants=network-online.target` and the same ordering after `network-online.target`
and `remote-fs-pre.target`. As for `nfs`, systemd already knows that `cifs` is a
network filesystem and classifies it on its own. Write `_netdev` anyway: the LFCS
exam expects it, it documents the intent, and it becomes indispensable as soon as
a **local** filesystem sits on a network transport (an `ext4` on an iSCSI volume,
which systemd cannot guess).

### The dialect version: do not force `vers=3.0`

The companion guide advises `-o vers=3.0` to "force SMB3" rather than letting the
negotiation happen. On this machine, **the advice is counter-productive**: with
`credentials=/etc/atelier-smb.cred,vers=3.0`, the mount fails, and `dmesg` says
why.

```text
mount error(95): Operation not supported
CIFS: VFS: \\127.0.0.1 Dialect not supported by server.
```

Two manual pages from the machine explain this refusal. `man mount.cifs`: "*If no
dialect is specified on mount `vers=default` is used*", which negotiates the
**highest common version**, here **3.1.1**, so better than 3.0. And `man
smb.conf`: the `SMB3` value of `server min protocol` is an alias for `SMB3_11`,
that is SMB 3.1.1; a server hardened that way therefore refuses SMB 3.0.0. With
`server min protocol = SMB3_00`, the same `vers=3.0` goes through.

Conclusion: **let the negotiation happen**, and check the dialect you got, either
in the options (`findmnt -no OPTIONS /mnt/documents` contains `vers=3.1.1`), or in
the file that `man mount.cifs` points to for that purpose:

```bash
sudo grep Dialect /proc/fs/cifs/DebugData      # Dialect 0x311 = SMB 3.1.1
```

Only force a version to go **down** to an old server, never to go up: `vers=1.0`
(SMB1, the real historical "CIFS", the one of EternalBlue) is also flatly refused
by this server, with the same error 95.

### Troubleshooting and back to the initial state

Faced with a `mount error(N)`, read `sudo dmesg | tail -3`: the code is vague, the
kernel message is precise.

| Symptom | Likely cause | Fix |
|---|---|---|
| `cannot mount ... read-only.` | `/sbin/mount.cifs` helper missing, so the `cifs-utils` package is not installed | install it |
| `mount error(13): Permission denied`, dmesg `STATUS_LOGON_FAILURE` | wrong credentials, or quotes in the credentials file | fix the file, without quotes |
| `mount error(2)`, dmesg `BAD_NETWORK_NAME` | share name does not exist | `smbclient -L //<server> -U <user>` |
| `error 2 opening credential file ...` | wrong `credentials=` path | check the path, return code 2 |
| `mount error(95)`, dmesg `Dialect not supported` | `vers=` incompatible with `server min protocol` | remove `vers=`, let the negotiation happen |
| `mount error(113): could not connect` | server unreachable (6 s measured on this network) | route, address, firewall, port 445 |
| All the files belong to `root` | `uid=0` default of the CIFS client | add `uid=`/`gid=` |
| `chmod` returns 0 and changes nothing | `nounix` mount: permissions come from `file_mode` | adjust `file_mode=`/`dir_mode=` |
| The share disappears after a reboot | no line in `/etc/fstab` | add it, validate with `mount -a` |
| A user reads the SMB password | `password=` in `/etc/fstab` (mode 644) | credentials file in `0600` |

To undo everything, in this order: unmount, restore `/etc/fstab` from the copy
taken **before** the edit, erase the credentials, stop the server. Do not forget
the SMB account: `smbpasswd -x` removes it from the Samba database, which
`userdel` does not do.

```bash
sudo umount /mnt/documents
sudo cp -a /root/fstab.avant-cifs /etc/fstab && sudo systemctl daemon-reload
sudo shred -u /etc/atelier-smb.cred          # a password is not simply rm'd
sudo systemctl disable --now smbd nmbd
sudo rm -rf /srv/documents-demo /mnt/documents
sudo smbpasswd -x archiviste && sudo userdel archiviste
findmnt -t cifs ; sudo pdbedit -L            # no output expected
```
