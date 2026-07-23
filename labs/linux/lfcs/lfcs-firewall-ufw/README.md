# Lab — Debian firewall with ufw

## Reminder

[**ufw on the companion guide**](https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/)

`ufw allow <service|port>` adds a rule; `ufw enable` turns the firewall on and
makes it persistent at boot; `ufw status` shows the rules. It is the Debian
counterpart of `firewall-cmd`. Always keep `OpenSSH` allowed before enabling.

## The course

The examples below open a monitoring service on `9100/tcp` and a PostgreSQL
database on `5432/tcp`: the challenge will ask you for another service. Learn the
allow / enable / check / undo sequence, do not copy a line. Real output from an
Ubuntu 24.04.4 LTS, `ufw 0.36.2-6`.

### Where ufw stands on this machine

Before setting a single rule, record the state you will have to be able to
restore: it hides a trap.

```bash
sudo ufw status ; systemctl is-enabled ufw ; systemctl is-active ufw
grep ^ENABLED /etc/ufw/ufw.conf ; sudo iptables -S
```

```text
Status: inactive
enabled
active
ENABLED=no
-P INPUT ACCEPT
-P FORWARD ACCEPT   [...]
```

Read carefully: the systemd unit `ufw.service` is **`enabled` and `active`**,
while `ufw status` answers **`inactive`**. These are two distinct notions. The
unit is only a launcher; the real state of the firewall lives in `ENABLED` in
`/etc/ufw/ufw.conf`, which only `ufw enable` and `ufw disable` write. Hence the
practical consequence: **`systemctl status ufw` will never tell you whether the
firewall is filtering**. The only reliable answer is `ufw status`, confirmed by
the three `iptables` policies at `ACCEPT`. Ubuntu ships ufw installed but
disarmed: that is your point of comparison.

### The golden rule: allow SSH before enabling

ufw's default policy is `deny incoming`: at activation, **everything that is not
explicitly allowed drops**, including port 22. On a remote server, the order of
the next two commands therefore decides whether you keep your access. The rule
first, the activation next:

```bash
sudo ufw allow OpenSSH
sudo ufw show added
```

```text
Rules updated
Added user rules (see 'ufw status' for running firewall):
ufw allow OpenSSH
```

As long as ufw is inactive, the rules filter nothing: they pile up in a queue
that `ufw show added` displays, and will be applied as one block at activation.
That is what makes the preparation risk-free.

```bash
sudo ufw enable ; sudo ufw status verbose
```

```text
Command may disrupt existing ssh connections. Proceed with operation (y|n)? y
Firewall is active and enabled on system startup
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
22/tcp (OpenSSH)           ALLOW IN    Anywhere
[...]
```

The warning is not decorative: always check from a **new** connection, not only
in the terminal already open.

> **What the opposite mistake gives.** While writing this course, the SSH rule
> was deleted while ufw was still active. The current session survived, ufw
> letting established connections live on; the **next** one died silently:
> `ssh: connect to host ... port 22: Connection timed out`. No refusal, no
> message, the packet is dropped, and no second account catches that since
> `student` goes through the same port 22. The machine had to be shut down on the
> hypervisor side to rewrite `ENABLED=no` into the disk. **Without a rescue
> console, this mistake is final.**

Two reflexes follow from that. Keep **a second SSH session open** before touching
the firewall: it will survive a blunder and let you type `sudo ufw disable`. And
if SSH is exposed to the Internet, prefer `ufw limit 22/tcp` over `allow`:
according to the guide, `limit` blocks a source beyond six connections per thirty
seconds.

### What ufw actually builds inside netfilter

ufw is not a firewall: it is a **front end** that writes netfilter rules.

```bash
sudo iptables -S | wc -l
sudo iptables -S INPUT
sudo iptables -S ufw-user-input
update-alternatives --display iptables | sed -n '3p'
sudo nft list tables
```

```text
101
-P INPUT DROP
-A INPUT -j ufw-before-logging-input
[...]
-A ufw-user-input -p tcp -m tcp --dport 22 -m comment --comment "\'dapp_OpenSSH\'" -j ACCEPT
  link currently points to /usr/sbin/iptables-nft
# Warning: table ip filter is managed by iptables-nft, do not touch!
```

Three lines before activation, one hundred and one after. The `INPUT` policy went
from `ACCEPT` to `DROP` and the chain now only delegates to a dozen `ufw-*`
chains; your own rules land in a single one of them, `ufw-user-input`. On Ubuntu
24.04, `iptables` is in fact `iptables-nft`: all of this ends up in nftables,
which says so itself. Hence the guide's warning: **never mix ufw with iptables
rules set by hand**. A manual rule inserted into `INPUT` would come before the
`ufw-*` chains and would silently contradict the output of `ufw status`, which
only knows what ufw wrote. To preview a rule without applying it:
`ufw --dry-run allow …`.

### Application profiles

This is ufw's specificity compared to firewalld, and what the exam expects. A
**profile** is a file dropped into `/etc/ufw/applications.d/` by the package that
installs the service. Create one:

```bash
sudo tee /etc/ufw/applications.d/atelier-exporter <<'EOF'
[Exporteur]
title=Exporteur de metriques
description=Agent de collecte interroge par le superviseur
ports=9100/tcp
EOF
sudo ufw app list ; sudo ufw app info Exporteur
```

```text
Available applications:
  Exporteur
  OpenSSH
Profile: Exporteur
Title: Exporteur de metriques
[...]
Port:
  9100/tcp
```

The rule is then written with the profile name, more readable than a port
number:

```bash
sudo ufw allow Exporteur ; sudo ufw allow postgresql ; sudo ufw status
```

```text
To                         Action      From
OpenSSH                    ALLOW       Anywhere
Exporteur                  ALLOW       Anywhere
5432/tcp                   ALLOW       Anywhere
```

These two `allow` do not use the same mechanism, and the output gives it away.
`postgresql` is a **service** name resolved once and for all through
`/etc/services` (`grep ^postgresql /etc/services` returns `postgresql 5432/tcp`):
it becomes `5432/tcp` in the status, the name is lost. `Exporteur` is a
**profile**: it stays named, its definition being read back from the file. Hence
a consequence: modifying a profile already in use is not enough.

```bash
sudo sed -i 's|^ports=9100/tcp|ports=9100,9101/tcp|' /etc/ufw/applications.d/atelier-exporter
sudo ufw app update Exporteur
sudo ufw reload
sudo iptables -S ufw-user-input | grep Exporteur
```

```text
Rules updated for profile 'Exporteur'
Skipped reloading firewall
Firewall reloaded
-A ufw-user-input -p tcp -m multiport --dports 9100,9101 -m comment --comment "\'dapp_Exporteur\'" -j ACCEPT
```

`Skipped reloading firewall` is the warning not to miss: `app update` rewrites the
rules file but **leaves the in-memory firewall as it is**. Without the
`ufw reload`, the chain would have stayed on port 9100 only.

### Rule order matters, and ufw makes it visible

`ufw status numbered` numbers the rules, and that number is the real order of
evaluation. Add a denial for a specific host **after** a general allow:

```bash
sudo ufw deny from 10.10.30.1 to any port 9100 proto tcp comment 'test ordre'
sudo ufw status numbered
```

```text
[ 1] OpenSSH                    ALLOW IN    Anywhere
[ 2] Exporteur                  ALLOW IN    Anywhere
[ 3] 5432/tcp                   ALLOW IN    Anywhere
[ 4] 9100/tcp                   DENY IN     10.10.30.1                 # test ordre
```

The rule is listed, and yet it is useless. Proof from 10.10.30.1, with a service
listening on the port:

```bash
nc -zv 10.10.30.18 9100 ; sudo iptables -S ufw-user-input
```

```text
Connection to 10.10.30.18 9100 port [tcp/*] succeeded!
-A ufw-user-input -p tcp -m tcp --dport 9100 [...] -j ACCEPT
-A ufw-user-input -s 10.10.30.1/32 -p tcp -m tcp --dport 9100 -j DROP
```

netfilter reads from top to bottom and stops at the first verdict: the profile's
`ACCEPT` decides before the `DROP` of the last line is reached. A deny rule
placed after an allow that covers it **never applies**. Fix it by inserting at a
precise rank:

```bash
sudo ufw --force delete 4 ; sudo ufw status numbered
sudo ufw insert 1 deny from 10.10.30.1 to any port 9100 proto tcp comment 'test ordre'
```

```text
Rule inserted
[ 1] 9100/tcp                   DENY IN     10.10.30.1                 # test ordre
[ 2] OpenSSH                    ALLOW IN    Anywhere
[...]
```

The same `nc` no longer gets through: it stays blocked until its timeout (exit
code 124), with no refusal message, the signature of a `DROP`. Two details: the
numbers **shift** after every deletion, read `status numbered` again between two
`delete`; and `ufw delete allow Exporteur` works too, safer in a script.

### Enabling and persisting are the same command

This is the ergonomic difference with firewalld, where you have to remember
`--permanent`. Here `ufw enable` does both at once: it writes `ENABLED=yes` into
`/etc/ufw/ufw.conf`, and the rules live in `/etc/ufw/user.rules`
(`user6.rules` for IPv6):

```bash
sudo sed -n '/### RULES ###/,/### END RULES ###/p' /etc/ufw/user.rules
```

```text
### tuple ### deny tcp 9100 0.0.0.0/0 any 10.10.30.1 in comment=74657374206f72647265
-A ufw-user-input -p tcp --dport 9100 -s 10.10.30.1 -j DROP
### tuple ### allow tcp 22 0.0.0.0/0 any 0.0.0.0/0 OpenSSH - in
-A ufw-user-input -p tcp --dport 22 -j ACCEPT -m comment --comment 'dapp_OpenSSH'
```

Each rule appears there twice: the `### tuple ###` line is the form ufw knows how
to read back and renumber, the next one is its netfilter translation. Comments
are encoded in hexadecimal (`74657374206f72647265` decodes to `test ordre`). Do
not trust that for all it is worth: verify with a reboot, that is what the exam
does.

```bash
sudo systemctl reboot   # then, once the machine is back:
sudo ufw status numbered ; grep ^ENABLED /etc/ufw/ufw.conf
```

```text
Status: active
[ 1] 9100/tcp                   DENY IN     10.10.30.1                 # test ordre
[ 2] OpenSSH                    ALLOW IN    Anywhere
[...]
ENABLED=yes
```

State, rules **and order** came back intact, including the insertion in position
1. Nothing more to do: no `--permanent`, no `systemctl enable`.

One last point, the log. `ufw status verbose` shows `Logging: on (low)`, but
`/var/log/ufw.log` **does not exist** as long as no packet has been logged: it is
`rsyslog` that creates it at the first line, through `/etc/rsyslog.d/20-ufw.conf`.
A connection to a closed port triggers it, and writes a line
`[UFW BLOCK] ... SRC=10.10.30.1 DST=10.10.30.18 PROTO=TCP DPT=4444 SYN` in it. Be
careful, though, about what that log contains: at the `low` level, only the
packets blocked by the **default policy** appear in it. The explicit deny set
earlier on port 9100 left no trace in it (`grep -c DPT=9100` returns `0` while
`DPT=4444` counts four). A `ufw deny` filters silently; switch to
`sudo ufw logging medium` if you have to audit it.

### Troubleshooting and going back to the initial state

| Symptom | Likely cause | Fix |
|---|---|---|
| `ufw status` says `inactive` while `systemctl is-active ufw` says `active` | Two distinct notions: `ENABLED=no` in `/etc/ufw/ufw.conf` | `sudo ufw enable`, never `systemctl start` |
| SSH drops right after `ufw enable` | Port 22 not allowed, `deny incoming` policy | Rescue console, `sudo ufw disable`, fix, try again |
| A `deny` rule listed in `status` blocks nothing | It is placed after an `allow` that covers it | `sudo ufw status numbered`, then `ufw delete N` and `ufw insert 1 ...` |
| A modified profile has no effect | `ufw app update` writes the file without reloading | `sudo ufw reload` |
| The service stays unreachable while `status` looks fine | Manual `iptables` rule upstream of the `ufw-*` chains | `sudo iptables -S INPUT`, and do not mix the two tools |
| `/var/log/ufw.log` missing, or rules invisible in `iptables -L` | No packet logged; ufw writes its own chains | Normal; `ufw logging medium` and `iptables -S ufw-user-input` |

To undo everything, **the order is critical**: disable ufw **before** removing
the SSH rule, never the other way round.

```bash
sudo ufw disable                     # first: nothing filters any more
sudo ufw delete allow Exporteur      # only then, the rules
sudo ufw delete allow postgresql
sudo ufw delete deny from 10.10.30.1 to any port 9100 proto tcp
sudo ufw delete allow OpenSSH
sudo rm -f /etc/ufw/applications.d/atelier-exporter
```

Deleted by its full description, a rule goes away without confirmation; by its
number, `ufw delete N` asks you to confirm. `ufw reset` does all of that at once
but **also** erases your SSH allow: use it only in front of a console, and set
`sudo ufw allow OpenSSH` back immediately after. Finally, check the return to the
starting point, by comparing with the first section:

```bash
sudo ufw status ; sudo ufw show added ; sudo ufw app list ; sudo iptables -S
```

```text
Status: inactive
Added user rules (see 'ufw status' for running firewall):
(None)
Available applications:
  OpenSSH
-P INPUT ACCEPT
-P FORWARD ACCEPT   [...]
```

One detail if you compare right after the `disable`: the `ufw-*` chains, emptied
of their rules, **stay declared** until the next reboot. `sudo iptables -S` then
returns some forty lines of jumps, without a single verdict. It is the three
`ACCEPT` policies that are authoritative.
