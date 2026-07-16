# Challenge — lfcs-mount-cifs

## Mission

Monte le partage SMB servi par le second hôte, de façon persistante, sans fuiter
le mot de passe.

## Objectif (état attendu)

1. `//<serveur>/labshare` est monté sur `/mnt/labshare`, type `cifs`.
2. Le fichier servi `README.txt` est lisible à travers le montage.
3. `/etc/fstab` le rend persistant, avec `_netdev`.
4. Le mot de passe n'est **pas** dans `/etc/fstab` ; il vit dans un fichier
   credentials en `0600` référencé par `credentials=`.

## Contraintes

- Adresse du serveur et identifiants : `/root/smb-server.env`.
- On lit `findmnt`, le fichier servi, `/etc/fstab` et le mode du fichier
  credentials.

## Validation

```bash
dsoxlab check lfcs-mount-cifs
```
