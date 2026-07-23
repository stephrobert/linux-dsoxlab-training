# Contexte — un accès qu'ugo ne sait pas exprimer

`root` possède `/srv/projet` et `report.txt`. Tu dois donner à **un utilisateur
précis** un accès en écriture au fichier et à **un groupe** un accès en lecture
au répertoire — sans changer le propriétaire ni les bits `ugo`, et sans les
rendre lisibles par tout le monde. C'est exactement le rôle des **ACL POSIX**.

L'idée : une ACL ajoute des entrées utilisateur ou groupe nommés par-dessus les
droits `ugo`, sans toucher à ces derniers. Et ce dont héritent les fichiers créés
plus tard ne se règle pas au même endroit que l'accès accordé aujourd'hui.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/
