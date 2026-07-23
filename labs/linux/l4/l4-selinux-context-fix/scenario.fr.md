# Contexte — bon contenu, mauvaise étiquette

Du contenu web a été placé dans un répertoire personnalisé `/srv/labweb`, mais
sous SELinux enforcing un serveur web confiné ne peut pas le lire : les fichiers
portent le mauvais type, hérité de `/srv`. Ré-étiquette, et fais en sorte que la
correction **tienne** à un relabel complet ou à un reboot, pas seulement le temps
d'une retouche ponctuelle.

L'idée : une étiquette posée à la main sur un fichier est balayée par le premier
relabel du système. La façon durable, celle qu'attend le RHCSA, consiste à
**déclarer la règle** qui dit quel type ce chemin doit porter, puis à laisser la
policy l'appliquer.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
