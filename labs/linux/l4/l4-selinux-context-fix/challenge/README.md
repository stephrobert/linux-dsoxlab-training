# Challenge — l4-selinux-context-fix

## Mission

Relabel `/srv/labweb` to `httpd_sys_content_t`, persistently.

## Goal (expected state)

1. Files under `/srv/labweb` have SELinux type `httpd_sys_content_t` (`ls -Z`).
2. A persistent `semanage fcontext` rule maps `/srv/labweb` to that type.

## Constraints

- `chcon` alone fails — it doesn't survive a relabel. Use `semanage fcontext` +
  `restorecon`.
- Don't disable SELinux. Validation reads `ls -Z` and `semanage fcontext -l`.

## Validation

```bash
dsoxlab check l4-selinux-context-fix
```
