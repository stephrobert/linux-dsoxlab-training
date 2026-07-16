# Lab — diagnose an SELinux AVC denial

> Prepare: `dsoxlab provision` then `dsoxlab run l4-selinux-diagnose-avc`

## Recap

[**SELinux on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

When a confined service is denied, SELinux logs an **AVC** in the audit log.
`ausearch -m AVC -ts recent` and `sealert` turn it into a readable cause.
For a mislabeled file in a standard path, `restorecon` re-applies the policy's
expected type (`httpd_sys_content_t` for `/var/www/html`). `ls -Z` shows the type.
Never `setenforce 0`.

## Objectives

- `/var/www/html/index.html` has type `httpd_sys_content_t`;
- `http://localhost/index.html` returns `200`;
- SELinux stays `Enforcing`.

## Validate

```bash
dsoxlab check l4-selinux-diagnose-avc
```
