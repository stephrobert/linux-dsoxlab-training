# Turn this host into a NAT gateway

## The situation

This host must forward traffic: incoming connections on **`tcp/8080`** should be
sent to a backend server at **`192.0.2.20:80`**, with the source address
masqueraded so replies come back. And it must hold across a reboot — a NAT rule
that vanishes on restart is worse than none.

The point: forwarding traffic on someone else's behalf is not the kernel's
default behaviour, it has to be allowed. Redirecting a port and masquerading the
source address are then two distinct treatments, at two different points of a
packet's journey. And an nftables rule added live dies at reboot: persistence is
configured elsewhere.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/nat-port-forwarding/

## What is asked

### Mission

Make this host a NAT gateway: forward `tcp/8080` to `192.0.2.20:80` with
masquerade, persistently.

### Goal (expected state)

1. `net.ipv4.ip_forward` = `1` (live) and declared in `/etc/sysctl.d/`.
2. nftables ruleset has `tcp dport 8080 dnat to 192.0.2.20:80` (prerouting) and
   `192.0.2.20 masquerade` (postrouting).
3. It survives reboot: `nftables.service` enabled + the rules `include`d in
   `/etc/sysconfig/nftables.conf`.

### Constraints

- `ip_forward` is the prerequisite — a NAT rule without it does nothing.
- A live `nft add` alone is lost on reboot: persist through the RHEL config.
- Validation reads sysctl, the nft ruleset and the persistence files.

### Validation

```bash
dsoxlab check l4-nat-portforward
```
