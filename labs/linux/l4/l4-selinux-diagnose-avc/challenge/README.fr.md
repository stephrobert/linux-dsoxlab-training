# Challenge — l4-selinux-diagnose-avc

## Mission

`http://localhost` renvoie 403 — un AVC SELinux, pas un bug de permissions.
Diagnostique-le et restaure le contexte.

## Objectif (état attendu)

1. `/var/www/html/index.html` a le type `httpd_sys_content_t` (`ls -Z`).
2. `curl http://localhost/index.html` renvoie `200`.
3. SELinux est toujours `Enforcing`.

## Contraintes

- `setenforce 0` / permissive = **échec**. Corrige le label, pas le mode.
- Le bon type est déjà dans la policy pour `/var/www/html` — `restorecon` suffit,
  pas besoin de règle `semanage fcontext`.
- On lit `ls -Z`, le code HTTP et `getenforce`.

## Validation

```bash
dsoxlab check l4-selinux-diagnose-avc
```
