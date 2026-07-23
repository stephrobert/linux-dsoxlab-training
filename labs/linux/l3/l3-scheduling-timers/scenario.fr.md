# Contexte — du travail récurrent, façon systemd

Une tâche de maintenance doit tourner régulièrement. Sur un hôte systemd,
l'approche moderne est une **unité timer** : un `.timer` qui déclenche un
`.service`, avec journalisation, dépendances et gestion par `systemctl` — et ça
revient après un reboot.

L'idée : le travail à faire et le moment où il se déclenche sont décrits dans
deux unités séparées, la seconde portant le planning. Et comme toute unité
systemd, un timer ne revient après un redémarrage que s'il a été activé pour
cela.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/
