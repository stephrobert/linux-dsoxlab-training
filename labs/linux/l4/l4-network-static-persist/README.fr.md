# Lab — IPv4 statique persistante avec NetworkManager

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-network-static-persist`

## Rappel

[**NetworkManager sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/)

Sur RHEL, `NetworkManager` pilote les interfaces. `nmcli con add` crée un profil
de connexion ; `ipv4.method manual` + `ipv4.addresses` fixe une adresse statique ;
le profil atterrit dans `/etc/NetworkManager/system-connections/` et survit donc
au reboot. `ip addr add` est volatile.

Travaille sur l'interface dédiée `lab0`, jamais sur `enp5s0` (gestion).

## Objectifs

- la connexion `lab-static` a `ipv4.method` = `manual` ;
- ses `ipv4.addresses` incluent `192.0.2.50/24` ;
- le fichier de profil existe sur disque ;
- `lab0` porte `192.0.2.50` en live.

## Valider

```bash
dsoxlab check l4-network-static-persist
```
