# Contexte — lancer une tâche selon un horaire

Un script de rapport (`/usr/local/bin/report.sh`) doit tourner **chaque jour à
02:30**, sans intervention. Personne ne va le lancer à la main — c'est le rôle de
**cron**.

L'idée : une ligne cron décrit d'abord *quand*, à travers plusieurs champs de
temps, puis *quoi*. Sa forme exacte n'est pas la même selon qu'elle est posée
dans la crontab d'un utilisateur ou dans un fichier système.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/
