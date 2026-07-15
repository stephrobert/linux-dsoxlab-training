# Lab — partitionnement GPT avec parted

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-partition-gpt`

## Rappel

[**Partitions sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/)

`parted -s <disque> mklabel gpt` écrit une table GPT ; `mkpart` découpe une
partition entre deux offsets (`1MiB 513MiB` → une partition de 512 Mio). GPT lève
les limites du MBR (4 primaires, 2 Tio). Après édition, `partprobe <disque>` fait
relire la table au noyau pour que `<disque>1`, `<disque>2` apparaissent ; `lsblk`
les montre.

## Objectifs

Sur le disque supplémentaire :

- poser une table GPT ;
- partition 1 = 512 Mio ;
- partition 2 = 1 Gio ;
- `partprobe` pour que le noyau les voie.

## Valider

```bash
dsoxlab check l2-partition-gpt
```
