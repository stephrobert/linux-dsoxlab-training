# Lab — redirection de port NAT persistante avec nftables

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-nat-portforward`

## Rappel

[**NAT & redirection de port sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/)

Le routage exige `net.ipv4.ip_forward = 1` (persiste-le dans `/etc/sysctl.d/`).
nftables fait le travail : une table `nat` avec une chaîne `prerouting`
(`dnat` = la redirection de port) et une chaîne `postrouting` (`masquerade` =
SNAT). Sur RHEL, la persistance passe par `/etc/sysconfig/nftables.conf` (qui
`include` ton fichier `.nft`) plus le service `nftables` activé.

## Objectifs

- `net.ipv4.ip_forward` = `1`, actif et persistant ;
- le ruleset nftables a `tcp dport 8080 dnat to 192.0.2.20:80` et
  `192.0.2.20 masquerade` ;
- le ruleset persiste (nftables activé + include dans la config RHEL).

## Valider

```bash
dsoxlab check l4-nat-portforward
```
