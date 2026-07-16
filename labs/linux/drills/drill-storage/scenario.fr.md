# Contexte — le stockage, contre la montre

Le stockage, c'est là que les candidats RHCSA et LFCS perdent le plus de points,
pour une raison : la chaîne est longue — partition, PV, VG, LV, système de
fichiers, montage, fstab — et un seul maillon manquant rend tout le reste sans
valeur.

Ce drill est un **chrono** : 5 tâches, 25 minutes, aucun indice. Les mêmes
compétences servent les deux certifications : `parted`, LVM, XFS et `mkswap` sont
identiques sur RHEL et Debian.

Deux pièges qui coûtent cher :

- un montage qui marche **maintenant** mais absent de `/etc/fstab`, ou écrit par
  chemin de device au lieu de l'**UUID** — les noms de devices bougent ;
- un **volume logique étendu dont le système de fichiers n'a pas suivi** :
  `lvextend` seul ne donne rien, l'espace reste inutilisable.

Lis le sujet : `dsoxlab challenge drill-storage`.
