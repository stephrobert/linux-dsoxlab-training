# Challenge — l4-selinux-context-fix

## Mission

Ré-étiquette `/srv/labweb` en `httpd_sys_content_t`, de façon persistante.

## Objectif (état attendu)

1. Les fichiers sous `/srv/labweb` ont le type SELinux `httpd_sys_content_t` (`ls -Z`).
2. Une règle `semanage fcontext` persistante mappe `/srv/labweb` vers ce type.

## Contraintes

- `chcon` seul échoue — il ne survit pas à un relabel. Utilise `semanage fcontext`
  + `restorecon`.
- Ne désactive pas SELinux. On lit `ls -Z` et `semanage fcontext -l`.

## Validation

```bash
dsoxlab check l4-selinux-context-fix
```
