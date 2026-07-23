# Contexte — le RHCSA EX200 en conditions d'examen

On te confie **deux machines de la famille RHEL fraîchement provisionnées** et
**180 minutes**. Ce capstone reproduit le vrai EX200 : des tâches pratiques dont
le résultat doit **survivre à un reboot**, notées sur l'état du système et non
sur les commandes que tu as tapées.

- **`alma-rhcsa-1.lab`** (serveur) porte 16 tâches : partitionnement et LVM, XFS,
  swap, un export NFS, utilisateurs, groupes et ACL, un réseau statique, unités
  et timers systemd, chrony, SELinux (contexte, booléen, port), installation de
  logiciels.
- **`alma-rhcsa-2.lab`** (client) porte 4 tâches dépendantes : monter le partage
  NFS, un accès SSH par clé uniquement vers le serveur, et la récupération d'un
  mot de passe root inconnu.

Le score de réussite est de **70/100**. Aucun indice. `man`, `--help` et
`/usr/share/doc/` sont tes seuls compagnons, exactement comme le jour de
l'examen.
