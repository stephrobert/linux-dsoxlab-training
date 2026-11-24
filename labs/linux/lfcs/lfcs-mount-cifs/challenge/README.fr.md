# Monter un partage SMB sans fuiter le mot de passe

## La situation

SMB/CIFS, c'est la façon dont Linux parle aux serveurs de fichiers Windows, et à
n'importe quel serveur Samba. Monter un partage est facile ; le monter de façon
**persistante et sûre**, c'est là qu'on dérape. Deux pièges t'attendent :

- au démarrage, un système de fichiers réseau n'est pas monté au même moment
  qu'un disque local, et l'ignorer suffit à faire échouer le montage au boot ;
- **`/etc/fstab` est lisible par tous** (`0644`). Mets-y le mot de passe du
  compte SMB et chaque utilisateur de la machine peut le lire.

Un second hôte sert le partage **`//<serveur>/labshare`**. Son adresse et ses
identifiants sont dans **`/root/smb-server.env`** sur ton client.

L'idée : un montage qui marche aujourd'hui mais casse au reboot n'est pas fini,
et un montage qui marche mais fuite un mot de passe est pire que pas de montage
du tout.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/services/stockage/smb/

## Ce qui est demandé

### Mission

Monte le partage SMB servi par le second hôte, de façon persistante, sans fuiter
le mot de passe.

### Objectif (état attendu)

1. `//<serveur>/labshare` est monté sur `/mnt/labshare`, type `cifs`.
2. Le fichier servi `README.txt` est lisible à travers le montage.
3. `/etc/fstab` le rend persistant, avec `_netdev`.
4. Le mot de passe n'est **pas** dans `/etc/fstab` ; il vit dans un fichier
   credentials en `0600` référencé par `credentials=`.

### Contraintes

- Adresse du serveur et identifiants : `/root/smb-server.env`.
- On lit `findmnt`, le fichier servi, `/etc/fstab` et le mode du fichier
  credentials.

### Validation

```bash
dsoxlab check lfcs-mount-cifs
```
