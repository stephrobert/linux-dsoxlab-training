# Contexte — une mine dans la config sshd

Quelqu'un a déposé un bout de config avec une faute : la configuration de sshd ne
passe plus le contrôle de syntaxe. Le sshd **en cours** fonctionne encore, car il
ne relit sa config qu'au reload : tu peux donc toujours te connecter. Mais le
prochain `systemctl reload sshd` ou le prochain reboot rendrait le serveur
injoignable. Désamorce avant que ça arrive.

L'idée : une config sshd cassée est la façon dont les admins se verrouillent
dehors. Le démon sait vérifier sa configuration **hors ligne**, avant tout
rechargement, et sait aussi afficher les réglages qu'il appliquerait réellement.
C'est ce réflexe qui manque ici.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/
