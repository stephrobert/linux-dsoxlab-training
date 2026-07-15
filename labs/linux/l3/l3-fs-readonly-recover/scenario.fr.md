# Contexte — un montage de données bloqué en lecture seule

Les applications qui écrivent dans `/srv/data` échouent : le filesystem est monté
en **lecture seule**, et pire, une faute de frappe dans `/etc/fstab` fait
qu'`mount -a` renvoie une erreur — à un vrai reboot, la machine tomberait en mode
urgence. Diagnostique et répare.

Ta mission, sur la VM :

1. Trouve pourquoi `/srv/data` est en lecture seule et pourquoi `mount -a` échoue
   (inspecte `/etc/fstab` — une option est mal orthographiée).
2. **Corrige l'entrée fstab** pour que ses options soient valides.
3. **Remonte** `/srv/data` en lecture-écriture (`mount -o remount,rw /srv/data`).
4. Confirme que `mount -a` ne renvoie plus d'erreur.

L'idée : une option de montage invalide dans `/etc/fstab` casse `mount -a` et peut
bloquer le démarrage ; `findmnt` montre les options actuelles, `mount -o
remount,rw` bascule un montage sans démonter, et `mount -a` est le moyen sûr de
tester fstab avant de rebooter.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/
