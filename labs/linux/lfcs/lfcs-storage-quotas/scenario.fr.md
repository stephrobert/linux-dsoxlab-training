# Contexte — plafonner l'espace disque avec les quotas XFS

Un système de fichiers partagé sans quota, c'est un système de fichiers qu'un
seul utilisateur peut remplir à lui tout seul. Les **quotas** plafonnent l'espace
qu'un compte peut consommer — et sur XFS ce n'est pas un service qu'on démarre :
ils s'activent **au montage**, par une option de montage. Oublie cette option
dans `/etc/fstab` et tes quotas disparaissent silencieusement au prochain reboot.

Un disque dédié de 5 Go, **`/dev/vdb`**, est attaché à la VM et encore vierge.
L'utilisateur **`devops`** existe déjà.

Ta mission, sur la VM Ubuntu :

1. **Formate** `/dev/vdb` en **XFS**.
2. **Monte**-le sur **`/srv/data`** avec les **quotas utilisateur activés**
   (`uquota`), et rends le montage **persistant** dans `/etc/fstab` — avec
   l'option de quota.
3. **Impose** un quota de blocs à `devops` : **40M en souple**, **50M en dur**.

L'idée : `xfs_quota -x -c "state -u" /srv/data` doit rapporter à la fois
`Accounting: ON` **et** `Enforcement: ON` — la comptabilité seule mesure sans
rien plafonner. Et c'est l'entrée fstab qui fait survivre le tout à un reboot.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/
