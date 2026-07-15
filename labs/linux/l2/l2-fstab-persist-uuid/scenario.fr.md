# Contexte — rendre un montage résistant au reboot

La machine a un disque supplémentaire, déjà formaté en ext4, mais il n'est ni
monté ni déclaré. Ta mission : le monter sur `/srv/data` et rendre ce montage
**permanent** — le genre de tâche qui fait échouer les candidats RHCSA quand ils
montent à la main et oublient `/etc/fstab`, ou référencent le disque par un nom
de périphérique qui peut changer au prochain démarrage.

Ta mission, sur la VM :

1. Trouver l'**UUID** du disque (`blkid` / `lsblk -f`).
2. Créer le point de montage `/srv/data`.
3. Ajouter une entrée `/etc/fstab` qui le monte sur `/srv/data`, **par UUID** —
   jamais par `/dev/vdX`.
4. Prouver que l'entrée est valide avec `mount -a`, pour qu'elle se remonte à
   chaque démarrage.

L'idée : les noms de périphériques (`/dev/vdb`) ne sont pas stables d'un reboot à
l'autre ; un UUID l'est. Une entrée fstab par UUID est ce qui rend le montage
réellement persistant.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/
