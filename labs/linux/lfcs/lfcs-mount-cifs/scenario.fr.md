# Contexte — monter un partage SMB sans fuiter le mot de passe

SMB/CIFS, c'est la façon dont Linux parle aux serveurs de fichiers Windows — et
à n'importe quel serveur Samba. Monter un partage est facile ; le monter de façon
**persistante et sûre**, c'est là qu'on dérape. Deux pièges t'attendent :

- un système de fichiers réseau monté sans **`_netdev`** est tenté avant que le
  réseau soit là au boot ;
- **`/etc/fstab` est lisible par tous** (`0644`). Mets-y `password=…` et chaque
  utilisateur de la machine peut lire le mot de passe du compte SMB.

Un second hôte sert le partage **`//<serveur>/labshare`**. Son adresse et ses
identifiants sont dans **`/root/smb-server.env`** sur ton client.

Ta mission, sur le client Ubuntu :

1. **Monte** `//<serveur>/labshare` sur **`/mnt/labshare`**, type `cifs`.
2. Rends-le **persistant** dans `/etc/fstab` avec l'option **`_netdev`**.
3. Garde le mot de passe **hors de `/etc/fstab`** : mets-le dans un **fichier
   credentials** lisible par root seul (`0600`) et référence-le avec
   `credentials=<chemin>`.
4. Prouve que l'entrée est valide avec `sudo mount -a`.

L'idée : un montage qui marche aujourd'hui mais casse au reboot n'est pas fini,
et un montage qui marche mais fuite un mot de passe est pire que pas de montage
du tout.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/stockage/smb/
