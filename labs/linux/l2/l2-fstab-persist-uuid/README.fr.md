# Lab — montage persistant par UUID

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-fstab-persist-uuid`

## Rappel

[**Montages persistants sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/)

`blkid` et `lsblk -f` montrent l'UUID d'un filesystem. Une ligne `/etc/fstab`
(`<quoi> <où> <type> <options> <dump> <pass>`) le monte au démarrage. Référence
le disque par `UUID=` — les noms comme `/dev/vdb` peuvent changer d'un reboot à
l'autre. `mount -a` monte tout ce que déclare fstab et valide ton entrée sans
redémarrer.

## Objectifs

Sur la VM, monte le disque ext4 supplémentaire de façon persistante :

- trouve son UUID (`blkid`) ;
- crée `/srv/data` ;
- ajoute une entrée fstab `UUID=<uuid> /srv/data ext4 defaults 0 0` ;
- lance `mount -a` — `/srv/data` doit être monté.

## Valider

```bash
dsoxlab check l2-fstab-persist-uuid
```
