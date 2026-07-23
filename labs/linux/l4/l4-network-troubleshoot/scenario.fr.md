# Contexte — l'interface est configurée mais morte

Une connexion nommée `lab-net` existe sur l'interface `lab1` avec une adresse
statique correcte, pourtant l'interface ne porte aucune IP et elle ne reviendra
pas après un reboot. Quelque chose cloche dans son état : trouve-le et ranime le
lien.

Tu travailles sur `lab1`. **Ne touche jamais à l'interface de gestion**, celle
qui porte ta route par défaut : c'est ton lien vers la machine.

L'idée : une connexion peut être entièrement configurée et pourtant ne rien
porter, et une connexion qui remonte aujourd'hui ne remontera pas forcément au
prochain boot. Ce sont deux états distincts, tous deux lisibles dans ce que
rapporte NetworkManager : à lire, pas à deviner.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/
