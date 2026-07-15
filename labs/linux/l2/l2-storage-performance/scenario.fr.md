# Contexte — arrêter de gaspiller des I/O sur les dates d'accès

`/srv/data` sert une charge très sollicitée en lecture. Par défaut, Linux met à
jour la **date d'accès** (atime) de chaque fichier à la lecture, ce qui
transforme les lectures en écritures et dégrade les performances. Le correctif
standard est l'option de montage **`noatime`**. Ta mission : l'appliquer —
maintenant et durablement.

Ta mission, sur la VM :

1. Ajouter **`noatime`** aux options de montage de `/srv/data` dans `/etc/fstab`.
2. L'appliquer **sans reboot** (`mount -o remount /srv/data`).
3. Confirmer qu'il est actif (`findmnt /srv/data` montre `noatime`).

L'idée : les options de montage règlent le comportement d'un filesystem ;
`noatime` supprime les mises à jour d'atime. Éditer `/etc/fstab` le rend
persistant au reboot ; `mount -o remount` le rend actif immédiatement sans
démonter.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/
