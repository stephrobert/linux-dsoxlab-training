# Contexte — Ajouter du stockage redondant avec le RAID logiciel

Sur **alma-rhcsa-1.lab**, un service stocke des données qui doivent survivre à
la panne d'un disque. Sans contrôleur RAID matériel, vous utilisez le **RAID
logiciel** Linux avec `mdadm`.

Deux disques de secours sont attachés à la machine ; leurs noms de périphériques
sont notés dans `/root/raid-disks.env`, et ce sont les seuls que vous avez le
droit de toucher. Il faut en tirer un miroir qui tienne le choc, et qui se
retrouve intact après un redémarrage.

Méthode dans le guide associé :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/
