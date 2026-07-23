# Lab — persistent NFS mount

## Reminder

[**NFS on the companion guide**](https://blog.stephane-robert.info/docs/services/stockage/nfs/)

A server exports a directory through `/etc/exports`; a client mounts it with
`mount -t nfs <server>:/path <mount-point>`. A mount created by hand disappears
at reboot: persistence goes through a line in `/etc/fstab`. The `nfs-utils`
package provides the client on RHEL-family distributions;
`showmount -e <server>` lists the exports of a server.

## The course

The examples below work on a `/srv/partage-demo` share mounted on `/mnt/depot`:
the challenge will ask you for another export, another mount point and another
file to read. The goal is to learn the method, not to copy a line.

Every output reproduced here comes from an AlmaLinux 10.2 machine (kernel
6.12), with `nfs-utils` 2.8.3, SELinux in `Enforcing` and `firewalld` active.

### The setup: server and client on the same machine

You do not need two machines to learn. You set up a small NFS server and
connect to it through `127.0.0.1`. On the server side:

```bash
sudo mkdir -p /srv/partage-demo /srv/archives-demo
echo "inventaire du depot" | sudo tee /srv/partage-demo/bienvenue.txt
echo "note archivee"       | sudo tee /srv/archives-demo/lisez-moi.txt
sudo chown -R nobody:nobody /srv/partage-demo /srv/archives-demo
```

```text title="/etc/exports"
/srv/partage-demo  127.0.0.0/8(rw,sync,no_subtree_check)
/srv/archives-demo 127.0.0.0/8(ro,sync,no_subtree_check)
```

```bash
sudo systemctl enable --now nfs-server
systemctl status nfs-server
```

```text
     Active: active (exited) since Wed 2026-07-22 14:36:32 UTC; 7s ago
```

`active (exited)` is not a failure: the NFS server runs in kernel threads, the
systemd unit only starts them, then exits.

> **Does a mount onto yourself really go through the network?** Yes. Once the
> share is mounted, `ss` shows an established TCP connection on port 2049, just
> like for a remote server:
>
> ```bash
> ss -tn state established '( sport = :2049 or dport = :2049 )'
> ```
>
> ```text
> Recv-Q Send-Q Local Address:Port Peer Address:Port
> 0      0          127.0.0.1:967     127.0.0.1:2049
> 0      0          127.0.0.1:2049    127.0.0.1:967
> ```
>
> The kernel does not short-circuit the network stack: the options, the
> versions and the outage behaviours observed below are those of a real NFS
> mount. Only the latency is unrealistic.

### Seeing what the server exposes

Two points of view, not to be confused. On the **server** side, `exportfs -v`
shows the effective configuration, default options included:

```bash
sudo exportfs -ra     # re-read /etc/exports and apply
sudo exportfs -v
```

```text
/srv/partage-demo
		127.0.0.0/8(sync,wdelay,hide,no_subtree_check,sec=sys,rw,secure,root_squash,no_all_squash)
/srv/archives-demo
		127.0.0.0/8(sync,wdelay,hide,no_subtree_check,sec=sys,ro,secure,root_squash,no_all_squash)
```

Three options were never written and yet they are there: `sec=sys`,
`root_squash` and `secure`. They are the defaults, and they matter (see below).

On the **client** side, `showmount -e` queries the server over the network:

```bash
showmount -e 127.0.0.1
```

```text
Export list for 127.0.0.1:
/srv/archives-demo 127.0.0.0/8
/srv/partage-demo  127.0.0.0/8
```

This is the first command to run when a mount fails: if `showmount` does not
answer, the problem is on the server or on the network, no point looking in
`fstab`.

### Mounting by hand

```bash
sudo mkdir -p /mnt/depot
sudo mount -t nfs 127.0.0.1:/srv/partage-demo /mnt/depot
findmnt /mnt/depot
```

```text
TARGET     SOURCE                      FSTYPE OPTIONS
/mnt/depot 127.0.0.1:/srv/partage-demo nfs4   rw,relatime,vers=4.2,rsize=131072,wsize=131072,namlen=255,hard,fatal_neterrors=none,proto=tcp,timeo=600,retrans=2,sec=sys,clientaddr=127.0.0.1,local_lock=none,addr=127.0.0.1
```

Three things to read in that line:

- you asked for `-t nfs`, the kernel answers **`nfs4`** with **`vers=4.2`**: the
  highest version common to the client and the server was negotiated
  automatically;
- `proto=tcp` and port 2049 are enough with NFSv4, there are no auxiliary
  daemons to open any more;
- `hard`, `timeo=600`, `retrans=2` are the default behaviours in case of an
  outage. A whole section below is devoted to them.

`nfsstat -m` gives the same information, mount by mount, and it is the command
to remember to check the **version actually negotiated**:

```bash
nfsstat -m
```

```text
/mnt/depot from 127.0.0.1:/srv/partage-demo
 Flags:	rw,relatime,vers=4.2,rsize=131072,wsize=131072,namlen=255,hard,...
```

And the content served by the server is there:

```bash
cat /mnt/depot/bienvenue.txt
```

```text
inventaire du depot
```

### What the client asks for, what the server enforces

Mount the second share, exported as `ro`, and look at the options on the client
side:

```bash
sudo mkdir -p /mnt/archives
sudo mount -t nfs 127.0.0.1:/srv/archives-demo /mnt/archives
findmnt -no OPTIONS /mnt/archives
```

```text
rw,relatime,vers=4.2,rsize=131072,wsize=131072,namlen=255,hard,...
```

The client displays **`rw`**. And yet:

```bash
echo test | sudo tee /mnt/archives/interdit.txt
```

```text
tee: /mnt/archives/interdit.txt: Read-only file system
```

Remember the lesson: the options shown by `findmnt` or `mount` are the ones the
**client** asked for, not the ones the **server** applies. A share exported as
`ro` refuses writes even if the mount claims to be `rw`. To know the truth, you
have to look at `exportfs -v` on the server.

Second surprise, on the read-write share this time:

```bash
echo "ligne ajoutee depuis le client" | sudo tee /mnt/depot/essai.txt
ls -l /mnt/depot
```

```text
total 8
-rw-r--r--. 1 nobody nobody 20 Jul 22 14:36 bienvenue.txt
-rw-r--r--. 1 nobody nobody 31 Jul 22 14:36 essai.txt
```

The file was created by `root` through `sudo`, and it belongs to `nobody`. That
is `root_squash`, active by default: the server replaces the client's UID 0 with
the anonymous user. NFS reasons in **numeric UIDs and GIDs**; what the client
believes its identity to be does not bind the server.

### `hard` or `soft`: what happens when the server disappears

This is the least understood point of NFS, and the easiest to check: you only
have to stop the service while a mount is active.

#### The default, `hard`: you wait, indefinitely

```bash
sudo mount -t nfs -o hard,timeo=30,retrans=2,actimeo=0 \
  127.0.0.1:/srv/partage-demo /mnt/depot
sudo systemctl stop nfs-server
```

A reader is started in the background, and 20 seconds later it still has
produced nothing:

```text
  PID STAT CMD
18530 D    cat /mnt/depot/bienvenue.txt
```

State **`D`** is *uninterruptible sleep*: the process sleeps in the kernel,
waiting for an answer that never comes. It displayed nothing, it failed at
nothing, it waits. Restart the server:

```bash
sudo systemctl start nfs-server
```

```text
14:38:17      <- read starts
inventaire du depot
rc=0
14:38:38      <- end, 21 seconds later
```

The read finished **normally**, with the right content and a return code of 0.
This is exactly what you expect from a `hard` mount: no data lost, no error
reported to the application, at the cost of an unbounded wait.

> **A blocked `hard` mount freezes everything that touches it.** During the
> wait, `df`, `ls`, a `umount` and even a shell completion that walks through
> the mount point freeze in turn. On a production server, a single unreachable
> NFS line can therefore paralyse services that do not use it directly.

How do you get out of it when you cannot restart the server? Two options, tried
with the server stopped and a reader still active on the mount. `umount -f`
fails immediately, because a process is still holding the mount point:

```bash
sudo umount -f /mnt/depot
```

```text
umount.nfs4: /mnt/depot: device is busy
```

```text
real	0m0.019s      (return code 16)
```

`umount -l` (*lazy*), on the other hand, detaches the mount point from the tree
without waiting for the processes, and returns after 18 seconds:

```bash
sudo umount -l /mnt/depot
```

```text
real	0m18.077s     (return code 0)
```

Remember the order: restart the server if you can, otherwise `umount -f`, then
`umount -l` as a last resort. `-l` hides the problem without solving it: the
blocked processes stay blocked.

#### Difference between the guide and the machine: `kill -9` works

The companion guide states that a process blocked in `D` on a `hard` mount
cannot be killed, that "`kill -9` has no effect". On this machine, that is not
what happens:

```bash
sudo kill -9 18756
```

```text
process gone after 1s
```

Tested twice, same result: the process dies in about a second, without having
displayed anything. The RPC waits of the modern NFS client are *killable*: a
fatal signal interrupts them. This is not true of every operation nor of every
kernel, and the test was run with the server stopped on the loopback interface,
so with a clean connection refusal, not a network that silently swallows
packets. The cautious conclusion to remember: `kill -9` **may** work, do not
count on it, and above all do not use it as an argument for choosing `hard`
lightly.

#### `soft`: an error after a delay

```bash
sudo mount -t nfs -o soft,timeo=30,retrans=2,actimeo=0 \
  127.0.0.1:/srv/partage-demo /mnt/depot
sudo systemctl stop nfs-server
time cat /mnt/depot/bienvenue.txt
```

```text
cat: /mnt/depot/bienvenue.txt: Input/output error

real	0m18.085s
```

This time, the call **returns**: an input/output error after 18 seconds. Note
the gap with the naive computation: `timeo=30` means 3 seconds (the unit is the
**tenth** of a second) and `retrans=2` announces two retransmissions, which
would make 9 seconds. The NFSv4 client applies its own retry logic on top of
those values. Measure, do not deduce.

The unmount also goes through in the end, with the same delay:

```bash
time sudo umount /mnt/depot
```

```text
real	0m18.130s
```

#### Which one to choose

| Option | Behaviour if the server goes down | Use |
|---|---|---|
| `hard` (default) | unbounded wait, intact resume when it comes back | anything that writes, production |
| `soft` | input/output error after expiry | non-critical reads, scripts that must return |
| `timeo=n` | delay before retransmission, in **tenths of a second** | tune rather than switch to `soft` |
| `retrans=n` | number of retransmissions before giving up or warning | same |

The guide is clear on the subject and the `nfs(5)` manual confirms it: `soft`
exposes you to **silent corruption**, a write can fail while the application
believes it succeeded. Keep `hard`, and if the wait worries you, play with
`timeo` and `retrans`. During your outage tests, on the other hand, `soft`
keeps you from being stuck without being able to clean up.

### Making the mount persistent

A `mount` created by hand does not survive a reboot. The `/etc/fstab` line
follows the same grammar as for a local disk, except that the first field is a
remote resource:

```text title="/etc/fstab"
127.0.0.1:/srv/partage-demo /mnt/depot nfs _netdev,nofail,defaults 0 0
```

The six fields: the source `<server>:/<exported path>`, the mount point, the
type, the options, then `0 0` for dump and fsck (a network share is neither
backed up nor checked locally).

**Back it up before editing.** A mistake in `fstab` is paid for at the next
boot:

```bash
sudo cp -a /etc/fstab /root/fstab.bak
```

Then, in order:

```bash
sudo systemctl daemon-reload   # systemd re-reads fstab
sudo findmnt --verify          # syntax check
sudo mount -a                  # apply without rebooting
findmnt -no SOURCE,TARGET,FSTYPE /mnt/depot
```

```text
127.0.0.1:/srv/partage-demo /mnt/depot nfs4
```

`mount -a` is replayable: run a second time while the share is already mounted,
it does nothing and returns 0.

If you forget the `daemon-reload`, `findmnt --verify` reminds you:

```text
0 parse errors   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload
, 0 errors, 1 warning
```

> **`findmnt --verify` warns, it does not decide.** With a misspelled type
> (`nsf` instead of `nfs`), it does report
> `[W] nsf seems unsupported by the current kernel`, but **still exits with code
> 0**. It is `mount -a` that fails, with
> `mount: /mnt/depot: unknown filesystem type 'nsf'.` and code 32. Use both:
> `findmnt --verify` to read the warnings, `mount -a` for the proof.

### `_netdev` and `nofail`: what they really do

These two options exist for a simple reason: at boot, an NFS line is a mount
point that depends on a third-party machine.

**What an unreachable server costs**, measured by hand:

```bash
time sudo mount -t nfs 192.0.2.1:/srv/partage-demo /mnt/injoignable
```

```text
mount.nfs: Connection timed out for 192.0.2.1:/srv/partage-demo on /mnt/injoignable

real	3m2.042s
```

Three minutes before giving up. The `nfs(5)` manual announces a default of
`retry=2` (two minutes) for a foreground mount; the actual wait measured is
longer, because the last attempt exhausts its own timeout after the end of the
window. With `retry=0`, the same command returns in 9 seconds.

**`_netdev` classifies the mount as a network mount.** The `systemd.mount(5)`
manual, on the machine, is explicit:

```text
_netdev
    Normally the file system type is used to determine if a mount is a
    "network mount", i.e. if it should only be started after the network is
    available. Using this option overrides this detection and specifies that
    the mount requires network.

    Network mount units are ordered between remote-fs-pre.target and
    remote-fs.target, instead of local-fs-pre.target and local-fs.target.
    They also pull in network-online.target and are ordered after it and
    network.target.
```

You can check it without rebooting, by reading the unit systemd builds from
`fstab`:

```bash
sudo systemctl daemon-reload
systemctl show mnt-depot.mount -p After -p Wants
```

```text
Wants=network-online.target
After=network.target -.mount system.slice remote-fs-pre.target nfs-server.service network-online.target systemd-journald.socket
```

> **Difference with the guide.** The guide presents `_netdev` as indispensable,
> failing which "the boot may stay blocked". On this machine, the same line
> **without** `_netdev` produces exactly the same dependencies:
> `Wants=network-online.target`, ordering after `network-online.target` and
> before `remote-fs.target`. This is consistent with the manual quoted above:
> for a type **known to be a network type**, the automatic detection is enough
> and `_netdev` only confirms it. The option remains useful, and expected in an
> exam: it is mandatory for a **local** file system laid on a network transport
> (an `ext4` on an iSCSI volume, which systemd cannot guess), and it documents
> the intent. Write it, now knowing what it changes and what it does not.

**`nofail` decides whether the failure is fatal.** It is this option, not
`_netdev`, that changes something at boot, and the difference is readable in the
dependencies of `remote-fs.target`. Without `nofail`:

```text
Requires=mnt-injoignable.mount
```

With `nofail`:

```text
Requires=
Wants=... mnt-injoignable.mount ...
```

The mount moves from `Requires` to `Wants`: its failure no longer brings down
the target. Beware, `nofail` does not remove the **wait**, only its fatal
nature. Note by the way that systemd bounds that wait, which `mount` alone does
not do:

```bash
systemctl show mnt-injoignable.mount -p TimeoutUSec
```

```text
TimeoutUSec=1min 30s
```

> **Never test an NFS line with a reboot.** `mount -a` and `findmnt --verify`
> prove the same thing without any risk, and `systemctl show <unit>.mount`
> proves the rest. A reboot on a doubtful `fstab` means a minute and a half of
> waiting per unreachable entry, and a machine that comes back degraded if the
> entry is declared without `nofail`. None of that teaches you anything the
> commands above do not say faster.

### The alternative: mount on demand

When the share is not needed at boot, you can have it mounted on first access
rather than at boot:

```text title="/etc/fstab"
127.0.0.1:/srv/partage-demo /mnt/depot nfs _netdev,noauto,x-systemd.automount 0 0
```

```bash
sudo systemctl daemon-reload
sudo systemctl start mnt-depot.automount
findmnt -no TARGET,FSTYPE /mnt/depot
```

```text
/mnt/depot autofs
```

Before any access, the mount point is an `autofs`: nothing is connected, the
boot waits for nobody. On first access:

```bash
cat /mnt/depot/bienvenue.txt
findmnt -no SOURCE,TARGET,FSTYPE /mnt/depot
```

```text
inventaire du depot
systemd-1                   /mnt/depot autofs
127.0.0.1:/srv/partage-demo /mnt/depot nfs4
```

The NFS mount was stacked on top of the `autofs`. Beware however: `noauto`
means nothing is mounted as long as nobody looks. A check that requires an
**active** mount after `mount -a` will not be satisfied by this method.

### When the export path is not the one you think

The server side holds a trap that shows up on the client side. Add an NFSv4
export root with `fsid=0`:

```text title="/etc/exports"
/srv                127.0.0.0/8(rw,sync,fsid=0,crossmnt,no_subtree_check)
/srv/partage-demo   127.0.0.0/8(rw,sync,no_subtree_check)
```

Three mounts, three different results, all measured:

```bash
sudo mount -t nfs  127.0.0.1:/srv/partage-demo /mnt/depot && nfsstat -m
```

```text
/mnt/depot from 127.0.0.1:/srv/partage-demo
 Flags:	rw,relatime,vers=3,...,mountvers=3,mountport=20048,mountproto=udp,...
```

The mount **succeeded**, but in **NFSv3**. Nothing reported it: you had to read
`vers=3` in `nfsstat -m`.

```bash
sudo mount -t nfs  127.0.0.1:/partage-demo /mnt/depot && nfsstat -m
```

```text
/mnt/depot from 127.0.0.1:/partage-demo
 Flags:	rw,relatime,vers=4.2,...
```

With the path **relative to the `fsid=0` root**, you do get NFSv4.2.

```bash
sudo mount -t nfs4 127.0.0.1:/srv/partage-demo /mnt/depot
```

```text
mount.nfs4: mounting 127.0.0.1:/srv/partage-demo failed, reason given by server: No such file or directory
```

By forcing `nfs4` on the full path, the failure becomes explicit: for NFSv4,
that path does not exist, since everything is relative to the root declared by
`fsid=0`.

To remember: `fsid=0` changes the way the **client** has to name the export.
Without `fsid=0` in `/etc/exports` (the configuration at the beginning of this
course), the full path works and gives NFSv4.2 directly. In every case,
`showmount -e` lists the **system** paths of the server, not necessarily the
ones an NFSv4 client has to ask for: check the version obtained with
`nfsstat -m` after each mount.

### Firewall and SELinux

On the demonstration machine, mounting through the loopback interface asked
nothing of the firewall, but the active zone does not contain NFS:

```bash
sudo firewall-cmd --list-services
```

```text
cockpit dhcpv6-client ssh
```

```bash
sudo firewall-cmd --info-service=nfs
```

```text
nfs
  ports: 2049/tcp
```

For a **remote** client, you therefore have to open the service on the server
side:

```bash
sudo firewall-cmd --add-service=nfs --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-services
```

```text
cockpit dhcpv6-client nfs ssh
```

On the client side, nothing to open: the connection observed above goes from the
client (source port 967) to port 2049 of the server, so it is the client that
initiates it.

SELinux stayed in `Enforcing` during all the tests above without blocking
anything. It can on the other hand get in the way when a confined application
reads an NFS share; the symptom is a `Permission denied` that Unix permissions
do not explain, and the reflex remains `sudo ausearch -m AVC -ts recent`.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `showmount -e <server>` does not answer | NFS service stopped, or port 2049 filtered on the server |
| `mount.nfs: Connection timed out` after three minutes | server unreachable; check the address, the route, the firewall |
| `mount.nfs: access denied by server` | the client address is not covered by the `/etc/exports` line |
| `mount.nfs4: ... No such file or directory` | wrong export path, or an `fsid=0` root that makes paths relative |
| `mount: unknown filesystem type 'nsf'` | typo on the type in `fstab`; `mount -a` exits with 32 |
| The mount works but in `vers=3` | negotiation fell back; read it with `nfsstat -m`, force it with `-t nfs4` or `vers=4.2` |
| Write refused although the client shows `rw` | the export is `ro` on the server; look at `exportfs -v` |
| Created files belong to `nobody` | `root_squash` (default): the client's UID 0 is mapped to the anonymous user |
| `df`, `ls` and `umount` frozen | `hard` mount whose server no longer answers; restart the server, otherwise `umount -f`, then `umount -l` |
| `umount -f` answers `device is busy` (code 16) | a process still holds the mount point; move on to `umount -l` |
| `Input/output error` on a network share | `soft` mount that expired; the server does not answer |
| The share disappears at reboot | no line in `/etc/fstab` |
| `findmnt --verify` reports nothing but `mount -a` fails | `--verify` only emits warnings and exits with 0; trust the return code of `mount -a` |
| The boot waits a minute and a half | unreachable NFS entry; systemd bounds the mount to `TimeoutUSec` (1 min 30 s by default) |
| `remote-fs.target` failed after boot | NFS entry failed **without** `nofail`: the target declares it in `Requires` |
| `fstab` modified but systemd ignores the change | `sudo systemctl daemon-reload` forgotten |
| `Stale file handle` | export modified without `exportfs -ra`; re-apply on the server then remount |

To undo everything and start over:

```bash
sudo umount /mnt/depot /mnt/archives
sudo cp -a /root/fstab.bak /etc/fstab      # restore the backup
sudo systemctl daemon-reload
sudo systemctl disable --now nfs-server
sudo rm -rf /srv/partage-demo /srv/archives-demo /mnt/depot /mnt/archives
sudo truncate -s 0 /etc/exports            # or restore your own backup
sudo exportfs -ra
```

Check that nothing is left behind:

```bash
findmnt -t nfs,nfs4     # no output expected
sudo exportfs -v        # no output expected
```
