# Contexte — apprendre un nouveau dépôt à dnf

Les logiciels viennent de quelque part. Quand un paquet n'est pas dans les dépôts
par défaut, tu pointes `dnf` vers un autre en déposant un fichier `.repo` sous
`/etc/yum.repos.d/`. Fais-le bien : un id clair, une vraie `baseurl`, activé, et
**vérifié GPG** pour que les paquets soient authentifiés.

Ta mission, sur la VM — crée `/etc/yum.repos.d/labrepo.repo` de sorte que :

1. il déclare un dépôt d'id **`[labrepo]`** ;
2. il ait une **`baseurl`** valide (ex. le miroir AppStream AlmaLinux 10) ;
3. il soit **`enabled=1`** ;
4. il soit **`gpgcheck=1`** (avec un `gpgkey`), pour vérifier les signatures.

Confirme avec `dnf repolist` que dnf connaît maintenant le dépôt.

L'idée : un fichier `.repo` est de l'INI — une `[section]` par dépôt.
`gpgcheck=1` est le défaut de sécurité à ne jamais retirer ; `dnf repolist` (et
`--all`) liste ce que dnf a configuré.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/
