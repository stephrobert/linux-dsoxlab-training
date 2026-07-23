# Lab — SELinux boolean and port labeling

## Reminder

[**SELinux on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Under enforcing SELinux, you grant access without turning it off. **Booleans**
toggle predefined policy switches — `setsebool -P <bool> on` makes it persistent.
**Port labeling** lets a confined service bind a non-standard port —
`semanage port -a -t <type> -p tcp <port>`. Read with `getsebool` and
`semanage port -l`.

## The course

The examples below are about the `deny_ptrace` boolean and about a second SSH
server that you want to make listen on port `2222`: the challenge will ask you
for another boolean and another port. Learn the method, it transposes as is.
All the output reproduced here was recorded on an **AlmaLinux 10** VM with
`policycoreutils-python-utils` 3.10 and `audit` 4.0.3.

### Check that SELinux really is enforcing

Nothing that follows makes sense if SELinux does nothing. Two commands:

```bash
getenforce
# Enforcing
sudo sestatus
```

```text
SELinux status:                 enabled
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
[...]
```

The last two lines do not say the same thing: **`Current mode`** is the mode in
force right now, **`Mode from config file`** the one for the next boot. A
difference points at a `setenforce` typed by hand and never consolidated, since
`setenforce` only touches the current mode:

```bash
sudo setenforce 0 && getenforce   # Permissive
sudo setenforce 1 && getenforce   # Enforcing
```

> **Do not modify `/etc/selinux/config` in this lab.** A typo in this file can
> make the machine unbootable, and going through `disabled` forces a full
> relabel at the next boot, the files created without SELinux no longer having
> any label. Permissive mode is taken with `setenforce 0` and given back right
> away with `setenforce 1`.

### Find the right boolean and read its state

The `targeted` policy of AlmaLinux 10 exposes **314 booleans** (`getsebool -a |
wc -l`). You search them by keyword:

```bash
getsebool -a | grep ptrace
# deny_ptrace --> off
```

`getsebool` gives a value, `semanage boolean -l` gives the full context:

```bash
sudo semanage boolean -l | grep deny_ptrace
```

```text
SELinux boolean                State  Default Description

deny_ptrace                    (off  ,  off)  Allow deny to ptrace
```

**Remember these two columns between parentheses, the whole topic is there**:
the first is the **current state** (the one `getsebool` returns), the second
the **state recorded in the policy**, reloaded at the next boot. As long as
they are identical, all is well.

### The trap: `setsebool` without `-P` does not survive a reboot

Let us enable the boolean without `-P`. The effect is immediate and quite real:
`strace` can no longer trace anyone.

```bash
time sudo setsebool deny_ptrace on
# real  0m0.019s
getsebool deny_ptrace
# deny_ptrace --> on
strace -c -f /bin/true
# strace: ptrace(PTRACE_TRACEME, ...): Permission denied
```

But the two columns have diverged, and `-C`, which only displays the **recorded
local modifications**, returns **nothing at all**:

```bash
sudo semanage boolean -l | grep deny_ptrace
# deny_ptrace                    (on   ,  off)  Allow deny to ptrace
sudo semanage boolean -l -C
# (no line)
```

Current `on`, policy `off`: a change absent from `-C` only exists in the memory
of the kernel. Reboot:

```bash
sudo systemctl reboot
# then, once reconnected:
getsebool deny_ptrace
# deny_ptrace --> off
```

Lost. The service that depended on this boolean will fall over again weeks
later, and nobody will make the connection.

With `-P`, the change is written into the policy store:

```bash
time sudo setsebool -P deny_ptrace on
# real  0m0.326s
sudo semanage boolean -l -C
# deny_ptrace                    (on   ,   on)  Allow deny to ptrace
```

The two columns agree, and the modification is now visible in `-C`. After a
second reboot, `getsebool deny_ptrace` still answers `on`.

On this VM, `-P` costs **about 0.33 s against 0.02 s** without it, some fifteen
times more: it rewrites the policy, where the volatile version only writes one
byte in `/sys/fs/selinux`. On a slower or busier machine, the gap is counted in
seconds, and it is that delay that makes people forget the `-P`.

Finally, `setsebool -P <bool> off` restores the right value but **leaves the
trace in `-C`**. `semanage boolean` has no `-d`; it is `-D`, which removes all
the local boolean customisations, that makes it disappear:

```bash
sudo setsebool -P deny_ptrace off
sudo semanage boolean -l -C     # deny_ptrace is still there, as (off , off)
sudo semanage boolean -D
sudo semanage boolean -l -C     # empty
```

### Label a port with `semanage port`

A confined domain can only bind the ports whose **type** it is allowed. You
first read what the policy already knows:

```bash
sudo semanage port -l | grep ssh_port_t
# ssh_port_t                     tcp      22
sudo semanage port -l | grep 2222
# (nothing: 2222 is associated with no type)
```

You add the port to the wanted type:

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo semanage port -l | grep ssh_port_t
# ssh_port_t                     tcp      2222, 22
```

**`-C` is the option to remember**: it only displays what you added yourself,
which lets you find your own modifications in the middle of the 466 lines of
the policy.

```bash
sudo semanage port -l -C
```

```text
SELinux Port Type              Proto    Port Number

ssh_port_t                     tcp      2222
```

When the port already belongs to another type, `-a` does not stop: it warns and
switches to modification on its own.

```bash
sudo semanage port -a -t ssh_port_t -p tcp 3306
# Port tcp/3306 already defined, modifying instead
```

A `-m` instead of the `-a` does the same thing, without a message.
Get into the habit of using `-m` when you know the port is already defined: it
is explicit, and on older versions of `policycoreutils`, `-a` fails where `-m`
goes through. Beware too of reading `semanage port -l` after such an addition:
the port appears **under both types**, the original entry and yours. Only
`-l -C` removes the ambiguity.

Removal is done with `-d`, and only concerns your additions:

```bash
sudo semanage port -d -t ssh_port_t -p tcp 3306   # removes your local modification
sudo semanage port -d -t ssh_port_t -p tcp 22
# ValueError: Port tcp/22 is defined in policy, cannot be deleted
sudo semanage port -d -t ssh_port_t -p tcp 2223
# ValueError: Port tcp/2223 is not defined
sudo semanage port -m -t ssh_port_t -p tcp 2224
# ValueError: Port tcp/2224 is not defined
```

One last point: `semanage` always writes into the policy store. There is no
volatile equivalent for ports, so a labeling survives a reboot without your
having to ask for anything, unlike booleans.

### "Permission denied" when nothing justifies it

To put all this to the test, let us make a second `sshd` listen on port `2222`,
without touching the service in place:

```bash
sudo tee /etc/systemd/system/sshd-demo.service <<'EOF'
[Service]
ExecStart=/usr/sbin/sshd -D -e -p 2222 -o PidFile=/run/sshd-demo.pid
EOF
sudo systemctl daemon-reload && sudo systemctl start sshd-demo.service
```

Before the labeling, the service falls over:

```text
Active: failed (Result: exit-code)
sshd[1412]: Bind to port 2222 on 0.0.0.0 failed: Permission denied.
sshd[1412]: Cannot bind any address.
systemd[1]: sshd-demo.service: Main process exited, code=exited, status=255/EXCEPTION
```

**`Permission denied` although the service runs as root**, on a port above
1024, with a binary and a configuration that are perfectly readable. No Unix
permission explains this refusal, and neither does the firewall: it filters
incoming packets, it does not prevent a local process from reserving a port.

A methodological trap in passing: started **by hand**, the same server starts
without a murmur.

```bash
sudo /usr/sbin/sshd -p 2222 -e -o PidFile=/run/sshd-demo.pid   # no error
ps -eZ | grep sshd
# system_u:system_r:sshd_t:s0-s0:c0.c1023                1101 ? sshd
# unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023  1285 ? sshd
```

It inherits the `unconfined_t` context of your shell: not confined, therefore
not refused. Only **systemd** performs the transition to `sshd_t`. A test "by
hand" therefore proves nothing about the service: always go through
`systemctl`.

Once the port is labeled, the service starts:

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo systemctl restart sshd-demo.service
sudo ss -tlnp | grep 2222
# LISTEN 0 128 0.0.0.0:2222 0.0.0.0:* users:(("sshd",pid=1718,fd=7))
```

The port is open **locally**. A connection from another machine still fails
though, with a `bash: connect: No route to host`: that is `firewalld`
rejecting the packet, and it takes `sudo firewall-cmd --add-port=2222/tcp`. The
two layers are independent and are troubleshot separately: SELinux allows the
process to **reserve** the port, the firewall allows the traffic to **reach**
it.

### Reading the refusal: the AVC

The refusal is logged by `auditd`, and `sudo ausearch -m AVC -ts recent` plays
it back:

```text
type=AVC msg=audit(1784736098.894:318): avc:  denied  { name_bind } for  pid=1412
  comm="sshd" src=2222 scontext=system_u:system_r:sshd_t:s0-s0:c0.c1023
  tcontext=system_u:object_r:unreserved_port_t:s0 tclass=tcp_socket permissive=0
```

Five fields are enough to decide:

| Field | Value here | What it says |
|---|---|---|
| `denied { … }` | `name_bind` | the refused operation: reserving a port |
| `comm` / `src` | `sshd` / `2222` | who, and on what |
| `scontext` | `sshd_t` | the **source** type, that of the process |
| `tcontext` | `unreserved_port_t` | the **target** type, that of the port today |
| `permissive` | `0` | the refusal **blocked**; `1` would have said "logged but let through" |

It is `tcontext` that gives the repair: the port carries `unreserved_port_t`
whereas `sshd_t` expects `ssh_port_t`. So nothing else is missing but a
`semanage port -a`.

The `permissive` field is easy to check: after `setenforce 0`, the same attempt
succeeds and the AVC is logged with `permissive=1`. That is what permissive
mode is good for in a diagnosis, and also why "it works in permissive" is not a
solution, only a test.

Two warnings from the field:

- **`sealert` is not available here**: `rpm -q setroubleshoot-server` answers
  `package setroubleshoot-server is not installed`. On a minimal image, do not
  count on it, know how to read the raw AVC;
  `sudo grep AVC /var/log/audit/audit.log` gives the same lines.
- In a **script** or through `ssh machine 'command'`, standard input is a pipe:
  `ausearch` reads from it instead of reading the logs and answers
  `<no matches>` although the refusals exist. Add `--input-logs` then.

Finally, beware of automatic suggestions. On this precise refusal,
`ausearch -m AVC -ts recent | audit2why` concludes:

```text
	Was caused by:
	The boolean nis_enabled was set incorrectly.
	Allow access by executing:
	# setsebool -P nis_enabled 1
```

That command would indeed make the refusal disappear, by allowing `sshd` to
open **any** unreserved port. Labeling the single wanted port is infinitely
more precise. `audit2why` points at a path, it does not choose the right one.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| The boolean is right today, wrong after a reboot | `setsebool` run without `-P`; check the two columns of `semanage boolean -l` |
| `semanage boolean -l -C` is empty although a boolean was just changed | the change is volatile, it was not written into the policy |
| `Permission denied` when starting a service, as root, on a free port | port not labeled; read `tcontext` in the AVC |
| The service starts by hand but not through `systemctl` | started by hand it stays `unconfined_t`; only systemd performs the transition |
| `Port tcp/N already defined, modifying instead` | the port already belongs to a type; use `-m` explicitly |
| `ValueError: Port tcp/N is defined in policy, cannot be deleted` | `-d` only removes your additions, not the original entries |
| `ValueError: Port tcp/N is not defined` | `-m` and `-d` require an already defined port; use `-a` to create |
| The service listens (`ss -tlnp`) but stays unreachable | this is no longer SELinux: see `firewall-cmd --list-ports` |
| `ausearch` answers `<no matches>` from a script | add `--input-logs` |
| `sealert: command not found` | `setroubleshoot-server` absent; read the raw AVC |

To undo everything, then prove the return to the original state: the last three
commands must return two empty lists and `Enforcing`.

```bash
sudo systemctl stop sshd-demo.service
sudo rm -f /etc/systemd/system/sshd-demo.service && sudo systemctl daemon-reload
sudo semanage port -d -t ssh_port_t -p tcp 2222
sudo setsebool -P deny_ptrace off && sudo semanage boolean -D
sudo firewall-cmd --reload

sudo semanage port -l -C
sudo semanage boolean -l -C
getenforce
```
