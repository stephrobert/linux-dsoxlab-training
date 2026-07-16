# Context — a 403 that isn't a permissions problem

`httpd` is running and `/var/www/html/index.html` exists and is world-readable,
yet the site returns **403 Forbidden**. Unix permissions are fine — this is
**SELinux** denying `httpd` access because the file carries the wrong label. The
denial is recorded as an **AVC** in the audit log. Read it, and fix it the right
way — no `setenforce 0`.

Your mission, on the VM:

1. **Diagnose** the denial: `sudo ausearch -m AVC -ts recent` (or `sealert`)
   points at `/var/www/html/index.html` and the wrong type.
2. **Restore** the correct context with `restorecon` (the right type,
   `httpd_sys_content_t`, is already defined in policy for `/var/www/html` — no
   `semanage` rule needed).
3. Confirm the site now returns **200**.

The point: an SELinux denial looks like a permissions bug but isn't. `ausearch`
/`sealert` turn the AVC into a readable cause; `restorecon` re-applies the
policy's expected label for a standard path. Disabling SELinux is never the fix.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
