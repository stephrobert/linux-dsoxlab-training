# Contexte — systemd, contre la montre

`systemd`, c'est là qu'un administrateur Linux passe ses journées : un service
qui doit revenir, une tâche qui doit tourner au bon moment, une unité qui ne
doit plus jamais démarrer. À l'examen, rien de tout ça n'est la question — c'est
l'**outillage** avec lequel tu réponds.

Ce drill est un **chrono** : 5 tâches, 25 minutes, aucun indice. Les mêmes
compétences servent RHCSA et LFCS : systemd est systemd, sur RHEL comme sur
Debian.

Trois pièges que tu retrouveras :

- **`enabled` et `running` sont deux choses différentes** : un service peut
  tourner aujourd'hui et avoir disparu après un reboot ;
- **`disable` n'empêche pas de démarrer** — seul `mask` le fait ;
- un **timer** a besoin de son `.service` : les deux vont ensemble.

Lis le sujet : `dsoxlab challenge drill-systemd`.
