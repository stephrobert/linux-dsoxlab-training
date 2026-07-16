# Lab — fix a SELinux file context persistently

> Prepare: `dsoxlab provision` then `dsoxlab run l4-selinux-context-fix`

## Recap

[**SELinux on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Every file has an SELinux **type**. A confined service only reads files with the
type its policy allows (`httpd_sys_content_t` for web content). `chcon` sets a
label but a relabel loses it; `semanage fcontext -a -t <type> "<path-regex>"`
writes a persistent rule and `restorecon -Rv <path>` applies it. `ls -Z` shows the
live type.

## Objectives

- files under `/srv/labweb` have type `httpd_sys_content_t`;
- a persistent `semanage fcontext` rule exists for `/srv/labweb`.

## Validate

```bash
dsoxlab check l4-selinux-context-fix
```
