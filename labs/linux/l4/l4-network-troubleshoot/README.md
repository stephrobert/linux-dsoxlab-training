# Lab — diagnose a down network connection

## Reminder

[**Network diagnosis on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/)

When "it does not work", the question is not which command to run, but at which
layer the failure sits. So you climb up in order: the link, the address, the
route, the name, then the service. Each layer has its command (`ip link`,
`ip addr`, `ip route get`, `getent hosts`, `ss -tlnp`) and its own symptom. An
interface can be fully configured and still be inactive: it is the live state
that is authoritative, never the configuration file.

## The course

The examples below build a complete demonstration network in a network
namespace, on the `203.0.113.0/24` subnet, with an HTTP server on port 8080: the
challenge deals with another interface, other addresses and other tools. The
point is to learn to read the symptoms, not to copy a line.

Before diagnosing anything, know what you have at hand. On the AlmaLinux 10 VM
of this lab:

```bash
for c in ip ss ping curl getent dig nc traceroute mtr nmap; do
  printf "%-12s %s\n" "$c" "$(command -v $c || echo ABSENT)"
done
```

```text
ip           /usr/sbin/ip
ss           /usr/sbin/ss
[...]
dig          /usr/bin/dig
nc           ABSENT
traceroute   ABSENT
mtr          ABSENT
nmap         ABSENT
```

`nc`, `traceroute` and `mtr` are **missing**, whereas the online guide gives them
as the first command of several paths. So you have to know how to do without
them: `curl` tests a TCP port, and **bash** opens a socket all by itself with
`/dev/tcp/<host>/<port>`. Conversely `ifconfig`, `netstat` and `route` are indeed
there (the `net-tools` package, pulled in by the VM preparation), but these are
the deprecated commands: stick to `ip` and `ss`.

### A disposable test bench: the network namespace

You do not learn to break a network on the machine you are connected through. A
**network namespace** (`netns`) gives you a complete, isolated network stack: its
own interfaces, its own routing table, its own firewall rules. You link it to the
machine with a `veth` pair, two virtual interfaces welded together like the two
ends of a cable.

```bash
sudo ip netns add banc
sudo ip link add veth-atelier type veth peer name veth-banc
sudo ip link set veth-banc netns banc
sudo ip addr add 203.0.113.1/24 dev veth-atelier
sudo ip link set veth-atelier up
sudo ip netns exec banc ip link set lo up
sudo ip netns exec banc ip link set veth-banc up
sudo ip netns exec banc ip addr add 203.0.113.2/24 dev veth-banc
```

`ip netns exec banc <command>` runs a command **inside** the namespace. Seen from
the inside, the rest of the machine does not exist:

```bash
sudo ip netns exec banc ip -br addr
# lo               UNKNOWN        127.0.0.1/8 ::1/128
# veth-banc@if4    UP             203.0.113.2/24 fe80::c098:bdff:fecf:9d1a/64
```

The `@if4` is valuable: it is the index of the interface on the other side. On
the machine side, `ip link show veth-atelier` symmetrically shows
`link-netns banc`.

### The link: `ip link` before anything else

A link has **two** states, and that is the first thing to read. The
administrative state (`UP` or `DOWN`) says whether you enabled it. The physical
state (`LOWER_UP`) says whether the cable is plugged in. Let us cut the end of
the cable that is inside the bench:

```bash
sudo ip netns exec banc ip link set veth-banc down
ip -br link show veth-atelier
```

```text
veth-atelier@if3 DOWN           9a:1d:e8:2a:ca:4c <NO-CARRIER,BROADCAST,MULTICAST,UP>
```

Read carefully: the `UP` flag is still there (the interface is enabled), but
`LOWER_UP` has gone and `NO-CARRIER` shows up. Nobody is plugged in on the other
side. `ip -br addr` is even more misleading, it shows the address as if all was
well:

```text
veth-atelier@if3 DOWN           203.0.113.1/24 fe80::981d:e8ff:fe2a:ca4c/64
```

The address is configured, the route exists, and yet `ping` receives nothing. A
`veth` pair reproduces exactly the symptom of an unplugged cable or a switched-off
switch port. Bring the link back up, and the traffic flows again:

```bash
sudo ip netns exec banc ip link set veth-banc up
ip -br link show veth-atelier
# veth-atelier@if3 UP    9a:1d:e8:2a:ca:4c <BROADCAST,MULTICAST,UP,LOWER_UP>
```

Two commands complete this layer: `ip neigh show dev veth-atelier` shows the MAC
address learned on the other side (`203.0.113.2 lladdr c2:98:bd:cf:9d:1a STALE`),
proof that layer 2 works, and `ip -s link show <iface>` gives the `errors` and
`dropped` counters, which must stay at zero.

### The address and the route: `ip route get` rather than `ip route`

`ip route` lists the table; `ip route get <destination>` answers the only
question that matters: where will **this** packet leave from? The nuance is not
cosmetic. Let us take the bench back at the moment when the address was set but
the interface not yet enabled:

```bash
ip route | grep 203 || echo "(aucune route 203.0.113.0/24)"
ip route get 203.0.113.2
```

```text
(aucune route 203.0.113.0/24)
203.0.113.2 via 10.10.30.1 dev eth0 src 10.10.30.12
    cache
```

That is the real face of a routing failure on an ordinary machine. The direct
route does not exist (the kernel only creates the connected route once the
interface is enabled), so the packet leaves towards the **default gateway**, on
the wrong interface, and gets lost: `curl` ends in a timeout. The guide announces
an `unreachable` in case of a routing problem; as soon as a default route exists,
you will not see `unreachable`, you will see an unexpected `dev`. That is the
line you have to know how to read.

Once the interface is enabled, the same command tells the truth:

```text
203.0.113.2 dev veth-atelier src 203.0.113.1
    cache
```

`Network is unreachable` does exist, but only when **no** route covers the
destination, default route included. The bench, which has no gateway, shows it:

```bash
sudo ip netns exec banc ip route get 8.8.8.8
# RTNETLINK answers: Network is unreachable
sudo ip netns exec banc ping -c1 -W1 8.8.8.8
# ping: connect: Network is unreachable
```

Finally, note that everything set with `ip addr add` or `ip link set up` lives
**in memory**: nothing survives a reboot. Persistent configuration is handled
elsewhere, by NetworkManager on this family of distributions.

### The name: `getent hosts` rather than `ping`

Testing resolution with `ping <name>` means testing two things at once and not
knowing which one failed. `getent hosts` queries resolution **alone**, through
the same path as applications (the one in `/etc/nsswitch.conf`):

```bash
getent hosts serveur-banc.lab ; echo "rc=$?"     # rc=2, no output
ping -c1 -W1 serveur-banc.lab
# ping: serveur-banc.lab: Name or service not known
curl -sS --connect-timeout 3 http://serveur-banc.lab:8080/
# curl: (6) Could not resolve host: serveur-banc.lab
```

No packet left towards the network: no point looking for a firewall. To prove
that **only** the name is at fault, short-circuit resolution with
`curl --resolve`, which maps a name to an address for the duration of one
request:

```bash
curl -sS --resolve serveur-banc.lab:8080:203.0.113.2 http://serveur-banc.lab:8080/
# page de test
```

The service answers perfectly: the failure really is in the naming. Two traps to
know about. First, **`dig` does not see `/etc/hosts`**: it talks directly to the
DNS server, whereas applications go through NSS. On this VM, the two tools give
two different answers for the same name:

```bash
getent hosts atelier.lab      # ::1        atelier.lab atelier.lab
dig +short atelier.lab        # 10.10.30.12
```

A triumphant `dig` therefore proves nothing about what the application will see.
Second, `dig +short` returns **0 even on an NXDOMAIN**, with empty output, while
`getent hosts` returns 2: in a script, test with `getent`, and keep `dig` to read
the header of the answer and the resolver queried.

```bash
dig serveur-banc.lab | grep -E "^;; ->>HEADER|^;; SERVER"
# ;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 33212
# ;; SERVER: 10.10.30.1#53(10.10.30.1) (UDP)
```

That resolver comes from `/etc/resolv.conf` (here `nameserver 10.10.30.1`,
written by NetworkManager). Be wary of `resolvectl status`, often quoted: the
`systemd-resolved` service is **not active** on this VM and the command fails
with `Failed to get global data: The name is not activatable`.

### The service: who listens, who filters

Last layer, that of the remote service. `ss -tlnp` lists listening sockets (`-t`
TCP, `-l` listening, `-n` without resolution, `-p` with the process):

```bash
sudo ip netns exec banc ss -tlnp
```

```text
State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
LISTEN 0      5        203.0.113.2:8080      0.0.0.0:*    users:(("python3",pid=3208,fd=3))
LISTEN 0      5          127.0.0.1:8081      0.0.0.0:*    users:(("python3",pid=3462,fd=3))
```

Read the **Local Address** column, not only the port. The service on port 8081
only listens on `127.0.0.1`: it answers locally and refuses any connection coming
from the network, while `systemctl` declares it perfectly active. Without `sudo`,
`ss` does show the sockets but leaves the `Process` column empty.

Lacking `nc`, there are two ways to test a port. `bash` first, which gives the
raw error message:

```bash
timeout 3 bash -c "echo > /dev/tcp/203.0.113.2/9090"
# bash: connect: Connection refused
```

`curl` next, but it needs `-v`: since version 8, its summary message drowns the
real cause under a pointless "Could not connect to server".

```bash
curl -v --connect-timeout 3 http://203.0.113.2:9090/ 2>&1 | grep "^\*"
```

```text
[...]
* connect to 203.0.113.2 port 9090 from 203.0.113.1 port 54814 failed: Connection refused
* Failed to connect to 203.0.113.2 port 9090 after 0 ms: Could not connect to server
```

Now let us filter. A namespace has **its own** `nftables` rules: everything that
follows has no effect on the machine, `nft list tables` showing on the machine
side only the `inet firewalld` table.

```bash
sudo ip netns exec banc nft add table inet filtre
sudo ip netns exec banc nft add chain inet filtre entree \
  "{ type filter hook input priority 0; policy accept; }"
sudo ip netns exec banc nft add rule inet filtre entree tcp dport 8080 drop
time curl -sS --connect-timeout 5 http://203.0.113.2:8080/
```

```text
curl: (28) Connection timed out after 5002 milliseconds
real	0m5.009s
```

Same port, same service, a radically different message: `Connection refused`
above, a **timeout** here. A refusal is an answer, so the host is reachable and
nothing is listening. A timeout is silence, so something is dropping the packets.
It is the only one of the four messages that points at filtering.

### Four messages, four failures, and the case of `ping`

Each layer has its message. Recognising them means jumping straight to the right
command instead of checking everything again:

| Message | What it proves | Where to look |
|---|---|---|
| `Name or service not known`, `Could not resolve host` | no packet left, the name was not resolved | `getent hosts`, `/etc/resolv.conf`, `dig` |
| `Network is unreachable` | no route covers the destination | `ip route get <ip>`, `ip route show default` |
| `Connection refused` | the host answers, nothing listens on that port | `ss -tlnp` on the remote machine |
| a timeout | packets leave, nothing comes back: filtering | firewall on both sides, return route |

That leaves the case of `ping`, a bad first test for two reasons. It mixes
resolution and reachability, as we have just seen. And it tests ICMP, a protocol
the target service does not use. Both mistakes can be demonstrated on the bench.
With the rule that blocks port 8080, `ping` is perfectly reassuring while the
service is unreachable:

```text
2 packets transmitted, 2 received, 0% packet loss, time 1006ms
```

And conversely, blocking ICMP only:

```bash
sudo ip netns exec banc nft flush chain inet filtre entree
sudo ip netns exec banc nft add rule inet filtre entree ip protocol icmp drop
ping -c2 -W1 203.0.113.2 | tail -2
# 2 packets transmitted, 0 received, 100% packet loss, time 1033ms
curl -sS --connect-timeout 3 -o /dev/null -w "code=%{http_code}\n" http://203.0.113.2:8080/
# code=200
```

The `ping` fails at 100 %, the service answers `200`. Concluding "the machine is
off" from a silent `ping` is therefore a reasoning error, not an acceptable
shortcut: always test the port actually in use.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ip -br link` shows `NO-CARRIER` and `UP` together | interface enabled, but nothing plugged in on the other side |
| the address shows up in `ip addr` and nothing gets through | read the link state: an address survives a dead link |
| `ip route get` points at an unexpected `dev` | the direct route is missing, the packet leaves via the default route |
| `Network is unreachable` | no route, default one included, covers the destination |
| `Name or service not known` | resolution failed, no packet sent: see `/etc/resolv.conf` |
| `dig` answers while the application fails | `dig` ignores `/etc/hosts`, compare with `getent hosts` |
| `Connection refused` | nothing listens: `ss -tlnp`, check the listening address (`127.0.0.1`?) |
| clean timeout on a specific port | filtering: local firewall, remote firewall or return route |
| silent `ping`, service nevertheless reachable | ICMP filtered: never conclude from `ping` alone |
| `resolvectl` fails with `not activatable` | `systemd-resolved` is inactive here, read `/etc/resolv.conf` |
| the configuration disappears at reboot | `ip addr add` does not persist, you have to go through NetworkManager |

To dismantle the bench, first stop what runs inside it, then delete the
namespace: the disappearance of one end of a `veth` takes the other with it.

```bash
sudo ip netns pids banc         # what still lives in the bench
sudo kill <pid> ...             # stop it
sudo ip netns del banc
ip netns list                   # no output
ip -br link                     # veth-atelier is gone
```

The order is not decorative. Run while the servers were still running,
`ip netns del banc` did empty `ip netns list`, but `veth-atelier` was still
there, `UP`: a namespace survives the deletion of its name as long as a process
occupies it. So check with `ip -br link`, not `ip netns list`.
