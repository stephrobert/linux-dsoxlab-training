# Contexte — monter un partage depuis un serveur NFS

Ce lab utilise **deux machines** : un serveur (`alma-rhcsa-2`) exporte déjà un
partage NFS `/srv/export`, et ton client (`alma-rhcsa-1`) doit le monter. C'est
la tâche quotidienne « rattacher le stockage partagé », avec son piège reboot
classique : un montage réseau tenté avant que le réseau soit prêt, et c'est le
démarrage entier qui part en vrille.

L'idée : un filesystem réseau se déclare comme les autres, mais il dépend de
quelque chose que les autres n'exigent pas, le réseau. Cette dépendance ne se
devine pas toute seule au démarrage : elle se déclare.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/stockage/nfs/
