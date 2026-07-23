# Contexte — AppArmor, le contrôle d'accès obligatoire de Debian

Là où RHEL utilise SELinux, Debian et Ubuntu utilisent **AppArmor** : des profils
par programme qui confinent ce qu'un binaire peut faire. Un profil tourne en
**enforce** (violations bloquées) ou en **complain** (violations seulement
journalisées, le mode apprentissage utilisé pour régler un profil).

L'idée : AppArmor se pilote profil par profil. On peut mettre un profil en
apprentissage, le remettre en enforce ou le décharger complètement sans toucher
aux autres. C'est sa réponse à l'enforcing et au permissive de SELinux, mais à la
maille du programme, pas de la machine.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/
