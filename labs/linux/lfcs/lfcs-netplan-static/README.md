# Lab — static IP & route with netplan

## Reminder

[**netplan on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/)

netplan describes the network in `/etc/netplan/*.yaml`. A device gets
`addresses:` for static IPs and `routes:` (`to:`/`via:`) for static routes.
`netplan generate` translates without activating anything, `netplan try` applies
with automatic rollback, `netplan apply` applies with no safety net (persistent at
boot in both cases). Config files must be `0600`.

Work on the dedicated interface named by the challenge, never on the management
interface, the one that carries your default route.

## The course

The examples below work on a test interface `atelier0`, a file
`/etc/netplan/70-atelier.yaml` and the address `203.0.113.10/24`: the challenge
will ask you for another interface, another file and other addresses. Learn the
method, do not copy a line. All the output comes from an **Ubuntu 24.04.4 LTS** VM
(kernel **6.8.0-134-generic**) with **netplan.io 1.1.2-8ubuntu1~24.04.2** and
**systemd-networkd** as the backend; `203.0.113.0/24` is a prefix reserved for
documentation.

> **This is the most dangerous subject of the track.** netplan also configures the
> interface that carries your SSH session. A mistake applied with `netplan apply`
> throws you out with no recourse and forces console access. This whole course
> therefore takes place on an interface built for the occasion.

### First: which interface carries your session, and which file describes it

Two commands, in this order, before opening a single file. The first tells you
where your traffic goes out, the second tells you which file of `/etc/netplan/`
configures that interface:

```bash
ip route get 1.1.1.1
sudo grep -l enp1s0 /etc/netplan/*.yaml
```

```text
1.1.1.1 via 10.10.30.1 dev enp1s0 src 10.10.30.19 uid 1001
    cache
/etc/netplan/50-cloud-init.yaml
```

`enp1s0` is the management interface, `50-cloud-init.yaml` the **untouchable**
file: laid down by cloud-init, it designates the link by its MAC address
(`sudo netplan get ethernets` shows it) and gives it `dhcp4: true`. Note the name,
`enp1s0` and not `eth0`: Ubuntu's predictable names depend on the hardware. Always
record your own with `ip -br link`, do not copy the one from a tutorial.

### A throwaway interface, and the YAML that describes it

A `dummy` interface is a purely software card. netplan knows how to declare it
with the `dummy-devices:` family, and everything that follows (`addresses`,
`routes`, `nameservers`) is written **exactly** as for a real card. It is the
ideal training ground: nothing you do there can cut the session.

```yaml title="/etc/netplan/70-atelier.yaml"
network:
  version: 2
  renderer: networkd
  dummy-devices:
    atelier0:
      mtu: 1400
      addresses:
        - 203.0.113.10/24
      routes:
        - to: 192.168.240.0/24
          via: 203.0.113.254
          metric: 200
      nameservers:
        addresses: [9.9.9.9]
```

The `70-` prefix places the file **after** `50-cloud-init.yaml` in the reading
order (see below). `version: 2` is the netplan format, `renderer` the backend that
will execute, and `routes:` with `to:`/`via:` replaces the `gateway4:` of the old
tutorials, deprecated since netplan 0.103 according to the guide.

**Two spaces per level, never a tab.** This is the number one failure of the
subject, and the message leaves no doubt:

```text
/etc/netplan/70-atelier.yaml:7:1: Invalid YAML: tabs are not allowed for indent:
	- 203.0.113.10/24
^
```

Merely irregular indentation gives a neighbouring message,
`Invalid YAML: inconsistent indentation`. In both cases netplan gives you the
file, the line and the column: read it, it points at the exact error.

**Permissions matter.** A file created with `tee` is born in `644`, and netplan
holds it against you on every command:

```text
** (generate:19679): WARNING **: Permissions for /etc/netplan/70-atelier.yaml
are too open. Netplan configuration should NOT be accessible by others.
```

This is not fussiness: a netplan file can contain a Wi-Fi password **in clear
text** under `access-points:`, and in any case it reveals your addressing plan to
any local account. The fix, to be done as a reflex after every creation, is a
`sudo chmod 600` on the file. Careful, the warning is **only** a warning:
`netplan generate` still returns `0` and the too-open file is applied anyway.
NetworkManager keyfiles, on the other hand, are plainly and simply refused.

### Validating without applying: `generate`, `get`, and the rendering under `/run`

`netplan generate` translates your YAML into files for the backend, without
touching the network. Silence and exit code 0 amount to validation:

```bash
sudo netplan generate ; echo "rc=$?"
sudo ls /run/systemd/network/ ; ip -br link show atelier0
```

```text
rc=0
10-netplan-atelier0.netdev
10-netplan-atelier0.network
10-netplan-enp1s0.link
10-netplan-enp1s0.network
Device "atelier0" does not exist.
```

Two lessons in this output. First, **netplan is only a generator**: it produced a
`.netdev` (create the card) and a `.network` (address it), and it is
systemd-networkd that will execute. Your YAML has become INI, readable with
`sudo cat /run/systemd/network/10-netplan-atelier0.network`:

```text
[Match]
Name=atelier0
[Network]
Address=203.0.113.10/24
DNS=9.9.9.9
[Route]
Destination=192.168.240.0/24
Gateway=203.0.113.254
Metric=200
```

Second, **`generate` applies nothing**: the interface still does not exist. And
these files live under `/run`, regenerated at every boot: never edit them, they
will be overwritten. The only source of truth is `/etc/netplan/`.
`sudo netplan get dummy-devices.atelier0` answers the other question, that of the
**merged** configuration of all your files.

### `netplan try`: the 120-second safety net

`netplan try` applies the configuration then waits for a keyboard confirmation.
Without `Enter` within the delay, it **rolls back on its own**: your session being
dead, you confirm nothing, and the machine becomes reachable again by itself. The
default delay is 120 seconds (`DEFAULT_INPUT_TIMEOUT = 120` in the code of the
command), adjustable with `--timeout`.

```bash
sudo netplan try --timeout 20
```

```text
Do you want to keep these settings?

Press ENTER before the timeout to accept the new configuration

Changes will revert in 20 seconds [...] Changes will revert in  1 seconds
Reverting.
```

During the trial the configuration is really active; after `Reverting.`, the
address and the route are gone. With `Enter`, the answer is
`Configuration accepted.` and the configuration stays, already persistent. The
command requires a real terminal, since it reads your keyboard.

> **Three limits of the safety net, measured on this machine.**
>
> - `netplan try` does **not** back up `/etc/netplan` but the rendering, that is
>   `/run/systemd/network`. After `Reverting.`, your YAML is still there, and so
>   applied at the next boot: a revert does not undo the file.
> - A formidable corollary: if you ran `netplan generate` **before** the `try`,
>   `/run` already contains the new configuration, so the backup photographs the
>   new configuration, and the revert goes back nowhere. Two identical trials,
>   only `generate` sets them apart: without it, the address is indeed gone after
>   `Reverting.`; with it, it is still there.
> - A virtual card already created is destroyed neither by the rollback nor by
>   `netplan apply`: it loses its addresses and keeps its shell. Only
>   `sudo ip link del atelier0` makes it disappear.

The practical rule that follows, when working remotely: **run `try` first**. It
does its own `generate` and refuses an invalid YAML *before* touching the network,
returning 78 (`EX_CONFIG`):

```text
Invalid YAML: inconsistent indentation:
       routes: []
       ^
rc=78
```

Keep `netplan generate` for machines whose console you hold, or run it **after** an
accepted `try`. `netplan apply`, for its part, has no rollback mechanism at all:
reserve it for the local console or for a trivial change.

### Alphabetical order, and what "merging" means

All the `.yaml` files of `/etc/netplan/` are read in the **alphabetical order** of
their names, then merged. Hence the numeric prefixes. Let us add a second file,
read after ours, which redeclares the same interface, and read the merge again
with `sudo netplan get dummy-devices.atelier0`:

```yaml title="/etc/netplan/80-atelier-suite.yaml"
network:
  version: 2
  dummy-devices:
    atelier0:
      mtu: 1300
      addresses:
        - 203.0.113.60/24
```

```text
addresses:
- "203.0.113.10/24"
- "203.0.113.60/24"
mtu: 1300
[...]
```

Look closely: the merge does not behave the same way depending on the type of the
key. The scalar `mtu` is **replaced**, the last file read wins, 1300 overwrites
1400. The `addresses` list is **concatenated**, both addresses coexist. The real
state after applying confirms it, `ip -br addr show atelier0` gives
`203.0.113.10/24 203.0.113.60/24` and `ip -d link show atelier0` shows `mtu 1300`.

This is the most bewildering failure of the subject: a correct configuration,
applied without error, and yet with no effect, because a file with a higher name
redefines the same key. `netplan get` settles it in one command, since it shows the
result after merging and not what you wrote.

### The two backends, and the world across the way

netplan configures nothing itself, it generates the configuration of another
service, designated by `renderer`: **systemd-networkd** on a server,
**NetworkManager** on a workstation. Which one is running here?
`systemctl is-active systemd-networkd NetworkManager` answers `active` then
`inactive`. Beware of that second word: on this machine NetworkManager is not even
installed, and `systemctl status NetworkManager` answers
`Unit NetworkManager.service could not be found.` The command does not distinguish
"installed but stopped" from "absent". Declaring a `renderer` pointing at an
absent backend is the classic trap, and it passes validation:

```bash
sudo netplan generate ; echo "rc=$?"        # with renderer: NetworkManager
sudo ls /run/systemd/network/ /run/NetworkManager/system-connections/
```

```text
rc=0
/run/systemd/network/:  10-netplan-enp1s0.link  10-netplan-enp1s0.network
/run/NetworkManager/system-connections/:  netplan-atelier0.nmconnection
```

`generate` validates the **syntax**, not the **feasibility**: it returns 0 without
a word and simply moves the rendering to the other backend, in INI format. At
apply time, the penalty falls (`Failed to start NetworkManager.service: Unit
NetworkManager.service not found.`, followed by a Python traceback), the interface
loses its address and `networkctl list` declares it `unmanaged`. Always align the
`renderer` with the service actually running.

The table below sums up what changes when you move from the RHEL way, seen in the
NetworkManager lab, to the Ubuntu way. It is the comparison to have in mind in the
exam room:

| | netplan (Ubuntu) | NetworkManager (RHEL) |
|---|---|---|
| What you write | declarative YAML in `/etc/netplan/*.yaml` | `nmcli con add/mod` commands |
| Who executes | a generated backend: networkd or NetworkManager | NetworkManager itself |
| Where persistence lives | `/etc/netplan/*.yaml` in `0600` | `/etc/NetworkManager/system-connections/*.nmconnection` in `0600` |
| Too-open permissions | warning, the file is applied anyway | file **refused** at load time |
| Remote safety net | `netplan try`, automatic rollback | no equivalent, `nmcli con up` applies flat out |
| Error recovery | wait for the delay to expire | re-enable the old profile, if it is still reachable |
| Several files | merged in alphabetical order | one profile per connection, no merging |

Remember above all the "safety net" row: it is netplan's decisive advantage, and it
has no equivalent on the `nmcli` side, where a mistyped address throws you out
instantly.

### Persistence, troubleshooting and back to the initial state

Persistence is not deduced, it is verified. After `sudo systemctl reboot`, with
writing the file as the only action, `ip -br addr` and `ip route show`:

```text
enp1s0           UP             10.10.30.19/24 metric 100 [...]
atelier0         UNKNOWN        203.0.113.10/24 fe80::1c0a:a1ff:fe05:38b9/64
default via 10.10.30.1 dev enp1s0 proto dhcp src 10.10.30.19 metric 100
192.168.240.0/24 via 203.0.113.254 dev atelier0 proto static metric 200
203.0.113.0/24 dev atelier0 proto kernel scope link src 203.0.113.10
```

The interface came back on its own with its address and its route, and the default
route did not move. Note the last line, `203.0.113.0/24 [...] scope link`: it is
deduced from the `/24` netmask, nobody declared it, and it is what makes the `via`
gateway reachable; a gateway set outside that network would give a missing route.
`sudo netplan status --diff` completes the check by marking the differences between
the real state and your files.

| Symptom | Likely cause | Fix |
|---|---|---|
| `Invalid YAML: tabs are not allowed for indent` | a tab in the file | two spaces per level, never a tab |
| `Invalid YAML: inconsistent indentation` | irregular indentation levels | realign on the column shown |
| `Permissions ... are too open` | file created in `644` | `sudo chmod 600 /etc/netplan/<file>.yaml` |
| Applied without error, no effect | a file with a higher name redefines the key | `sudo netplan get` to read the merge |
| Interface `unmanaged`, with no address | `renderer` pointing at an absent backend | `systemctl is-active systemd-networkd NetworkManager` |
| `Reverting.` but the config is still there | `netplan generate` run before the `try` | run `try` alone again, with no prior `generate` |
| The test interface survives the removal of the file | `apply` does not destroy a virtual card | `sudo ip link del <interface>` |
| Session lost after a change | `netplan apply` used instead of `netplan try` | take over from the console, then apply the rule |

When the table is not enough, `journalctl -u systemd-networkd` and
`sudo netplan --debug apply` give the faulty step. To undo everything, remove the
file, apply, then delete the card: both gestures are needed, `apply` only takes the
address off it.

```bash
sudo rm -f /etc/netplan/70-atelier.yaml /etc/netplan/80-atelier-suite.yaml
sudo netplan apply
sudo ip link del atelier0
ip -br addr ; sudo ls /run/systemd/network/ ; ip route get 1.1.1.1
```

```text
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp1s0           UP             10.10.30.19/24 metric 100 fe80::5054:ff:fecd:18/64
10-netplan-enp1s0.link  10-netplan-enp1s0.network
1.1.1.1 via 10.10.30.1 dev enp1s0 src 10.10.30.19 uid 1001
```

No more interface, no more generated file, the session is intact. One last reflex,
before even the first line is written: back up the directory with
`sudo cp -a /etc/netplan /root/netplan.avant`, the only way to get back to an
identical state when nothing makes sense any more.
