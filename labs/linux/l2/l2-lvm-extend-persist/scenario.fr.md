# Contexte — /data manque d'espace

Sur **alma-rhcsa-1.lab**, une application écrit dans `/data`, un volume XFS de
1 GiB porté par le volume logique `vgdata/lvdata`. Le groupe de volumes dispose
encore d'espace libre sur son volume physique. Tu dois agrandir `/data` **sans
interruption** et t'assurer que ça tient après un reboot.

Le piège : le volume logique et le filesystem posé dessus sont deux couches
distinctes. Agrandir l'une ne suffit pas, et tant que l'autre n'a pas suivi,
l'espace ajouté reste invisible pour l'application.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/
