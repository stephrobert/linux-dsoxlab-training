# Contexte — le pare-feu, et la règle qui s'évapore

Tout candidat RHCSA l'a fait : ouvrir le port, tester, ça marche, passer à la
suite — et perdre les points, parce que la règle n'a jamais été rendue
permanente. Elle vivait en mémoire et est morte au premier rechargement.

Ce drill est un **chrono** : 5 tâches, 20 minutes, aucun indice. L'objectif est
le même sur les deux certifications ; seul l'outil change — `firewalld` sur
RHEL, `ufw` sur Debian. Le sujet ne nomme donc ni l'un ni l'autre.

Deux choses sont mesurées au-delà des commandes :

- la **persistance** — tes règles sont vérifiées *après un rechargement*. Ce qui
  n'y survit pas ne compte pas ;
- **ne pas te verrouiller dehors** — tu travailles à travers SSH. Un pare-feu qui
  s'active sans SSH autorisé te coûte la machine, et toutes les tâches
  restantes avec.

Lis le sujet : `dsoxlab challenge drill-firewall`.
