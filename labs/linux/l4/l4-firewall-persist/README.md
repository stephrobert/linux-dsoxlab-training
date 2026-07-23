# Lab — open a firewalld service permanently

## Reminder

[**firewalld on the companion guide**](https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/)

`firewalld` filters by **zone** (default `public`). `firewall-cmd --add-service`
changes runtime only (lost on reload/reboot); `--permanent` writes the zone
config, and `--reload` applies permanent to runtime. Check with
`--list-services` (runtime) and `--permanent --list-services`.

Never remove `ssh` — that closes your management access.

## The course

The examples below open a **raw port `8443/tcp`** then the named service `ftp`,
on an AlmaLinux 10 demonstration machine: the challenge, for its part, will ask
you for another service. The point is to learn the runtime / permanent
mechanism, not to copy a line.

All the output reproduced here is that of the workshop machine.

### Where a rule applies: the zone

`firewalld` does not have one list of rules, it has one **per zone**. Each
network interface belongs to a zone, and a command without `--zone` targets the
**default zone**.

```bash
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --get-zone-of-interface=eth0
sudo firewall-cmd --get-active-zones
```

```text
public
public
public (default)
  interfaces: eth0
```

Here the two coincide: the default zone is `public`, and `eth0` (the one
carrying the SSH session) happens to be in `public`. **This is not a guarantee**,
it is a convenience of the default configuration. On a machine with several
cards, check both before writing anything.

`--list-all` gives the complete state of the active zone:

```bash
sudo firewall-cmd --list-all
```

```text
public (default, active)
  target: default
  [...]
  interfaces: eth0
  sources:
  services: cockpit dhcpv6-client ssh
  ports:
  [...]
  rich rules:
```

Three allowed services, no raw port. Everything else is refused: that is the
starting point. Note `ssh` in the list, it is your access. It must never leave
it.

### A test port to see the firewall at work

To prove that a rule acts, something has to be listening behind it. A tiny TCP
server that accepts then hangs up is enough:

```bash
nohup python3 -c 'import socketserver; socketserver.TCPServer(("",8443), socketserver.BaseRequestHandler).serve_forever()' >/dev/null 2>&1 &
ss -tlnp | grep 8443
```

```text
LISTEN 0      5      0.0.0.0:8443      0.0.0.0:*    users:(("python3",pid=28029,fd=3))
```

The service listens on every address. From **another machine**, you test the
connection without any dedicated client:

```bash
timeout 5 bash -c 'exec 3<>/dev/tcp/<ip-de-la-vm>/8443'; echo $?
```

```text
bash: connect: No route to host
1
```

`No route to host` is not a routing failure: the firewall does not merely ignore
the packet, it **rejects** it, and that rejection is what the client translates
this way. The service is running, the firewall makes it unreachable.

### Runtime: the draft that disappears on reload

```bash
sudo firewall-cmd --add-port=8443/tcp
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --list-ports
```

```text
success
8443/tcp
```

The second list is **empty**: the rule only exists in runtime. From the other
machine, the connection now goes through (`echo $?` answers `0`).

Then the reload:

```bash
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

```text
success

```

The following line is empty: no port left. `--reload` re-reads the permanent
configuration and **throws away** everything that was only in runtime. The
connection gives `No route to host` again, and the SSH session, for its part,
did not move (TCP connections already established survive the reload).

That is the behaviour to remember: the runtime is a **draft**. It is also your
safety net, a mistake in runtime is wiped by a `--reload`.

### Permanent: written on the disk, but inactive until the reload

The other way round is just as disconcerting:

```bash
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --list-ports              # runtime
sudo firewall-cmd --permanent --list-ports  # permanent
```

```text
success

8443/tcp
```

The rule is recorded, and yet the connection from the other machine is still
refused. `--permanent` **does not act on the running firewall**, it writes a
file. That is what the guide sums up as "added with `--permanent` without
`--reload`".

Here is that file:

```bash
sudo ls -l /etc/firewalld/zones/
sudo cat /etc/firewalld/zones/public.xml
```

```text
-rw-r--r--. 1 root root 393 Jul 22 16:22 public.xml
```

```xml
<zone>
  <short>Public</short>
  [...]
  <service name="ssh"/>
  <service name="dhcpv6-client"/>
  <service name="cockpit"/>
  <port port="8443" protocol="tcp"/>
  <forward/>
</zone>
```

A surprising detail: **before that command, `/etc/firewalld/zones/` was empty**.
The `public` zone shipped by the distribution lives in
`/usr/lib/firewalld/zones/public.xml`, and `--permanent` makes a local copy of
it on the first write. An empty directory therefore does not mean "no permanent
rule", it means "nothing has been customised yet".

All that is left is to apply:

```bash
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

```text
success
8443/tcp
```

This time the connection goes through, and it will still go through after a
reboot.

### `--runtime-to-permanent`, and its side effect

When you have chained several conclusive attempts in runtime, one command
freezes the current state in one go:

```bash
sudo firewall-cmd --runtime-to-permanent
sudo firewall-cmd --permanent --list-services
sudo firewall-cmd --permanent --list-ports
```

```text
success
cockpit dhcpv6-client ftp ssh
8443/tcp
```

Convenient, but to be handled knowingly: it **rewrites every zone**, not only
the one you were modifying. After that single command, the zones directory no
longer contained one file but eleven, plus six policy files:

```text
block.xml  dmz.xml  drop.xml  external.xml  home.xml  internal.xml
nm-shared.xml  public.xml  public.xml.old  trusted.xml  work.xml
```

No rule changed (compared with the originals in `/usr/lib/firewalld/`, these
files are identical apart from reformatting), but those local copies **now
mask** the definitions shipped by the distribution, for every zone at once. On a
server you keep, prefer the explicit sequence `--permanent` then `--reload`,
which touches a single file.

### Named service or numbered port: two separate lists

A `firewalld` "service" is an alias to one or more ports. You can inspect it
before opening it:

```bash
sudo firewall-cmd --info-service=ftp
```

```text
ftp
  ports: 21/tcp
  protocols:
  source-ports:
  modules:
  destination:
  includes:
  helpers: ftp
```

`--add-service=ftp` therefore opens `21/tcp`, and the definition mentions in
addition a connection tracking `helper`. An `--add-port=21/tcp` would open only
the port number, with nothing else: the two forms do not cover the same thing,
and above all they are not read in the same place.

```bash
sudo firewall-cmd --add-service=ftp
sudo firewall-cmd --list-services
sudo firewall-cmd --list-ports
```

```text
success
cockpit dhcpv6-client ftp ssh
8443/tcp
```

Two separate lists: `--list-services` will **never** show a port added by
`--add-port`, and the other way round. A service looked for in the wrong list
passes for absent. When in doubt, `--list-all` displays both.

Rule of choice: the named service when it exists (readable, maintainable), the
raw port for anything listening on a non-standard port.

### The right rule in the wrong zone

This is the most frequent mistake, and the most silent one: `firewall-cmd`
answers `success` and nothing works.

```bash
sudo firewall-cmd --remove-port=8443/tcp             # default zone
sudo firewall-cmd --zone=work --add-port=8443/tcp    # "work" zone
sudo firewall-cmd --zone=work --list-ports
sudo firewall-cmd --list-ports
sudo firewall-cmd --get-active-zones
```

```text
success
success
8443/tcp

public (default)
  interfaces: eth0
```

The port is indeed open in `work`, the command succeeded, and yet the connection
from the other machine is refused: **no interface is in `work`**, the rule sees
no packet go by. The traffic arrives through `eth0`, so in `public`.

Hence the reflex: `--get-active-zones` first, `--zone=<that one>` next, or
nothing at all if the active zone is already the default zone.

### Undo, and what must never be done

Removing a permanent rule takes the same pair of commands as adding it:

```bash
sudo firewall-cmd --permanent --remove-port=8443/tcp
sudo firewall-cmd --permanent --remove-service=ftp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

```text
public (default, active)
  [...]
  services: cockpit dhcpv6-client ssh
  ports:
  [...]
```

The starting state is restored. Three moves, on the other hand, cut the session
immediately, and the second administrator account does not save you since it
goes through the same port:

- `--remove-service=ssh` on the active zone;
- `--set-default-zone=drop` or `block`, two zones that do not allow `ssh`
  (their `--list-all` shows an empty `services:`);
- `--panic-on`, which cuts all incoming **and** outgoing traffic.

The guide documents them as incident response tools, to be used only with a
backup console access.

For everyday troubleshooting, two commands are worth all the rest:
`firewall-cmd --list-all` (what the active zone really allows) and
`sudo firewall-cmd --set-log-denied=unicast`, which makes the refused packets
appear in `journalctl -u firewalld`. Remember to set it back to `off`
afterwards.

The troubleshooting table of the companion guide covers the other symptoms (rule
visible but inactive, rule gone after reboot, port open but service
unreachable): it is worth reading before starting.
