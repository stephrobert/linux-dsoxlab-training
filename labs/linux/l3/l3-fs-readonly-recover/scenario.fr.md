# Contexte — un montage de données bloqué en lecture seule

Les applications qui écrivent dans `/srv/data` échouent : le filesystem est monté
en **lecture seule**, et pire, une faute de frappe s'est glissée dans
`/etc/fstab` — à un vrai reboot, la machine tomberait en mode urgence.
Diagnostique et répare.

L'idée : une option de montage invalide dans `/etc/fstab` ne se voit pas tant que
personne ne relit le fichier ; au démarrage, elle bloque tout. Il faut donc les
deux : rendre `/srv/data` de nouveau inscriptible, et s'assurer que la
déclaration est saine avant de tenter un redémarrage.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/
