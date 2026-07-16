# Lab — persistent NAT port forwarding with nftables

> Prepare: `dsoxlab provision` then `dsoxlab run l4-nat-portforward`

## Recap

[**NAT & port forwarding on the companion guide**](https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/)

Forwarding needs `net.ipv4.ip_forward = 1` (persist it in `/etc/sysctl.d/`).
nftables does the work: a `nat` table with a `prerouting` chain
(`dnat` = the port forward) and a `postrouting` chain (`masquerade` = SNAT). On
RHEL, persistence is `/etc/sysconfig/nftables.conf` (which `include`s your `.nft`
file) plus the enabled `nftables.service`.

## Objectives

- `net.ipv4.ip_forward` = `1`, live and persistent;
- nftables ruleset has `tcp dport 8080 dnat to 192.0.2.20:80` and
  `192.0.2.20 masquerade`;
- the ruleset persists (nftables enabled + include in the RHEL config).

## Validate

```bash
dsoxlab check l4-nat-portforward
```
