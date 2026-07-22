# Lab — persistent static IPv4 with NetworkManager

## Reminder

[**NetworkManager on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/)

On RHEL, `NetworkManager` owns the interfaces. `nmcli con add` creates a
connection profile; `ipv4.method manual` + `ipv4.addresses` sets a static
address; the profile lands in `/etc/NetworkManager/system-connections/` so it
survives reboot. `ip addr add` is volatile.

Work on the dedicated interface named in the brief, never on the management
interface.

## The course

The examples below work on a test interface `demo0`, a connection named
`demo-static` and the address `198.51.100.20/24`: the challenge will ask you for
another interface, another connection name and another address. The point is to
learn the method, not to copy a line. The outputs come from an AlmaLinux 10 VM
with `nmcli` 1.56; `198.51.100.0/24` is a prefix reserved for documentation, no
real machine carries it.

### First spot the connection that carries your session

This is the first command to type on a remote machine, before any change. It
tells you which interface your traffic goes through, and therefore which one to
never touch:

```bash
ip route get 1.1.1.1
nmcli -t -f NAME,DEVICE,STATE con show --active
```

```text
1.1.1.1 via 10.10.30.1 dev eth0 src 10.10.30.12 uid 1001
    cache
cloud-init eth0:eth0:activated
lo:lo:activated
```

The default route goes out through `eth0`, and `eth0` is driven by the
connection named `cloud-init eth0`. **That profile is untouchable**: an unlucky
`nmcli con mod` followed by an `nmcli con up` throws you out instantly, and the
guide is categorical, no command will bring you back without console access.
That is why the whole course takes place on an interface built for the occasion.

### What `ip addr add` does not do

Let us build a test interface of type `dummy`, a purely software card the kernel
agrees to create on demand, and set an address on it by hand:

```bash
sudo ip link add demo0 type dummy
sudo ip link set demo0 up
sudo ip addr add 198.51.100.20/24 dev demo0
ip -4 addr show demo0
```

```text
5: demo0: <BROADCAST,NOARP,UP,LOWER_UP> mtu 1500 [...] state UNKNOWN
    inet 198.51.100.20/24 scope global demo0
```

The address is there, the card is `UP`: apparently, the job is done. Let us look
though at what NetworkManager thinks of it:

```bash
nmcli device status
nmcli -f NAME,FILENAME con show
```

```text
DEVICE  TYPE      STATE                    CONNECTION
demo0   dummy     connecting (externally)  demo0
NAME             FILENAME
cloud-init eth0  /etc/NetworkManager/system-connections/cloud-init-eth0.nmconnection
demo0            /run/NetworkManager/system-connections/demo0.nmconnection
```

Here is the trap, and it is more insidious than "nothing happens": the daemon
**adopted** the interface and manufactured a connection of the same name for it.
An `nmcli con show` read too quickly would suggest a proper profile. The
`FILENAME` column settles it: that profile lives under **`/run`**, not under
`/etc`.

```bash
findmnt -no TARGET,FSTYPE /run
```

```text
/run tmpfs
```

`/run` is a `tmpfs`, a filesystem in RAM, recreated empty at every boot. The
profile is therefore lost at reboot, exactly like the address. **Remember to
read `FILENAME`**: `/etc` means persistent, `/run` means volatile. Let us clean
up with `sudo ip link del demo0`, which makes the interface and the `/run`
connection disappear at once.

### Creating a persistent profile

A profile is created in one command. The `type dummy` keyword replaces here the
`type ethernet` of the guide, everything else is identical to what you would
write for a real card:

```bash
sudo nmcli connection add type dummy ifname demo0 con-name demo-static \
  ipv4.method manual ipv4.addresses 198.51.100.20/24 autoconnect no
```

```text
Connection 'demo-static' (ac314bb7-9bee-493d-9a47-bec7ceef5710) successfully added.
```

Each keyword has a role: `ifname demo0` designates the target card, `con-name
demo-static` names the profile (that name is the one every following command
will use), `ipv4.method manual` says "fixed address, no DHCP" and
`ipv4.addresses` gives the address and its mask. The guide points out a
shortcut: `ip4 198.51.100.20/24` switches `ipv4.method` to `manual` on its own,
the explicit form above does the same thing while saying it.

The `autoconnect no` is deliberate, it will be used below to take apart the
reboot trap. Note also what is **not** in the command: neither `ipv4.gateway`
nor `ipv4.dns`. On a real card you add them, as the guide shows; on a test
interface you refrain, because a gateway installs a default route that would
compete with the one of your management link.

### Configured is not active

The profile exists. The interface does not exist yet:

```bash
nmcli con show
ip -br link
```

```text
NAME             UUID                                  TYPE      DEVICE
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
demo-static      ac314bb7-9bee-493d-9a47-bec7ceef5710  dummy     --

lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
eth0             UP             52:54:00:cd:00:11 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

No `demo0` in `ip -br link`: the `--` dash in the `DEVICE` column is the symptom: profile
recorded, no card behind it. That is the fundamental distinction of the guide,
`nmcli connection` talks about **profiles**, `nmcli device` talks about
**cards**. Let us activate:

```bash
sudo nmcli connection up demo-static
nmcli -f GENERAL.DEVICE,GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS device show demo0
```

```text
Connection successfully activated (D-Bus active path: [...]/ActiveConnection/4)
GENERAL.DEVICE:                         demo0
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     demo-static
IP4.ADDRESS[1]:                         198.51.100.20/24
```

`GENERAL.STATE: 100 (connected)` is the **real** state of the card, and
`GENERAL.CONNECTION` says which profile produced it. The two commands do not
answer the same question: `con show` shows what is **written**, `device show`
shows what is **running**.

The classic troubleshooting case follows directly from that: `nmcli connection
modify` writes into the profile and applies nothing live.

```bash
sudo nmcli connection modify demo-static ipv4.addresses 198.51.100.21/24
nmcli -g ipv4.addresses con show demo-static      # what is configured
nmcli -g IP4.ADDRESS device show demo0            # what is active
```

```text
198.51.100.21/24
198.51.100.20/24
```

Two different values, no bug: the configuration and the current state are two
distinct things. You reconcile them by reactivating the profile, and
`nmcli -g IP4.ADDRESS device show demo0` then returns `198.51.100.21/24`.

```bash
sudo nmcli connection up demo-static
```

### The file on disk, and its `0600` permissions

It, and it alone, is what makes the persistence:

```bash
sudo ls -l /etc/NetworkManager/system-connections/
sudo cat /etc/NetworkManager/system-connections/demo-static.nmconnection
```

```text
-rw-------. 1 root root 331 Jul 22 13:30 cloud-init-eth0.nmconnection
-rw-------. 1 root root 232 Jul 22 16:35 demo-static.nmconnection

[connection]
id=demo-static
uuid=ac314bb7-9bee-493d-9a47-bec7ceef5710
type=dummy
autoconnect=false
interface-name=demo0

[ipv4]
address1=198.51.100.20/24
method=manual
[...]
```

A readable INI format, in `0600`, owned by `root`. Those permissions are not
decorative: these files contain the secrets (Wi-Fi keys, VPN credentials) in
clear text, and NetworkManager **refuses** to load a file that is too permissive.
Verifiable in one operation:

```bash
sudo chmod 0644 /etc/NetworkManager/system-connections/demo-static.nmconnection
sudo nmcli connection load /etc/NetworkManager/system-connections/demo-static.nmconnection
sudo journalctl -u NetworkManager -b --no-pager | tail -2
```

```text
Could not load file '/etc/NetworkManager/system-connections/demo-static.nmconnection'
[...] settings: load: failure to load "[...]/demo-static.nmconnection": File permissions (100644) are insecure
[...] audit: op="connections-load" [...] result="fail"
```

After a reboot, the verdict is final: the connection has **disappeared** from
`nmcli con show` while the file is still on disk. A `chmod 0600` followed by an
`nmcli connection load` brings it back immediately (and activates it right away
if `autoconnect` is set to `yes`).

### `autoconnect`, the real judge of the reboot

Our profile is perfect, on disk, in `0600`, and it will still not come back up.

```bash
nmcli -f connection.autoconnect con show demo-static
```

```text
connection.autoconnect:                 no
```

Proof by reboot, the only test that counts according to the guide:

```bash
sudo systemctl reboot
```

On the way back, `nmcli con show` then `ip -br link` give:

```text
demo-static      ac314bb7-9bee-493d-9a47-bec7ceef5710  dummy     --

lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
eth0             UP             52:54:00:cd:00:11 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

The profile survived, the interface did not. That is the exact trap of the
subject: a file on disk is not enough, NetworkManager must also be allowed to
activate it on its own. The fix fits in one line:

```bash
sudo nmcli connection modify demo-static connection.autoconnect yes
sudo grep -n autoconnect /etc/NetworkManager/system-connections/demo-static.nmconnection \
  || echo "(plus de ligne autoconnect)"
```

```text
(plus de ligne autoconnect)
```

A useful detail: the `autoconnect=false` line was not switched to `true`, it was
**removed**. A keyfile only records what departs from the default, and the
default is `yes`. So never conclude from the absence of the line that the setting
is missing. Second reboot, and this time:

```bash
nmcli con show --active
ip -4 -br addr show demo0
```

```text
NAME             UUID                                  TYPE      DEVICE
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
demo-static      ac314bb7-9bee-493d-9a47-bec7ceef5710  dummy     demo0

demo0            UNKNOWN        198.51.100.21/24
```

The interface came back on its own with its address, without typing anything.
Check along the way with `ip route` that the management link has not moved:

```text
default via 10.10.30.1 dev eth0 proto dhcp src 10.10.30.12 metric 100
10.10.30.0/24 dev eth0 proto kernel scope link src 10.10.30.12 metric 100
198.51.100.0/24 dev demo0 proto kernel scope link src 198.51.100.21 metric 550
```

A single default route, still through `eth0`. The `demo0` route is of `link`
scope: it only concerns its own network.

### Undoing, and troubleshooting

A single command removes the profile, the file and the interface:

```bash
sudo nmcli connection delete demo-static
nmcli con show
ip -br link
sudo ls -l /etc/NetworkManager/system-connections/
```

```text
Connection 'demo-static' (ac314bb7-9bee-493d-9a47-bec7ceef5710) successfully deleted.
NAME             UUID                                  TYPE      DEVICE
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
lo               6205a4b0-18bc-46db-8d76-6ac467bdb9cc  loopback  lo
[... ip -br link : plus de demo0 ...]
-rw-------. 1 root root 331 Jul 22 13:30 cloud-init-eth0.nmconnection
```

Check on the three levels: no more profile, no more interface, no more file.
Allow a second or two, `nmcli con show` may still display the connection right
after the command, the time for the daemon to propagate the information. The
table below sums up the failures met in this course.

| Symptom | Likely cause | Fix |
|---|---|---|
| `con show` gives the right IP, `ip addr` the old one | profile modified, never reactivated | `sudo nmcli con up <profile>` |
| `DEVICE` column at `--` | profile recorded but inactive | `sudo nmcli con up <profile>` |
| The address disappears at reboot | set with `ip addr add`, or `connection.autoconnect` at `no` | recreate a profile, or `nmcli con mod <profile> connection.autoconnect yes` |
| The profile disappears from `con show` after reboot | keyfile too permissive, refused at load time | `sudo chmod 0600 <file>` then `nmcli con load <file>` |
| `FILENAME` points at `/run/...` | in-memory connection, adopted from an interface brought up by hand | create a real profile with `nmcli con add` |
| The interface stays `unmanaged` | another manager claims the card | identify the active daemon before going further |
| Nothing makes sense | the journal always gives the exact reason | `sudo journalctl -u NetworkManager -b --no-pager \| tail -50` |

One last reflex, valid everywhere: before validating, reread the **profile**, not
the output of `ip addr`. It is the profile that will be replayed at the next
boot.

```bash
nmcli -f connection.autoconnect,ipv4.method,ipv4.addresses con show <profile>
```
