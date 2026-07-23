# Contexte — faire s'effacer la tâche batch

Un worker d'arrière-plan (`labworker.service`) tourne à fond en priorité normale
et rend la machine poussive pour tout le monde. Donne-lui un **nice de 10** pour
que l'ordonnanceur laisse passer le travail interactif d'abord — et que ça tienne
au redémarrage.

Ta mission, sur la VM :

1. Règle la priorité d'ordonnancement du service à **nice `10`** (plus le nice
   est haut, plus la priorité est basse) via l'unit — idéalement un drop-in
   (`systemctl edit labworker`).
2. Recharge et redémarre pour que le processus prenne réellement la nouvelle
   priorité.

L'idée : `nice` fixe la priorité de départ d'un processus, `renice` change celle
d'un processus en cours, et les signaux (`kill -TERM`, `-HUP`, `-9`) pilotent les
processus. Pour un service, la façon durable est `Nice=` dans l'unit.
`ps -o ni -p <pid>` montre la valeur live.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/
