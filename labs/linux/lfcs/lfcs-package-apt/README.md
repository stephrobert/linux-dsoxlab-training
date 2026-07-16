# Lab — Debian package management (apt/dpkg)

> Prepare: `dsoxlab provision` then `dsoxlab run lfcs-package-apt`

## Recap

[**apt on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/)

`apt-get install|remove` manages packages and dependencies; `apt-mark hold`
freezes a version so `apt upgrade` skips it (`apt-mark showhold` lists holds);
`dpkg -l <pkg>` shows install status; `dpkg -S <file>` says which package owns a
file. These are the Debian counterparts to `dnf` / `rpm -qf`.

## Objectives

- `tree` is installed;
- `tree` is on hold (`apt-mark showhold`);
- `dpkg -S /usr/bin/tree` resolves to `tree`.

## Validate

```bash
dsoxlab check lfcs-package-apt
```
