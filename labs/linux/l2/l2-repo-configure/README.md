# Lab — configure a dnf repository

> Prepare: `dsoxlab provision` then `dsoxlab run l2-repo-configure`

## Recap

[**dnf on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

A repo is defined by an INI `.repo` file in `/etc/yum.repos.d/`: `[id]`, `name`,
`baseurl` (or `mirrorlist`), `enabled`, `gpgcheck` and `gpgkey`. Keep
`gpgcheck=1` so packages are signature-verified. `dnf repolist` shows enabled
repos, `dnf repolist --all` shows every configured one.

## Objectives

Create `/etc/yum.repos.d/labrepo.repo`:

- id `[labrepo]`, a valid `baseurl`;
- `enabled=1`, `gpgcheck=1` (with `gpgkey`);
- `dnf repolist` lists `labrepo`.

## Validate

```bash
dsoxlab check l2-repo-configure
```
