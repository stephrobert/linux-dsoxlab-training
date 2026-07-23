# Contexte — monter un partage SMB sans fuiter le mot de passe

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
https://blog.stephane-robert.info/docs/services/stockage/smb/
