# Contexte — le même métier, deux outils

RHCSA et LFCS te demandent la même chose : installer, geler, interroger,
supprimer. Seul l'outil change — `dnf` sur RHEL, `apt` sur Debian. C'est
précisément pour ça que ce drill existe **une seule fois**, et que son sujet ne
nomme jamais la commande : un administrateur connaît l'objectif, puis prend
l'outil que sa distribution lui donne.

Ce drill est un **chrono** : 5 tâches, 20 minutes, aucun indice.

Ce qui est mesuré :

- **installer** et **supprimer** — la partie facile ;
- **geler** un paquet, pour qu'aucune mise à jour ne le bouge. C'est ce qu'on
  fait à une version dont une application dépend ;
- les deux **interrogations** qui te sauvent à l'examen : *quel paquet fournit
  ce fichier ?* et *qu'a installé ce paquet ?*

Lis le sujet : `dsoxlab challenge drill-packages`.
