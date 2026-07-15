# Lab — créer un filesystem XFS

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-filesystem-create-xfs`

## Rappel

[**XFS sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/)

`mkfs.xfs <device>` crée un filesystem XFS ; `-L <label>` y appose un label
(`-f` force par-dessus une signature existante). `blkid` et `lsblk -f` montrent
le type, le label et l'UUID. Un filesystem doit être **monté** sur un répertoire
pour être utilisé.

## Objectifs

Sur la partition préparée :

- la formater en XFS avec le label `DATA` (`mkfs.xfs -L DATA <part>`) ;
- créer `/srv/xfs` ;
- l'y monter.

## Valider

```bash
dsoxlab check l2-filesystem-create-xfs
```
