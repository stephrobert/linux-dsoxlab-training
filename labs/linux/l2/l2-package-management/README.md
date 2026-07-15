# Lab — package management with dnf

> Prepare: `dsoxlab provision` then `dsoxlab run l2-package-management`

## Recap

[**dnf on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

`dnf install <pkg>` adds a package and its dependencies; `dnf remove <pkg>` takes
it out; `dnf list installed` and `rpm -q <pkg>` query what is present. `rpm -ql
<pkg>` lists the files a package owns.

## Objectives

- install `tree`;
- remove `zip`;
- confirm with `rpm -q`.

## Validate

```bash
dsoxlab check l2-package-management
```
