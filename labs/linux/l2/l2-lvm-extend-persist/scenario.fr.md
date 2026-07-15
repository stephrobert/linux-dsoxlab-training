# Contexte — /data manque d'espace

Sur **alma-rhcsa-1.lab**, une application écrit dans `/data`, un volume XFS de
1 GiB porté par le volume logique `vgdata/lvdata`. Le groupe de volumes dispose
encore d'espace libre sur son volume physique. Tu dois agrandir `/data` **sans
interruption** et t'assurer que ça tient après un reboot.

Ta mission :

1. Étendre `vgdata/lvdata` à au moins **3 GiB**.
2. Agrandir le filesystem **XFS** pour que `/data` affiche vraiment la nouvelle
   taille.
3. Vérifier que le montage est persistant (déclaré dans `/etc/fstab` par UUID).

Le piège : étendre le volume logique ne suffit pas. Si tu oublies d'agrandir le
filesystem, `df -h /data` affiche toujours 1 GiB et l'espace ajouté est perdu.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/
