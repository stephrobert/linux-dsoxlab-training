# Contexte — monter seulement quand c'est nécessaire

Certains filesystems ne doivent pas rester montés en permanence : un disque
rarement utilisé, un partage réseau. **autofs** les monte **à l'accès** et les
démonte après un délai d'inactivité, économisant les ressources et évitant les
montages fantômes. Ici, le disque supplémentaire porte un XFS ; câble-le pour
qu'un accès à `/autofs/data` le monte.

L'idée : autofs ne monte rien tant que le chemin n'est pas sollicité, et il
démonte de lui-même quand plus personne ne s'en sert. Encore faut-il lui décrire
ce qu'il doit monter, et sous quel chemin.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/
