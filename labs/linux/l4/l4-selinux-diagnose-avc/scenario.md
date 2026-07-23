# Context — a 403 that isn't a permissions problem

`httpd` is running and `/var/www/html/index.html` exists and is world-readable,
yet the site returns **403 Forbidden**. Unix permissions are fine — this is
**SELinux** denying `httpd` access because the file carries the wrong label. The
denial is recorded as an **AVC** in the audit log. Read it, and fix it the right
way — no `setenforce 0`.

The point: an SELinux denial looks like a permissions bug but isn't. The audit
log keeps the exact trace of the denial, and tools exist to turn it into a
readable cause. Disabling SELinux is never the fix.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
