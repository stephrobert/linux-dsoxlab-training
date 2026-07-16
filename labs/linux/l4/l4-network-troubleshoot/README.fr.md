# Lab — diagnostiquer une connexion réseau tombée

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-network-troubleshoot`

## Rappel

[**Le diagnostic réseau sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/)

`nmcli con show <nom>` révèle l'état d'une connexion (`GENERAL.STATE`) et son
drapeau `connection.autoconnect`. Une connexion peut être configurée mais
**inactive** ; `nmcli con up` l'active, et `connection.autoconnect yes` la fait
revenir après un reboot. `ip addr` / `ip link` montrent l'interface active.

Travaille sur `lab1`, jamais sur `enp5s0` (gestion).

## Objectifs

- `lab-net` est `activated` ;
- `connection.autoconnect` = `yes` ;
- `lab1` porte `198.51.100.10` en live.

## Valider

```bash
dsoxlab check l4-network-troubleshoot
```
