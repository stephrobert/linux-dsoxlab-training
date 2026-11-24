# Ajouter du stockage redondant avec le RAID logiciel

## La situation

Sur **alma-rhcsa-1.lab**, un service stocke des données qui doivent survivre à
la panne d'un disque. Sans contrôleur RAID matériel, vous utilisez le **RAID
logiciel** Linux avec `mdadm`.

Deux disques de secours sont attachés à la machine ; leurs noms de périphériques
sont notés dans `/root/raid-disks.env`, et ce sont les seuls que vous avez le
droit de toucher. Il faut en tirer un miroir qui tienne le choc, et qui se
retrouve intact après un redémarrage.

Méthode dans le guide associé :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/

## L2 : RAID 1 logiciel avec mdadm

### Mission

Deux disques sont disponibles sur **alma-rhcsa-1.lab** (leurs noms de
périphériques sont dans `/root/raid-disks.env`). Construis un **RAID 1
redondant** qui survit à la perte d'un disque.

1. Crée une grappe **RAID 1** `/dev/md0` à partir des deux disques.
2. Formate-la (`mkfs.xfs`) et **monte**-la sur `/mnt/raid`.
3. Rends-la **persistante** en la déclarant dans `/etc/mdadm.conf`.

### Contraintes

- La grappe doit être de niveau **raid1** avec **2 disques actifs**.
- Elle doit être montée sur `/mnt/raid`.
- `/etc/mdadm.conf` doit contenir sa ligne `ARRAY`.

### Approche utile

Les gestes se déduisent du guide compagnon, dont le lien figure dans le
`## Rappel` du cours. Si tu bloques, `dsoxlab hint` les donne, au prix
annoncé.

### Validation

```bash
dsoxlab check l2-raid-mdadm
```
