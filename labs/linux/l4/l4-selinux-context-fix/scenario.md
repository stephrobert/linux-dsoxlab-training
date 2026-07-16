# Context — right content, wrong label

Web content was placed in a custom directory `/srv/labweb`, but under enforcing
SELinux a confined web server can't read it: the files carry the wrong type
(inherited from `/srv`, not `httpd_sys_content_t`). Relabel it — and make the fix
**stick** through a full relabel or reboot, not just a one-off `chcon`.

Your mission, on the VM:

1. Add a **file-context rule** mapping `/srv/labweb` (and everything under it) to
   type **`httpd_sys_content_t`**
   (`semanage fcontext -a -t httpd_sys_content_t "/srv/labweb(/.*)?"`).
2. **Apply** it to the existing files (`restorecon -Rv /srv/labweb`).

The point: `chcon` changes a label now but a relabel wipes it; `semanage fcontext`
writes a **persistent rule** and `restorecon` applies it from that rule — the
durable RHCSA way. `ls -Z` shows the live type.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
