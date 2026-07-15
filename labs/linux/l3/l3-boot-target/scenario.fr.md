# Contexte — un serveur démarre sans interface

Quelqu'un a laissé cette machine avec une cible de démarrage **graphique** par
défaut — inutile sur un serveur, et un gaspillage de ressources. Reviens à un
démarrage texte multi-utilisateur.

Ta mission, sur la VM :

1. Vérifie le défaut actuel (`systemctl get-default`).
2. Règle le défaut sur **`multi-user.target`** (sans couche graphique).

L'idée : les **cibles** (targets) systemd sont des états de démarrage ;
`multi-user.target` est l'état serveur standard (réseau + services, sans GUI),
`graphical.target` ajoute un gestionnaire d'affichage. `systemctl set-default`
change le lien symbolique `/etc/systemd/system/default.target`, donc ça survit au
reboot.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/
