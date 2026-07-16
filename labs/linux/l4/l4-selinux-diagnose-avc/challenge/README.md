# Challenge — l4-selinux-diagnose-avc

## Mission

`http://localhost` returns 403 — an SELinux AVC, not a permissions bug. Diagnose
it and restore the context.

## Goal (expected state)

1. `/var/www/html/index.html` has type `httpd_sys_content_t` (`ls -Z`).
2. `curl http://localhost/index.html` returns `200`.
3. SELinux is still `Enforcing`.

## Constraints

- `setenforce 0` / permissive is a **fail**. Fix the label, not the mode.
- The correct type is already in policy for `/var/www/html` — `restorecon` is
  enough, no `semanage fcontext` rule needed.
- Validation reads `ls -Z`, the HTTP code, and `getenforce`.

## Validation

```bash
dsoxlab check l4-selinux-diagnose-avc
```
