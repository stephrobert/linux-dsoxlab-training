# Lab — montage SMB/CIFS persistant

> Préparer : `dsoxlab provision` puis `dsoxlab run lfcs-mount-cifs`

## Rappel

[**SMB sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/stockage/smb/)

Un montage CIFS demande le paquet `cifs-utils` et un partage authentifié :
`mount -t cifs //<serveur>/<partage> <point-de-montage> -o credentials=<fichier>`.

Deux choses le rendent digne de la production :

- **`_netdev`** dans `/etc/fstab` — le montage attend le réseau au boot ;
- un **fichier credentials** (lignes `username=` / `password=`) en `0600`, parce
  que `/etc/fstab` est lisible par tous et ne doit jamais contenir de mot de
  passe.

L'adresse du serveur et les identifiants sont dans `/root/smb-server.env`.

## Objectifs

- `//<serveur>/labshare` monté sur `/mnt/labshare`, type `cifs` ;
- le fichier servi lisible à travers le montage ;
- entrée `/etc/fstab` persistante avec `_netdev` ;
- mot de passe absent de `/etc/fstab`, isolé dans un fichier credentials `0600`.

## Valider

```bash
dsoxlab check lfcs-mount-cifs
```
