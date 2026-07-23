# Contexte — distribuer juste ce qu'il faut de sudo

L'équipe d'exploitation doit redémarrer des services, mais elle ne doit **pas**
obtenir root complet. C'est de la délégation au moindre privilège : autoriser le
groupe `operators` à lancer `systemctl` — et seulement ça — sans mot de passe.

L'idée : la politique sudo se découpe en fragments indépendants plutôt que de
s'entasser dans un seul fichier, et c'est la liste des commandes autorisées qui
fait tout l'intérêt de la délégation. Une erreur de syntaxe y est
catastrophique : elle se valide avant de s'appliquer, jamais après.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/
