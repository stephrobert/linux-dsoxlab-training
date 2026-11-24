# Bon contenu, mauvaise étiquette

## La situation

Du contenu web a été placé dans un répertoire personnalisé `/srv/labweb`, mais
sous SELinux enforcing un serveur web confiné ne peut pas le lire : les fichiers
portent le mauvais type, hérité de `/srv`. Ré-étiquette, et fais en sorte que la
correction **tienne** à un relabel complet ou à un reboot, pas seulement le temps
d'une retouche ponctuelle.

L'idée : une étiquette posée à la main sur un fichier est balayée par le premier
relabel du système. La façon durable, celle qu'attend le RHCSA, consiste à
**déclarer la règle** qui dit quel type ce chemin doit porter, puis à laisser la
policy l'appliquer.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/durcissement/selinux/

## Ce qui est demandé

### Mission

Ré-étiquette `/srv/labweb` en `httpd_sys_content_t`, de façon persistante.

### Objectif (état attendu)

1. Les fichiers sous `/srv/labweb` ont le type SELinux `httpd_sys_content_t` (`ls -Z`).
2. Une règle `semanage fcontext` persistante mappe `/srv/labweb` vers ce type.

### Contraintes

- `chcon` seul échoue — il ne survit pas à un relabel. Utilise `semanage fcontext`
  + `restorecon`.
- Ne désactive pas SELinux. On lit `ls -Z` et `semanage fcontext -l`.

### Validation

```bash
dsoxlab check l4-selinux-context-fix
```
