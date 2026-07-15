# Contexte — monter un partage depuis un serveur NFS

Ce lab utilise **deux machines** : un serveur (`alma-rhcsa-2`) exporte déjà un
partage NFS `/srv/export`, et ton client (`alma-rhcsa-1`) doit le monter. C'est
la tâche quotidienne « rattacher le stockage partagé » — et le piège reboot
classique, c'est d'oublier `_netdev`, si bien que le montage est tenté avant que
le réseau soit prêt.

Ta mission, sur la VM **cliente** :

1. Trouve l'adresse du serveur (elle est notée dans `/root/nfs-server.env`).
2. Monte son `/srv/export` sur `/mnt/nfs`.
3. Rends-le **persistant** dans `/etc/fstab`, type `nfs`, avec l'option
   **`_netdev`** pour qu'il attende le réseau au démarrage.
4. Valide avec `mount -a` — `/mnt/nfs/hello.txt` doit devenir lisible.

L'idée : un filesystem réseau se monte comme un autre mais exige `_netdev` (et
`nfs-utils`). `showmount -e <serveur>` liste les exports d'un serveur.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/stockage/nfs/
