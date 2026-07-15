# Lab — profil de performance tuned

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-tuned-profile`

## Rappel

[**tuned sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/)

`tuned` applique un lot nommé de réglages noyau/sysfs. `tuned-adm list` affiche
les profils disponibles, `tuned-adm active` le courant, `tuned-adm profile <nom>`
bascule. Le choix actif est sauvegardé dans `/etc/tuned/active_profile`, donc
persistant. Le service `tuned` doit tourner.

## Objectifs

- profil actif = `throughput-performance` ;
- persisté dans `/etc/tuned/active_profile`.

## Valider

```bash
dsoxlab check l3-tuned-profile
```
