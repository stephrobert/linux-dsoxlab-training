# Context — turn this host into a NAT gateway

This host must forward traffic: incoming connections on **`tcp/8080`** should be
sent to a backend server at **`192.0.2.20:80`**, with the source address
masqueraded so replies come back. And it must hold across a reboot — a NAT rule
that vanishes on restart is worse than none.

Your mission, on the VM:

1. **Enable IP forwarding**, persistently: `net.ipv4.ip_forward = 1` in
   `/etc/sysctl.d/` (the absolute prerequisite — without routing, no NAT rule
   applies), then `sysctl --system`.
2. Create an **nftables `nat` table** `lab-nat`:
   - `prerouting` (`type nat hook prerouting priority dstnat`):
     `tcp dport 8080 dnat to 192.0.2.20:80`;
   - `postrouting` (`type nat hook postrouting priority srcnat`):
     `ip daddr 192.0.2.20 masquerade`.
3. **Persist** it: save the table to `/etc/nftables/lab-nat.nft`, `include` it in
   `/etc/sysconfig/nftables.conf`, and `systemctl enable --now nftables`.

The point: `ip_forward=1` is the prerequisite; nftables does the DNAT
(port forward) in `prerouting` and the `masquerade` (SNAT) in `postrouting`; and
on RHEL persistence goes through `/etc/sysconfig/nftables.conf` + the enabled
`nftables.service`, not a live `nft add` that dies on reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/
