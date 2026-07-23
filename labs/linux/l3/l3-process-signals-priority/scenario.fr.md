# Contexte — faire s'effacer la tâche batch

Un worker d'arrière-plan (`labworker.service`) tourne à fond en priorité normale
et rend la machine poussive pour tout le monde. Donne-lui un **nice de 10** pour
que l'ordonnanceur laisse passer le travail interactif d'abord — et que ça tienne
au redémarrage.

L'idée : la priorité d'un processus se fixe au lancement, et se corrige à chaud
sur un processus déjà en cours. Mais un service géré par systemd repart de sa
définition à chaque redémarrage : une correction à chaud ne lui survit pas.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/
