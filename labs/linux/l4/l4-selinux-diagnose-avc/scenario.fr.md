# Contexte — un 403 qui n'est pas un problème de permissions

`httpd` tourne et `/var/www/html/index.html` existe et est lisible par tous,
pourtant le site renvoie **403 Forbidden**. Les permissions Unix sont bonnes :
c'est **SELinux** qui refuse l'accès à `httpd` parce que le fichier porte le
mauvais label. Le refus est enregistré comme un **AVC** dans le journal d'audit.
Lis-le, et corrige proprement, sans `setenforce 0`.

L'idée : un refus SELinux ressemble à un bug de permissions mais n'en est pas un.
Le journal d'audit garde la trace exacte du refus, et des outils savent la
traduire en cause lisible. Désactiver SELinux n'est jamais la solution.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
