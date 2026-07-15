# Challenge — l2-nfs-mount-persist

## Mission

Un serveur NFS (`alma-rhcsa-2`) exporte `/srv/export`. Sur le **client**
(`alma-rhcsa-1`), monte cet export de façon persistante.

## Objectif (état attendu, côté client)

1. `/mnt/nfs` est **monté** (type **nfs**).
2. `/mnt/nfs/hello.txt` est **lisible** (le montage sert bien le serveur).
3. `/etc/fstab` a une entrée `nfs` pour `/mnt/nfs` avec l'option **`_netdev`**.

## Contraintes

- L'IP du serveur est dans `/root/nfs-server.env`. `nfs-utils` est installé.
- Piège reboot : sans `_netdev`, le montage réseau est tenté trop tôt au boot.
- La validation lit l'**état réel** du client (montage, contenu, fstab).

## Validation

```bash
dsoxlab check l2-nfs-mount-persist
```
