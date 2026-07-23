# Contexte — transformer un programme en service géré

Un petit programme (`/usr/local/bin/labapp.sh`) doit tourner comme un vrai
**service systemd** : démarré maintenant, redémarré en cas d'échec, et relancé
automatiquement au boot. Là, il n'a aucune unit.

L'idée : un fichier unit décrit *comment* lancer quelque chose. Reste à savoir
comment faire prendre en compte cette description par systemd, puis à distinguer
« tourne maintenant » de « revient au prochain boot » : ce sont deux gestes
distincts.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/
