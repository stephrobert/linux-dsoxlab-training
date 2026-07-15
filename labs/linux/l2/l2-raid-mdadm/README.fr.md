# Lab — Construire un RAID 1 logiciel avec mdadm

> Préparez la VM : `dsoxlab run l2-raid-mdadm`

## Rappel

[**Le RAID logiciel avec mdadm**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/)

Le RAID 1 duplique les données sur plusieurs disques : l'array survit à la perte
d'un disque. Un spare peut reconstruire automatiquement. L'array doit être
déclaré dans `mdadm.conf` (et l'initramfs) pour se réassembler au démarrage.

## Objectifs

- Créer un array **RAID 1** avec `mdadm`.
- Le formater et le monter.
- Le rendre **persistant** (`mdadm.conf`).

## Lancer et valider

```bash
dsoxlab run   l2-raid-mdadm
dsoxlab check l2-raid-mdadm
```
