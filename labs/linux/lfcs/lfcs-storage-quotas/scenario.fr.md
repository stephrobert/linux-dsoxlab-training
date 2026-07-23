# Contexte — plafonner l'espace disque avec les quotas XFS

Un système de fichiers partagé sans quota, c'est un système de fichiers qu'un
seul utilisateur peut remplir à lui tout seul. Les **quotas** plafonnent l'espace
qu'un compte peut consommer, et sur XFS ce n'est pas un service qu'on démarre :
ils s'activent **au montage**, par une option de montage. Oublie cette option
dans `/etc/fstab` et tes quotas disparaissent silencieusement au prochain reboot.

Un disque dédié de 5 Go, **`/dev/vdb`**, est attaché à la VM et encore vierge.
L'utilisateur **`devops`** existe déjà.

L'idée : compter et plafonner sont deux choses différentes. Une comptabilité de
quotas active mais sans application ne protège de rien : l'état des quotas du
système de fichiers doit montrer les deux. Et c'est l'entrée dans `/etc/fstab`
qui fait survivre l'ensemble à un reboot.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/
