# Contexte — un serveur démarre sans interface

Quelqu'un a laissé cette machine avec une cible de démarrage **graphique** par
défaut — inutile sur un serveur, et un gaspillage de ressources. Reviens à un
démarrage texte multi-utilisateur.

L'idée : les **cibles** (targets) systemd sont des états de démarrage ;
`multi-user.target` est l'état serveur standard (réseau + services, sans GUI),
`graphical.target` ajoute un gestionnaire d'affichage. Le système en désigne une
comme cible par défaut, et c'est cette désignation, et elle seule, qui survit au
reboot.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/
