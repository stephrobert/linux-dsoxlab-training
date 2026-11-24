# Un 403 qui n'est pas un problème de permissions

## La situation

`httpd` tourne et `/var/www/html/index.html` existe et est lisible par tous,
pourtant le site renvoie **403 Forbidden**. Les permissions Unix sont bonnes :
c'est **SELinux** qui refuse l'accès à `httpd` parce que le fichier porte le
mauvais label. Le refus est enregistré comme un **AVC** dans le journal d'audit.
Lis-le, et corrige proprement, sans `setenforce 0`.

L'idée : un refus SELinux ressemble à un bug de permissions mais n'en est pas un.
Le journal d'audit garde la trace exacte du refus, et des outils savent la
traduire en cause lisible. Désactiver SELinux n'est jamais la solution.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/durcissement/selinux/

## Ce qui est demandé

### Mission

`http://localhost` renvoie 403 — un AVC SELinux, pas un bug de permissions.
Diagnostique-le et restaure le contexte.

### Objectif (état attendu)

1. `/var/www/html/index.html` a le type `httpd_sys_content_t` (`ls -Z`).
2. `curl http://localhost/index.html` renvoie `200`.
3. SELinux est toujours `Enforcing`.

### Contraintes

- `setenforce 0` / permissive = **échec**. Corrige le label, pas le mode.
- Le bon type est déjà dans la policy pour `/var/www/html` — `restorecon` suffit,
  pas besoin de règle `semanage fcontext`.
- On lit `ls -Z`, le code HTTP et `getenforce`.

### Validation

```bash
dsoxlab check l4-selinux-diagnose-avc
```
