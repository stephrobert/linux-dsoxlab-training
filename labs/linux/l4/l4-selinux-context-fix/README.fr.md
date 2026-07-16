# Lab — corriger un contexte SELinux durablement

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-selinux-context-fix`

## Rappel

[**SELinux sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Chaque fichier a un **type** SELinux. Un service confiné ne lit que les fichiers
au type autorisé par sa policy (`httpd_sys_content_t` pour le contenu web).
`chcon` pose une étiquette mais un relabel la perd ; `semanage fcontext -a -t
<type> "<regex-chemin>"` écrit une règle persistante et `restorecon -Rv <chemin>`
l'applique. `ls -Z` montre le type actif.

## Objectifs

- les fichiers sous `/srv/labweb` ont le type `httpd_sys_content_t` ;
- une règle `semanage fcontext` persistante existe pour `/srv/labweb`.

## Valider

```bash
dsoxlab check l4-selinux-context-fix
```
