# Contexte — une auth par clé qui refuse en silence

Un utilisateur de service `deploy` doit se connecter en SSH avec sa clé, et la
clé publique est déjà dans `~deploy/.ssh/authorized_keys`. Pourtant `sshd` la
refuse et retombe sur rien. La clé est bonne ; ce sont les **permissions** qui ne
le sont pas : `sshd` ignore un `authorized_keys` accessible en écriture au groupe
ou aux autres, ou non détenu par l'utilisateur.

L'idée : l'auth SSH par clé, c'est autant une affaire de **propriétaire et de
permissions** que de clé. `sshd` refuse silencieusement un `authorized_keys` dont
l'environnement est trop ouvert ou mal détenu, sans rien annoncer côté client :
c'est le piège qui fait perdre des heures.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/
