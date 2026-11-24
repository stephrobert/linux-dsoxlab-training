# Right content, wrong label

## The situation

Web content was placed in a custom directory `/srv/labweb`, but under enforcing
SELinux a confined web server can't read it: the files carry the wrong type,
inherited from `/srv`. Relabel it — and make the fix **stick** through a full
relabel or a reboot, not just for the lifetime of a one-off tweak.

The point: a label set by hand on a file is wiped by the system's next relabel.
The durable way, the one RHCSA expects, is to **declare the rule** that says
which type this path must carry, then let the policy apply it.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/selinux/

## What is asked

### Mission

Relabel `/srv/labweb` to `httpd_sys_content_t`, persistently.

### Goal (expected state)

1. Files under `/srv/labweb` have SELinux type `httpd_sys_content_t` (`ls -Z`).
2. A persistent `semanage fcontext` rule maps `/srv/labweb` to that type.

### Constraints

- `chcon` alone fails — it doesn't survive a relabel. Use `semanage fcontext` +
  `restorecon`.
- Don't disable SELinux. Validation reads `ls -Z` and `semanage fcontext -l`.

### Validation

```bash
dsoxlab check l4-selinux-context-fix
```
