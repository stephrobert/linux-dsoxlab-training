# Lab — montage NFS persistant

> Prépare (provisionne les DEUX hôtes) : `dsoxlab provision` puis
> `dsoxlab run l2-nfs-mount-persist`

## Rappel

[**NFS sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/stockage/nfs/)

Un serveur exporte un répertoire via `/etc/exports` ; un client le monte avec
`mount -t nfs <serveur>:/chemin /mnt`. Rends-le persistant dans `/etc/fstab` en
type `nfs` avec l'option **`_netdev`** (le boot attend alors le réseau).
`nfs-utils` fournit le client ; `showmount -e <serveur>` liste les exports.

## Objectifs

Sur le **client** (`alma-rhcsa-1`) :

- monte le `/srv/export` du serveur sur `/mnt/nfs` ;
- persiste-le dans fstab en `nfs` avec `_netdev` ;
- `mount -a`, et `/mnt/nfs/hello.txt` doit être lisible.

L'adresse du serveur est dans `/root/nfs-server.env`.

## Valider

```bash
dsoxlab check l2-nfs-mount-persist
```
