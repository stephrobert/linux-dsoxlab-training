# Contexte — un 403 qui n'est pas un problème de permissions

`httpd` tourne et `/var/www/html/index.html` existe et est lisible par tous,
pourtant le site renvoie **403 Forbidden**. Les permissions Unix sont bonnes —
c'est **SELinux** qui refuse l'accès à `httpd` parce que le fichier porte le
mauvais label. Le refus est enregistré comme un **AVC** dans le journal d'audit.
Lis-le, et corrige proprement — pas de `setenforce 0`.

Ta mission, sur la VM :

1. **Diagnostique** le refus : `sudo ausearch -m AVC -ts recent` (ou `sealert`)
   pointe `/var/www/html/index.html` et le mauvais type.
2. **Restaure** le bon contexte avec `restorecon` (le bon type,
   `httpd_sys_content_t`, est déjà défini dans la policy pour `/var/www/html` —
   pas besoin de règle `semanage`).
3. Confirme que le site renvoie maintenant **200**.

L'idée : un refus SELinux ressemble à un bug de permissions mais n'en est pas un.
`ausearch`/`sealert` transforment l'AVC en cause lisible ; `restorecon` réapplique
le label attendu par la policy pour un chemin standard. Désactiver SELinux n'est
jamais la solution.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
