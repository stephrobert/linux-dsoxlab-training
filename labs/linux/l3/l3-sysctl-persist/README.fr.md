# Lab — durcissement noyau persistant avec sysctl

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-sysctl-persist`

## Rappel

[**Durcissement sysctl sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/)

`sysctl -w clé=valeur` change un paramètre noyau maintenant (perdu au reboot). Un
fichier dans `/etc/sysctl.d/*.conf` (`clé = valeur` par ligne) le rend
persistant ; `sysctl --system` recharge tous les fichiers de config.
`sysctl -n <clé>` lit la valeur active.

## Objectifs

Persistant dans `/etc/sysctl.d/` et actif :

- `net.ipv4.ip_forward = 0` ;
- `net.ipv4.conf.all.accept_redirects = 0`.

## Valider

```bash
dsoxlab check l3-sysctl-persist
```
