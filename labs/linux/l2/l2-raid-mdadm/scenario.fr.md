# Contexte — Ajouter du stockage redondant avec le RAID logiciel

Sur **alma-rhcsa-1.lab**, un service stocke des donnees qui doivent survivre a
la panne d'un disque. Sans controleur RAID materiel, vous utilisez le **RAID
logiciel** Linux avec `mdadm`.

Deux disques de secours sont attaches. Votre mission :

1. Les assembler en un miroir **RAID 1**.
2. Y poser un systeme de fichiers et le monter.
3. Faire en sorte que l'array se reassemble automatiquement apres un reboot.

Methode dans le guide associe :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/
