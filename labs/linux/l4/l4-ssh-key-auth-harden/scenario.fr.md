# Contexte — une auth par clé qui refuse en silence

Un utilisateur de service `deploy` doit se connecter en SSH avec sa clé — la clé
publique est déjà dans `~deploy/.ssh/authorized_keys`. Pourtant `sshd` la refuse
et retombe sur rien. La clé est bonne ; ce sont les **permissions** qui ne le
sont pas : `sshd` ignore un `authorized_keys` accessible en écriture au groupe/aux
autres ou non détenu par l'utilisateur.

Ta mission, sur la VM :

1. Fais de `~deploy/.ssh` un répertoire détenu par `deploy:deploy`, mode **`0700`**.
2. Fais de `~deploy/.ssh/authorized_keys` un fichier détenu par `deploy:deploy`,
   mode **`0600`**.
3. Garde la clé publique existante en place.

L'idée : l'auth SSH par clé, c'est autant une affaire de **propriétaire et de
permissions** que de clé. `sshd` refuse silencieusement `authorized_keys` si
`.ssh` est trop ouvert ou pas détenu par l'utilisateur — le piège qui fait perdre
des heures. `stat -c '%a %U:%G'` montre les deux.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/
