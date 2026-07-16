# Lab — diagnostiquer un refus AVC SELinux

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-selinux-diagnose-avc`

## Rappel

[**SELinux sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Quand un service confiné est refusé, SELinux logge un **AVC** dans le journal
d'audit. `ausearch -m AVC -ts recent` et `sealert` le transforment en cause
lisible. Pour un fichier mal étiqueté dans un chemin standard, `restorecon`
réapplique le type attendu par la policy (`httpd_sys_content_t` pour
`/var/www/html`). `ls -Z` montre le type. Jamais `setenforce 0`.

## Objectifs

- `/var/www/html/index.html` a le type `httpd_sys_content_t` ;
- `http://localhost/index.html` renvoie `200` ;
- SELinux reste `Enforcing`.

## Valider

```bash
dsoxlab check l4-selinux-diagnose-avc
```
