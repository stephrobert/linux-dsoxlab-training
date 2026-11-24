# Monter un partage depuis un serveur NFS

## La situation

Ce lab utilise **deux machines** : un serveur (`alma-rhcsa-2`) exporte déjà un
partage NFS `/srv/export`, et ton client (`alma-rhcsa-1`) doit le monter. C'est
la tâche quotidienne « rattacher le stockage partagé », avec son piège reboot
classique : un montage réseau tenté avant que le réseau soit prêt, et c'est le
démarrage entier qui part en vrille.

L'idée : un filesystem réseau se déclare comme les autres, mais il dépend de
quelque chose que les autres n'exigent pas, le réseau. Cette dépendance ne se
devine pas toute seule au démarrage : elle se déclare.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/services/stockage/nfs/

## Ce qui est demandé

### Mission

Un serveur NFS (`alma-rhcsa-2`) exporte `/srv/export`. Sur le **client**
(`alma-rhcsa-1`), monte cet export de façon persistante.

### Objectif (état attendu, côté client)

1. `/mnt/nfs` est **monté** (type **nfs**).
2. `/mnt/nfs/hello.txt` est **lisible** (le montage sert bien le serveur).
3. `/etc/fstab` a une entrée `nfs` pour `/mnt/nfs` avec l'option **`_netdev`**.

### Contraintes

- L'IP du serveur est dans `/root/nfs-server.env`. `nfs-utils` est installé.
- Piège reboot : sans `_netdev`, le montage réseau est tenté trop tôt au boot.
- La validation lit l'**état réel** du client (montage, contenu, fstab).

### Validation

```bash
dsoxlab check l2-nfs-mount-persist
```
