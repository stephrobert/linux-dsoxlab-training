# Lab — bond + bridge link aggregation with nmcli

## Reminder

[**Bond & bridge on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/)

A **bond** aggregates several links into a single logical interface, for
redundancy or throughput; a **bridge** is a software switch that puts several
interfaces on the same L2 segment. The two combine: the bond at the bottom, the
bridge on top. `nmcli con add type bond|dummy|bridge`, the `bond.options` option
and the controller/port pair wire the whole thing, and each connection profile
persists across reboot. `/proc/net/bonding/<bond>` and
`/sys/class/net/<bridge>/brif/` show the result on the kernel side. Work on the
dedicated interfaces given by the task list, never on the management interface.

## The course

The examples below build an `agg0` aggregation on two test links `demo0` and
`demo1`, under a `pont0` bridge, with `miimon=200` and the address
`192.0.2.10/24`: the challenge will ask you for other names and other values.
The point is to learn the method, not to copy a line. The output comes from an
AlmaLinux 10.2 VM (kernel 6.12) with `nmcli` 1.56; `192.0.2.0/24` is a prefix
reserved for documentation, no real machine carries it.

### Identify first the card that carries your session

The guide opens on this warning: aggregating the interface you are connected
through cuts your own session, with no way back.

```bash
ip route get 1.1.1.1
nmcli -t -f NAME,DEVICE,TYPE con show --active
```

```text
1.1.1.1 via 10.10.30.1 dev eth0 src 10.10.30.14 uid 1001
cloud-init eth0:eth0:802-3-ethernet
```

The default route goes out through `eth0`, driven by the `cloud-init eth0`
profile: **neither that card nor that profile must appear in any command of this
course**.

### A bridge and an aggregation answer two opposite needs

They get confused because they look alike on the command line. The guide tells
them apart by the direction in which they work:

- an **aggregation** (bond) merges several physical links into a single
  interface, for **redundancy** (one cable goes down, the other takes over) or
  for **throughput**. It looks **downwards**, towards the hardware;
- a **bridge** is a **software switch** that places several interfaces on the
  same segment, to give network access to **virtual machines** or containers. It
  looks **upwards**, towards the machines.

The two combine: this is the classic architecture of a virtualisation host. The
**mode** then decides how the links cooperate, and the right-hand column is the
only one that counts in operation:

| Mode | Behaviour | Constraint on the switch side |
|---|---|---|
| `active-backup` (1) | one active link, the other on standby | **none** |
| `balance-rr` (0) | packet-by-packet distribution | none, but risk of reordering |
| `802.3ad` (4, LACP) | the links add up, negotiated in LACP | **LACP port-channel configured on the far side** |

### Build two test links and aggregate them

A `dummy` interface is a purely software card that the kernel creates on demand.
It enrols in an aggregation exactly like a real card, which makes it possible to
demonstrate everything without touching the management link. We deliberately
start in `balance-rr`, we will change mode afterwards:

```bash
sudo nmcli con add type bond ifname agg0 con-name demo-agg \
  bond.options "mode=balance-rr,miimon=200" ipv4.method disabled ipv6.method disabled
sudo nmcli con add type dummy ifname demo0 con-name port-a controller demo-agg port-type bond
sudo nmcli con add type dummy ifname demo1 con-name port-b controller demo-agg port-type bond
ip -br link
```

```text
Connection 'demo-agg' (7937f0c0-22bd-49f0-8081-bbf9f68a8395) successfully added.
[... two identical lines for port-a and port-b ...]
agg0     UP        e6:20:b2:04:08:1d <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP>
demo0    UNKNOWN   e6:20:b2:04:08:1d <BROADCAST,NOARP,SLAVE,UP,LOWER_UP>
demo1    UNKNOWN   e6:20:b2:04:08:1d <BROADCAST,NOARP,SLAVE,UP,LOWER_UP>
```

The three interfaces share **the same MAC address**, that of the aggregation:
seen from the outside, there is only one card. Together with the `MASTER` and
`SLAVE` markers, this is the sign that the enrolment succeeded. The real state
lives in a kernel file:

```bash
cat /proc/net/bonding/agg0
```

```text
Bonding Mode: load balancing (round-robin)
MII Status: up
MII Polling Interval (ms): 200
[...]
Slave Interface: demo0
MII Status: up
Link Failure Count: 0
[... same block for demo1 ...]
```

That file is the **source of truth**: effective mode, polling interval, list of
links and health of each one. `miimon` asks the kernel to check the state of the
links every 200 ms; without it, no automatic failover. Let us switch to
`active-backup`, with a preferred link:

```bash
sudo nmcli con mod demo-agg bond.options "mode=active-backup,miimon=200,primary=demo0"
grep "Bonding Mode" /proc/net/bonding/agg0     # => load balancing (round-robin)
```

The profile on disk does say `mode=active-backup`, the kernel is still running
round-robin: `nmcli con mod` **writes** the configuration, it does not apply it.
You have to reactivate, and also reactivate the ports, which reactivating the
controller detaches:

```bash
sudo nmcli con up demo-agg
sudo nmcli con up port-a && sudo nmcli con up port-b
cat /proc/net/bonding/agg0
```

```text
Connection successfully activated (controller waiting for ports) [...]

Bonding Mode: fault-tolerance (active-backup)
Primary Slave: demo0 (primary_reselect always)
Currently Active Slave: demo0
MII Status: up
[...]
Slave Interface: demo0
MII Status: up
[... same for demo1 ...]
```

The `controller waiting for ports` message says exactly what is happening: the
controller is up, it is waiting for its ports. An aggregation whose ports have
all gone down stays in that state, with `Currently Active Slave: None`.

### Prove the failover, and what LACP gives without a switch

An aggregation that has never failed over before your eyes remains a promise:

```bash
sudo ip link set demo0 down
grep -E "Currently Active|Slave Interface|MII Status|Link Failure" /proc/net/bonding/agg0
ip -br link show agg0
```

```text
Currently Active Slave: demo1
MII Status: up
Slave Interface: demo0
MII Status: down
Link Failure Count: 1
Slave Interface: demo1
MII Status: up
Link Failure Count: 0
agg0    UP    6e:5b:a7:b8:ac:a2 <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP>
```

Three things to read. The active link has become `demo1`. The `Link Failure
Count` of `demo0` went to **1** and it will not go back down: that failure
history tells you a link gave way even if everything is fine at the moment you
look. And above all, **the aggregation stays `UP`**: for the upper layers,
nothing happened. Let us bring the link back:

```bash
sudo ip link set demo0 up
grep -E "Currently Active|Link Failure Count" /proc/net/bonding/agg0
```

```text
Currently Active Slave: demo0
Link Failure Count: 1
Link Failure Count: 0
```

`demo0` **took over again** on its own, because it is declared `primary`.
Without that parameter, the aggregation would have stayed on `demo1`.

Same manipulation in `802.3ad` (`bond.options "mode=802.3ad,miimon=200"`, then
reactivation of the controller and of the ports): `/proc/net/bonding/agg0` does
announce `IEEE 802.3ad Dynamic link aggregation`, but both links go
`MII Status: down` and each ends up in a **different aggregator**
(`Aggregator ID: 2` and `Aggregator ID: 3`). Nothing is aggregated, for want of
an LACP port-channel configured on the switch on the far side: this is exactly
the constraint announced by the table of modes. Treacherous detail, the
aggregation itself keeps displaying `MII Status: up`; never rely on that line
alone, always go down to the ports. We go back to `active-backup` before moving
on.

### Put a bridge on top: the address changes carrier

Let us first give an address to the aggregation, then create the bridge, whose
default parameters deserve a look:

```bash
sudo nmcli con add type bridge ifname pont0 con-name demo-pont ipv4.method disabled ipv6.method disabled
nmcli -f bridge.stp,bridge.forward-delay,bridge.priority con show demo-pont
cat /sys/class/net/pont0/bridge/forward_delay
```

```text
bridge.stp:                             yes
bridge.forward-delay:                   15
bridge.priority:                        32768
1500
```

`stp` is **enabled by default**: the bridge takes part in the *Spanning Tree
Protocol*, which detects network loops. `forward-delay` is 15 seconds on the
`nmcli` side and `1500` on the kernel side, which counts in hundredths of a
second: same value, two units. Let us enrol the aggregation:

```bash
ip -br addr show agg0
sudo nmcli con mod demo-agg controller demo-pont port-type bridge
sudo nmcli con up demo-agg && sudo nmcli con up port-a && sudo nmcli con up port-b
ip -br addr show agg0
nmcli -f ipv4.method,ipv4.addresses con show demo-agg
```

```text
agg0    UP    192.0.2.10/24
agg0    UP
```

The address has **disappeared**, and the last command displays nothing at all:
when a connection becomes a port of a bridge, NetworkManager leaves it no IPv4
setting whatsoever. The file on disk confirms it, its `[ipv4]` section has been
replaced by an empty `[bridge-port]` section, under a header that has become
`port-type=bridge`. This is the classic surprise of the topic: **a port has no
address, it is the bridge that carries it**. On a real card, the production
address must therefore be moved onto the bridge in the same move, on pain of an
outage.

```bash
sudo nmcli con mod demo-pont ipv4.method manual ipv4.addresses 192.0.2.10/24
sudo nmcli con up demo-pont
ip -br addr show pont0
bridge link show
```

```text
pont0    DOWN    192.0.2.10/24
14: agg0: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 master pont0 state listening priority 32 cost 100
```

The bridge has the address but it is **`DOWN`**, and its port is in `listening`.
Nothing is broken: it is STP doing its job. By polling every five seconds, you
see the complete sequence:

```text
  5s  port: learning     pont0  DOWN  <NO-CARRIER,BROADCAST,MULTICAST,UP>
 15s  port: learning     pont0  DOWN  <NO-CARRIER,BROADCAST,MULTICAST,UP>
 20s  port: forwarding   pont0  UP    <BROADCAST,MULTICAST,UP,LOWER_UP>
```

A bridge port goes through `listening` then `learning`, each lasting
`forward-delay`, before moving to `forwarding`. **About thirty seconds of
silence** during which the bridge passes no traffic. This is the number one
cause of "it does not work" on this topic: you test too early. You can do away
with it when no loop is possible, with `sudo nmcli con mod demo-pont bridge.stp
no` followed by reactivating the bridge, the controller and the ports:
`bridge link show` then shows `state forwarding` **immediately**, and `pont0`
comes up right after. The price to pay is real: without STP, two paths between
the same switches produce a broadcast storm that saturates the segment. On a
virtualisation host whose bridge has only one link to the outside, the loop is
impossible and turning STP off is common; elsewhere, leave it on. Final check of
the stack: `ls /sys/class/net/pont0/brif/` lists `agg0`, and in `ip -br link`
the four interfaces share the same MAC address.

### `master`/`slave` or `controller`/`port`: the vocabulary has changed

Many guides still online write `master <bond> slave-type bond`, and that is a
real source of confusion. On `nmcli` 1.56, both vocabularies work and query
**the same property**:

```bash
nmcli -f connection.master,connection.slave-type,connection.controller,connection.port-type con show port-a
```

```text
connection.master:                      7937f0c0-22bd-49f0-8081-bbf9f68a8395
connection.slave-type:                  bond
connection.controller:                  7937f0c0-22bd-49f0-8081-bbf9f68a8395
connection.port-type:                   bond
```

Two useful details. The value returned is the **UUID** of the controller, not
its name, even if you designated it by name at creation time. And whatever
keyword you use, the file written on disk always uses the **modern** form,
`controller=` and `port-type=`. The manual confirms the direction of the change:
`man nmcli | grep -i "deprecated for ethernet"` returns
`bond-slave (deprecated for ethernet with controller)` and its twin for
`bridge-slave`. The other way round, everything coming from the kernel sticks to
the old vocabulary: `/proc/net/bonding/` writes `Slave Interface`, `ip -br link`
displays the `MASTER` and `SLAVE` markers, and `bridge link show` says
`master pont0`. Remember the rule: **`nmcli` speaks modern, the kernel speaks
old**, and both designate the same thing.

### Undo, and troubleshoot

A single command removes the four profiles, their files and their interfaces:

```bash
sudo nmcli con delete demo-pont demo-agg port-a port-b
nmcli con show ; ip -br link ; ls /proc/net/bonding
```

```text
Connection 'demo-pont' (8da45496-...) successfully deleted.
[... three identical lines ...]
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
lo               5a266d1c-6574-4c58-9d79-067b8f446d10  loopback  lo
eth0     UP        52:54:00:cd:00:13 <BROADCAST,MULTICAST,UP,LOWER_UP>
ls: cannot access '/proc/net/bonding': No such file or directory
```

The deletion is **asynchronous**: right after the command, `ip -br link` still
showed `agg0`, `demo0` and `demo1` detached with new MAC addresses, and
`nmcli con show` still listed the profiles with a `--` in the `DEVICE` column. A
few seconds later everything had disappeared, `/proc/net/bonding` included,
since it only exists as long as an aggregation exists. Check on all three
planes: profiles, interfaces, files.

| Symptom | Likely cause | Fix |
|---|---|---|
| The profile mode does not match `/proc/net/bonding` | `con mod` writes, it does not apply | reactivate the controller **then** each port |
| `Currently Active Slave: None`, `MII Status: down` | ports not brought back up after the reactivation | `nmcli con up <port>` for each one |
| The ports stay `MII Status: down` in `802.3ad` | no LACP on the far side | switch to `active-backup`, or configure the port-channel |
| No failover when a link goes down | `miimon` missing from the `bond.options` | add `miimon=<ms>` |
| The preferred link does not take over again | no `primary=` | add it to the `bond.options` |
| The bridge stays `DOWN` with `NO-CARRIER` | port in `listening`/`learning`, STP in progress | wait twice `forward-delay`, or `bridge.stp no` |
| The enrolled interface lost its address | normal behaviour | set the address on the bridge |
| Nothing makes sense | the journal gives the exact reason | `sudo journalctl -u NetworkManager -b --no-pager \| tail -50` |

One last reflex: before validating, re-read `/proc/net/bonding/<bond>` and
`/sys/class/net/<bridge>/brif/`. These are the only two places where the state
is the kernel's, and not that of your intention.
