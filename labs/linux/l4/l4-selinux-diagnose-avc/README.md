# Lab — diagnose an SELinux AVC denial

## Reminder

[**SELinux on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

When a confined service is denied an access, SELinux logs an **AVC** in the audit
log. `ausearch -m avc` extracts it, `audit2why` explains it, `sealert` translates
it into plain language when it is installed. The AVC names the domain that acts
(`scontext`), the object aimed at (`tcontext`), the class of that object
(`tclass`) and the denied operation: those four fields are enough to point to the
fix. `ls -Z` shows the label of a file, `getenforce` the current mode. Never
`setenforce 0`.

## The course

The examples below deliberately deal with something other than the challenge:
you diagnose a `chronyd` that refuses to start, then an SSH connection that
**succeeds** despite a logged denial. You learn to read an AVC, you do not copy a
line.

This course covers neither the label fix nor the booleans: those are the
subjects of the `l4-selinux-context-fix` and `l4-selinux-boolean-port` labs.
Here, you stop at the moment the AVC said what to fix, because that is where
everything is decided. Every output reproduced was recorded on an AlmaLinux 10.2
in enforcing mode.

### Where denials are written, and where they are not

First question, always the same: is SELinux enforcing its policy?

```bash
getenforce
```

```text
Enforcing
```

In `Permissive`, everything that follows is still written to the log but nothing
is blocked: your failure then comes from somewhere else. To settle it, switch
with `setenforce 0` / `setenforce 1`, and **never** by touching
`/etc/selinux/config`, which only takes effect at the next boot.

Denials go from the kernel to `auditd`, which writes them into
**`/var/log/audit/audit.log`**. The guide also offers a shortcut,
`dmesg | grep -i denied`. Let us check it:

```bash
sudo dmesg | grep -ic denied
sudo grep -c "avc:  denied" /var/log/audit/audit.log
```

```text
0
71
```

**Zero in `dmesg`, seventy-one in the audit log.** When `auditd` is running, it
captures the messages, which do not stay in the kernel buffer: never conclude "no
denial" from the silence of `dmesg`.

### The symptom: an ordinary failure, with nothing abnormal in the permissions

Let us set up the failure. An administrator edits the `chronyd` configuration
from his home directory, then puts it back with `mv`:

```bash
cp /etc/chrony.conf ~/chrony.conf
printf '# ajustement atelier\n' >> ~/chrony.conf
sudo mv ~/chrony.conf /etc/chrony.conf
sudo systemctl restart chronyd
```

```text
Job for chronyd.service failed because the control process exited with error code.
```

The service then says what it knows how to say:

```bash
sudo journalctl -u chronyd --since -3min | tail -3
```

```text
chronyd[26618]: Fatal error : Could not open /etc/chrony.conf : Permission denied
systemd[1]: chronyd.service: Main process exited, code=exited, status=1/FAILURE
[...]
```

"Permission denied", and yet, on the Unix side, there is nothing to object to:
the file is readable by everyone and `chronyd` starts as root.

```bash
ls -lZ /etc/chrony.conf
```

```text
-rw-r--r--. 1 root root unconfined_u:object_r:user_home_t:s0 1406 Jul 22 16:09 /etc/chrony.conf
```

The `.` after the permissions signals a SELinux context, and `ls -Z` gives it:
`user_home_t`. The `mv` **kept the label of the source**, unlike a copy, which
would have taken that of the destination directory: this is the most frequent
origin of the denials met in production. But at this stage we are only
suspecting; the proof is in the AVC.

### Pulling the AVC out of the log, and the terminal trap

The reference command:

```bash
sudo ausearch -m avc -ts recent
```

```text
<no matches>
```

A wrong answer: the log contains 71 denials. `ausearch` behaves this way when it
has **no terminal**, exactly the case of an `ssh machine 'command'`, of a script
or of an automation tool. Two workarounds:

```bash
sudo ausearch -m avc -ts recent --input-logs   # reads the log files
ssh -tt machine 'sudo ausearch -m avc -ts recent'   # forces a terminal
```

Remember it: a `<no matches>` obtained from a script proves nothing at all.
Three sorting options are then in permanent use: `-ts` bounds the window
(`recent` means the last ten minutes, otherwise `today` or a time such as
`16:00`), `-c <name>` filters on `comm=`, that is the short name of the program,
and `-i` interprets dates and numeric values. With the filter on the service, the
denial shows up:

```bash
sudo ausearch -m avc -ts recent -c chronyd --input-logs
```

```text
type=AVC msg=audit(1784736582.173:16519): avc:  denied  { read } for  pid=26708
  comm="chronyd" name="chrony.conf" dev="vda4" ino=17207620
  scontext=system_u:system_r:chronyd_t:s0
  tcontext=unconfined_u:object_r:user_home_t:s0 tclass=file permissive=0
```

### Dissecting the AVC field by field

This is the skill of the lab. Take the line again:

| Field | Value here | What it says |
| --- | --- | --- |
| `denied { read }` | `read` | the denied **operation** |
| `scontext` | `system_u:system_r:chronyd_t:s0` | **who acts**: the domain of the process |
| `tcontext` | `unconfined_u:object_r:user_home_t:s0` | **on what**: the label of the target |
| `tclass` | `file` | **which kind of object**: file, directory, socket… |
| `permissive` | `0` | the denial was **enforced** |
| `comm=` | `chronyd` | the short name of the requesting program |
| `name=` | `chrony.conf` | the name of the target, without its path |

In `scontext` and `tcontext`, **only the third field matters**: `chronyd_t` on
one side, `user_home_t` on the other. The full sentence then reads like plain
English: *a `chronyd_t` process wanted to `read` a `file` labelled
`user_home_t`, and the policy does not allow for it.*

Two fields call for a nuance. `name=` only gives the leaf name; the **full path**
only appears, in a `path=` field, for certain system calls. On the same machine,
another denial shows it:

```text
avc:  denied  { open } for  pid=27058 comm="sshd-session"
  path="/home/sonde/.ssh/authorized_keys" [...] tclass=file permissive=1
```

When `path=` is missing, the `ino=` field is enough to find the file back:
`sudo find / -xdev -inum <inode>` answered here in less than a tenth of a second.
As for `comm=`, it is sometimes displayed in hexadecimal: this is not a bug but
the encoding `ausearch` applies to names containing spaces or special
characters, and `ausearch -i` makes them readable.

### The operation and the `tclass` point to the fix

This is the point to take away: **the operation + `tclass` pair tells you which
family of fix to look for**, even before you know which type to set.

| Operation and class | What is at stake | Where to fix |
| --- | --- | --- |
| `{ read }`, `{ write }`, `{ open }`, `{ getattr }` on `file` or `dir` | the **label** of a file or a directory | `restorecon`, or `semanage fcontext` if the policy ignores that path |
| `{ name_bind }` on `tcp_socket` or `udp_socket` | a service wants a **port** its type does not cover | `semanage port` |
| `{ name_connect }`, `{ connectto }` | an **outgoing connection** or one towards a socket | most often a **boolean** |

Our AVC falls into the first row: `{ read }` on `tclass=file`, so a label,
neither a port nor a boolean. These fixes are detailed in the
`l4-selinux-context-fix` and `l4-selinux-boolean-port` labs; what matters here is
to have known how to **choose** the right row from two words of the AVC. The
diagnosis is verified by fixing it, and the service starts again:

```bash
sudo restorecon -v /etc/chrony.conf
sudo systemctl restart chronyd && systemctl is-active chronyd
```

```text
Relabeled /etc/chrony.conf from unconfined_u:object_r:user_home_t:s0 to unconfined_u:object_r:etc_t:s0
active
```

### The false positive: an AVC is not always a block

Here is the most expensive reasoning error, and it can be seen on this same
machine. Let us deliberately mislabel the key file of an account, then connect
with its key:

```bash
sudo chcon -t var_log_t /home/sonde/.ssh/authorized_keys
ssh -i /tmp/cle-sonde sonde@localhost 'echo CONNEXION-OK'
```

```text
CONNEXION-OK
```

**The connection succeeds**, whereas the denial was indeed logged:

```text
avc:  denied  { read } for  pid=27058 comm="sshd-session" name="authorized_keys"
  scontext=system_u:system_r:sshd_session_t:s0-s0:c0.c1023
  tcontext=unconfined_u:object_r:var_log_t:s0 tclass=file permissive=1
```

The field that changes everything: **`permissive=1`**. The `sshd_session_t`
domain is one of the domains declared permissive by the policy itself:

```bash
sudo semanage permissive -l
```

```text
Builtin Permissive Types

dhcpc_hook_t
systemd_hibernate_resume_t
sshd_session_t
sshd_auth_t
[...]
```

For those domains, SELinux **logs without blocking**. The corresponding system
call confirms it, with `success=yes exit=0` where the `chronyd` one carried
`success=no exit=-13`. An `ausearch` option exploits that difference:

```bash
sudo ausearch -m avc -ts today --input-logs | grep -c "type=AVC"
sudo ausearch -m avc -ts today --input-logs | grep "type=AVC" | grep -c "permissive=1"
sudo ausearch -m avc -ts today --success no --input-logs | grep -c "type=AVC"
```

```text
71
24
47
```

71 logged denials, 24 of which in `permissive=1`; `--success no` keeps 47 of
them, which is exactly the 71 minus the 24. **Make `ausearch -m avc --success
no` a reflex**: without it, you will spend an hour "fixing" an AVC that never
prevented anything, while the failure is elsewhere.

### `audit2why`, `audit2allow`, and why `-M` comes last

`audit2why` takes an AVC on its standard input and translates it:

```bash
sudo ausearch -m avc --success no -ts recent -c chronyd --input-logs | audit2why
```

```text
	Was caused by:
		Missing type enforcement (TE) allow rule.

		You can use audit2allow to generate a loadable module to allow this access.
```

There is no rule to enable here: the policy has nothing that allows this access.
When a **boolean** is at stake, `audit2why` names it, and that is then the lead
to follow. Note its limit, measured above: it produces **the same verdict on a
`permissive=1` AVC**, without pointing out that the operation succeeded.

`audit2allow` goes further and writes the missing rule:

```bash
sudo ausearch -m avc --success no -ts recent -c chronyd --input-logs | audit2allow
```

```text
#============= chronyd_t ==============
allow chronyd_t user_home_t:file read;
```

Read that rule above all: it does not allow `chronyd` to read *that* file, it
allows it to read **every file carrying the `user_home_t` type** on the machine,
that is to say all the home directories. A rule names types, never paths. With
`-M`, `audit2allow` goes all the way to the installable module:

```bash
cd /tmp && sudo ausearch -m avc --success no -ts recent -c chronyd \
  --input-logs | audit2allow -M atelier-chrony
```

```text
******************** IMPORTANT ***********************
To make this policy package active, execute:

semodule -i atelier-chrony.pp
```

> That invitation is a trap. `semodule -i` carves a permanent exception into the
> policy to work around a mislabelled file that a `restorecon` would have fixed
> in a second: the hole stays open long after the incident is forgotten. The
> guide ranks `audit2allow -M` as the **third and last** option, after the label
> and the boolean, and requires reading the rule with `audit2allow -w` before
> installing it.

One last word about `sealert`, often quoted: it comes from the
`setroubleshoot-server` package, absent here as in any minimal installation, and
as in an exam.

```bash
rpm -q setroubleshoot-server
```

```text
package setroubleshoot-server is not installed
```

Knowing how to read the raw AVC is therefore not a fallback: it is the expected
skill.

**The reflex to keep**, faced with a service that fails with a "Permission
denied" the Unix permissions do not explain:

1. `getenforce`: is SELinux enforcing anything?
2. `sudo ausearch -m avc --success no -ts recent`, with `--input-logs` if you
   have no terminal: pull out the denials that were actually enforced.
3. Read `permissive=` before any conclusion: `1` means logged, not blocked.
4. Read the operation and `tclass`: they point to the family of fix.
5. Read `scontext` and `tcontext`: the type of the requester and that of the
   target.
6. Fix the cause, and only as a last resort consider a module.
