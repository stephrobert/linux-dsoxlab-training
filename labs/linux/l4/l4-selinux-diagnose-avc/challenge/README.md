# A 403 that isn't a permissions problem

## The situation

`httpd` is running and `/var/www/html/index.html` exists and is world-readable,
yet the site returns **403 Forbidden**. Unix permissions are fine — this is
**SELinux** denying `httpd` access because the file carries the wrong label. The
denial is recorded as an **AVC** in the audit log. Read it, and fix it the right
way — no `setenforce 0`.

The point: an SELinux denial looks like a permissions bug but isn't. The audit
log keeps the exact trace of the denial, and tools exist to turn it into a
readable cause. Disabling SELinux is never the fix.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/selinux/

## What is asked

### Mission

`http://localhost` returns 403 — an SELinux AVC, not a permissions bug. Diagnose
it and restore the context.

### Goal (expected state)

1. `/var/www/html/index.html` has type `httpd_sys_content_t` (`ls -Z`).
2. `curl http://localhost/index.html` returns `200`.
3. SELinux is still `Enforcing`.

### Constraints

- `setenforce 0` / permissive is a **fail**. Fix the label, not the mode.
- The correct type is already in policy for `/var/www/html` — `restorecon` is
  enough, no `semanage fcontext` rule needed.
- Validation reads `ls -Z`, the HTTP code, and `getenforce`.

### Validation

```bash
dsoxlab check l4-selinux-diagnose-avc
```
