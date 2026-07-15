# Contexte — un accès qu'ugo ne sait pas exprimer

`root` possède `/srv/projet` et `report.txt`. Tu dois donner à **un utilisateur
précis** un accès en écriture au fichier et à **un groupe** un accès en lecture
au répertoire — sans changer le propriétaire ni les bits `ugo`, et sans les
rendre lisibles par tout le monde. C'est exactement le rôle des **ACL POSIX**.

Ta mission, sur la VM :

1. Donne à l'utilisateur **`carol`** `rw` sur `/srv/projet/report.txt`
   (`setfacl -m u:...`).
2. Donne au groupe **`auditors`** `rx` sur `/srv/projet` (`setfacl -m g:...`).
3. Pose une **ACL par défaut** sur `/srv/projet` pour que les **nouveaux**
   fichiers héritent de `r` pour `auditors` (`setfacl -m d:g:...`).

L'idée : une ACL ajoute des entrées utilisateur/groupe nommés par-dessus `ugo` ;
`getfacl` les affiche ; une entrée `default:` est un gabarit dont les nouveaux
fichiers héritent. Un `+` dans `ls -l` signale un fichier porteur d'ACL.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/
