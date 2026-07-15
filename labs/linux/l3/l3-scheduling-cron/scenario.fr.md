# Contexte — lancer une tâche selon un horaire

Un script de rapport (`/usr/local/bin/report.sh`) doit tourner **chaque jour à
02:30**, sans intervention. Personne ne va le lancer à la main — c'est le rôle de
**cron**.

Ta mission, sur la VM :

1. Planifie `/usr/local/bin/report.sh` pour qu'il s'exécute **chaque jour à
   02:30** (minute `30`, heure `2`).
2. Utilise un vrai mécanisme cron — une entrée système dans `/etc/cron.d/`,
   `/etc/crontab`, ou une crontab utilisateur (`crontab -e`).

L'idée : une ligne cron, c'est cinq champs de temps — `minute heure
jour-du-mois mois jour-de-semaine` — puis (pour les fichiers système) un
utilisateur, puis la commande. `30 2 * * *` signifie 02:30 tous les jours.
`crontab -l` et les fichiers de `/etc/cron.d/` montrent ce qui est planifié.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/
