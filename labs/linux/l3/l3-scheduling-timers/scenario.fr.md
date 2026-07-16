# Contexte — du travail récurrent, façon systemd

Une tâche de maintenance doit tourner régulièrement. Sur un hôte systemd,
l'approche moderne est une **unité timer** : un `.timer` qui déclenche un
`.service`, avec journalisation, dépendances et gestion par `systemctl` — et ça
revient après un reboot.

Ta mission, sur la VM :

1. Crée **`/etc/systemd/system/labbackup.service`** — un service `oneshot` dont
   l'`ExecStart` fait `touch /run/labbackup.stamp`.
2. Crée **`/etc/systemd/system/labbackup.timer`** — un `[Timer]` avec un planning
   `OnCalendar=` (par ex. `*:0/10` toutes les dix minutes), et une section
   `[Install]` `WantedBy=timers.target`.
3. `systemctl daemon-reload`, puis **active et démarre** :
   `systemctl enable --now labbackup.timer`.

L'idée : un timer pilote un service selon un planning (`OnCalendar`), `systemctl
list-timers` montre la prochaine exécution, et être **enabled** est ce qui le fait
survivre au reboot — le remplaçant de cron dans le monde systemd.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/
