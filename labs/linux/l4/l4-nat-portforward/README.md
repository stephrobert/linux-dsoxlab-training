# Lab — persistent NAT port forwarding with nftables

## Reminder

[**NAT & port forwarding on the companion guide**](https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/)

Forwarding needs `net.ipv4.ip_forward = 1` (persist it in `/etc/sysctl.d/`).
nftables does the work: a `nat` table with a `prerouting` chain (`dnat` = the
port forward) and a `postrouting` chain (`masquerade` = SNAT). On RHEL,
persistence goes through `/etc/sysconfig/nftables.conf` (which `include`s your
`.nft` file) plus the enabled `nftables` service.

## The course

The examples below set up a demonstration gateway between two fictitious
networks, with its own ports and its own addresses: the challenge will ask you
for others. The point is to learn the method and to know how to prove it, not to
copy a line. All the outputs that follow were produced on an AlmaLinux 10.

### The two directions of NAT

NAT rewrites the addresses of the packets that cross the gateway, and nftables
does it in two distinct chains:

- **`prerouting`** (inbound): as soon as the packet arrives, the **destination**
  address is rewritten. That is **DNAT**, the one of port forwarding.
- **`postrouting`** (outbound): just before sending, the **source** address is
  rewritten. That is **SNAT**; its automatic form is **masquerade**, which takes
  the address of the outgoing interface.

Remember the guide's formula: **DNAT to come in, masquerade to go out**. And
remember the method: a forward is not demonstrated by reading a rule, but by
measuring twice, with and without it.

### The test bench: two networks without a second machine

To prove a forward, you need a client coming from the outside and a service to
reach. **Network namespaces** (`ip netns`) give both on a single machine: each
has its own network stack, its own interfaces and its own routing table. A
`veth` pair links them to the host like a cable.

```bash
for ns in client backend; do sudo ip netns add demo-$ns; done
sudo ip link add to-client  type veth peer name eth-c
sudo ip link add to-backend type veth peer name eth-b
sudo ip link set eth-c netns demo-client
sudo ip link set eth-b netns demo-backend

# Host side: the gateway has one foot in each network
sudo ip addr add 198.51.100.1/24 dev to-client  && sudo ip link set to-client up
sudo ip addr add 203.0.113.1/24  dev to-backend && sudo ip link set to-backend up

# The client, with the host as default route
sudo ip netns exec demo-client ip addr add 198.51.100.2/24 dev eth-c
sudo ip netns exec demo-client ip link set eth-c up
sudo ip netns exec demo-client ip route add default via 198.51.100.1

# The backend, deliberately without a default route (we will come back to it)
sudo ip netns exec demo-backend ip addr add 203.0.113.2/24 dev eth-b
sudo ip netns exec demo-backend ip link set eth-b up
```

Finally, two services on the high port `18443`, one on the host and one in the
backend, each serving a page that says where it comes from:

```bash
sudo mkdir -p /tmp/demo-local /tmp/demo-distant
echo SERVEUR-LOCAL-PORT-18443   | sudo tee /tmp/demo-local/index.html
echo SERVEUR-DISTANT-PORT-18443 | sudo tee /tmp/demo-distant/index.html
sudo sh -c 'cd /tmp/demo-local && setsid python3 -m http.server 18443 &'
sudo sh -c 'cd /tmp/demo-distant && setsid ip netns exec demo-backend \
  python3 -m http.server 18443 >/tmp/demo-distant.log 2>&1 &'
```

### Forwarding a port to a local service

First case: the entry port and the service are on the **same** machine. A
service listening on `18443` is exposed on `9443`.

Measurement 1, without any rule:

```bash
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
curl: (7) Failed to connect to 198.51.100.1 port 9443 after 0 ms: Could not connect to server
```

The table, the chain, the rule:

```bash
sudo nft add table ip demo-nat
sudo nft add chain ip demo-nat prerouting '{ type nat hook prerouting priority dstnat ; }'
sudo nft add rule  ip demo-nat prerouting iifname "to-client" tcp dport 9443 dnat to 198.51.100.1:18443
sudo nft list table ip demo-nat
```

```text
table ip demo-nat {
	chain prerouting {
		type nat hook prerouting priority dstnat; policy accept;
		iifname "to-client" tcp dport 9443 dnat to 198.51.100.1:18443
	}
}
```

Measurement 2, the same `curl`, preceded by the state of forwarding:

```bash
sysctl net.ipv4.ip_forward
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
net.ipv4.ip_forward = 0
SERVEUR-LOCAL-PORT-18443
```

**Remember that `0`.** A forward to a local service did not need routing: the
packet comes in, its destination is rewritten to an address of the machine
itself, it is delivered locally. It crosses nothing.

Measurement 3, the rule is removed, nothing else changes:

```bash
sudo nft flush chain ip demo-nat prerouting
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
curl: (7) Failed to connect to 198.51.100.1 port 9443 after 0 ms: Could not connect to server
```

Three measurements, and the rule is the only variable: the mechanism is proven.

### Forwarding to another machine: routing becomes mandatory

Second case, the real gateway: the service is on **another** machine. Only the
target of the `dnat` changes.

```bash
sudo nft add rule ip demo-nat prerouting iifname "to-client" tcp dport 9443 dnat to 203.0.113.2:18443
sysctl net.ipv4.ip_forward
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
net.ipv4.ip_forward = 0
curl: (28) Connection timed out after 5003 milliseconds
```

Note the change of symptom: `(7)` becomes `(28)`. An immediate refusal means
"nobody is listening"; a **timeout** means that the packet went somewhere and
that nothing came back. Here, it was dropped for lack of routing.

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
net.ipv4.ip_forward = 1
curl: (28) Connection timed out after 5002 milliseconds
```

Still failing, but no longer for the same reason. `conntrack` says so:

```bash
sudo conntrack -L | grep dport=9443
```

```text
tcp 6 114 SYN_SENT src=198.51.100.2 dst=198.51.100.1 sport=59474 dport=9443 [UNREPLIED] src=203.0.113.2 dst=198.51.100.2 sport=18443 dport=59474
```

Read the **two tuples**. The first one is the connection as seen from the
client. The second is the return the kernel expects: it should come from
`203.0.113.2:18443` and go to `198.51.100.2`. The `[UNREPLIED]` mention says
that this return never arrived. The DNAT did work, the packet was indeed routed;
it is the **reply** that is missing.

### MASQUERADE: bringing the replies back

Why does the backend not reply? Its routing table:

```text
203.0.113.0/24 dev eth-b proto kernel scope link src 203.0.113.2
```

It only knows its own network. The packet it received carried
`src=198.51.100.2`, an address it has no way of reaching. That is the trap
pointed out by the guide: without a return route to the client, the translation
breaks on the way. Two possible ways out: give the backend a default route
towards the gateway, or hide the source so that it believes it is talking to its
direct neighbour. The second one is the NAT way:

```bash
sudo nft add chain ip demo-nat postrouting '{ type nat hook postrouting priority srcnat ; }'
sudo nft add rule  ip demo-nat postrouting ip daddr 203.0.113.2 oifname "to-backend" masquerade
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
SERVEUR-DISTANT-PORT-18443
```

The log of the remote server (`/tmp/demo-distant.log`) shows who contacted it:

```text
203.0.113.1 - - [22/Jul/2026 16:42:35] "GET / HTTP/1.1" 200 -
```

`203.0.113.1` is the gateway, not the client: the source was indeed masqueraded.
And `conntrack` now carries **both** rewrites on a single line:

```text
tcp 6 119 TIME_WAIT src=198.51.100.2 dst=198.51.100.1 sport=37046 dport=9443 src=203.0.113.2 dst=203.0.113.1 sport=18443 dport=37046 [ASSURED]
```

Destination rewritten (`198.51.100.1:9443` becomes `203.0.113.2:18443`) and
source rewritten (`198.51.100.2` becomes `203.0.113.1`). This is the number one
diagnostic tool of NAT: it shows what the kernel does, not what you think you
wrote.

### Making all this persistent

Two things have been set in memory, and **both disappear at reboot**.

**Routing.** A `sysctl -w` does not survive; a file in `/etc/sysctl.d/` is
needed:

```bash
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/98-demo-routeur.conf
sudo sysctl --system
```

```text
* Applying /etc/sysctl.d/98-demo-routeur.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
```

`sysctl --system` replays exactly what boot does: it is the way to check your
file without rebooting.

> **The trap to know about.** Deleting the file does not put the previous value
> back. Measured: after `rm` of the file, `sysctl -n net.ipv4.ip_forward` still
> returns `1`. The file decides the value **at boot**, not the current value. To
> really go back, set it by hand with `sudo sysctl -w net.ipv4.ip_forward=0`.

**The ruleset.** Write the table into a file, then prove that it is enough to
rebuild it by simulating the reboot:

```bash
sudo sh -c 'nft list table ip demo-nat > /etc/nftables/demo-nat.nft'
sudo nft delete table ip demo-nat          # as at reboot: everything is lost
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
sudo nft -f /etc/nftables/demo-nat.nft     # what the service will do at boot
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
curl: (7) Failed to connect to 198.51.100.1 port 9443 after 0 ms: Could not connect to server
SERVEUR-DISTANT-PORT-18443
```

What remains is to have this file replayed at boot, and that is the role of the
`nftables` service. **Do not guess the path it reads, ask the unit:**

```bash
systemctl cat nftables | grep ExecStart
```

```text
ExecStart=/sbin/nft -f /etc/sysconfig/nftables.conf
```

> **Gap with the guide.** The guide writes `nft list ruleset > /etc/nftables.conf`,
> which is the Debian convention. On this AlmaLinux 10, `/etc/nftables.conf`
> **does not exist** (`ls` returns "No such file or directory") and the service
> reads `/etc/sysconfig/nftables.conf`. Following the guide to the letter here
> would produce a file that nothing loads: a rule you believe persisted and that
> never comes back. The `systemctl cat` above is your safeguard, on any
> distribution.

This file accepts two forms: the rules written directly in it, or an `include`
directive pointing to your own `.nft` file. The second keeps your work separate
from that of the distribution.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Immediate `curl: (7)` | No rule matches | `nft list table ip <table>` |
| `curl: (28)` timing out | Packet gone with no return | `conntrack -L`, look for `[UNREPLIED]` |
| Local DNAT that fails | Wrong `iifname` or wrong port | Add a `counter` (below) |
| Remote DNAT with no effect | Routing disabled | `sysctl net.ipv4.ip_forward` must be `1` |
| The backend does not reply | No return route to the client | `masquerade` in `postrouting`, or default route on the backend side |
| Everything disappears at reboot | Ruleset not persisted | `systemctl cat nftables` to find the right file |

The **counter** answers the only question that matters when nothing works: is
the rule even traversed?

```bash
sudo nft add rule ip demo-nat prerouting iifname "to-client" tcp dport 9443 counter dnat to 203.0.113.2:18443
sudo nft list chain ip demo-nat prerouting
```

```text
iifname "to-client" tcp dport 9443 counter packets 1 bytes 60 dnat to 203.0.113.2:18443
```

A counter at zero rules NAT out straight away: the packet does not reach the
rule, look at the interface, the port or the routing upstream.

On AlmaLinux, **firewalld has its own table** and coexists with yours; the order
is given by the priority of the chains:

```bash
sudo nft list ruleset | grep "hook prerouting priority dstnat"
```

```text
		type nat hook prerouting priority dstnat + 10; policy accept;
		type nat hook prerouting priority dstnat; policy accept;
```

The first one is firewalld's, the second yours. The lower the value, the earlier
the chain is called: here yours goes first.

> **Care with the service.** `systemctl cat nftables` also shows
> `ExecStop=/sbin/nft flush ruleset`: stopping the service empties **the whole**
> ruleset, including the tables of another firewall. On a machine you depend on
> for your session, prefer `nft -f <file>` to test a reload.

Finally, dismantle the test bench. Deleting a namespace takes its `veth`
interface and the processes that were running in it away with it:

```bash
sudo nft delete table ip demo-nat
sudo ip netns delete demo-client && sudo ip netns delete demo-backend
sudo sysctl -w net.ipv4.ip_forward=0
```
