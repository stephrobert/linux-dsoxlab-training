# Challenge — l4-nat-portforward

## Mission

Make this host a NAT gateway: forward `tcp/8080` to `192.0.2.20:80` with
masquerade, persistently.

## Goal (expected state)

1. `net.ipv4.ip_forward` = `1` (live) and declared in `/etc/sysctl.d/`.
2. nftables ruleset has `tcp dport 8080 dnat to 192.0.2.20:80` (prerouting) and
   `192.0.2.20 masquerade` (postrouting).
3. It survives reboot: `nftables.service` enabled + the rules `include`d in
   `/etc/sysconfig/nftables.conf`.

## Constraints

- `ip_forward` is the prerequisite — a NAT rule without it does nothing.
- A live `nft add` alone is lost on reboot: persist through the RHEL config.
- Validation reads sysctl, the nft ruleset and the persistence files.

## Validation

```bash
dsoxlab check l4-nat-portforward
```
