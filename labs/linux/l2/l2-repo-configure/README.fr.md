# Lab — configurer un dépôt dnf

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-repo-configure`

## Rappel

[**dnf sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

Un dépôt se définit par un fichier `.repo` (INI) dans `/etc/yum.repos.d/` :
`[id]`, `name`, `baseurl` (ou `mirrorlist`), `enabled`, `gpgcheck` et `gpgkey`.
Garde `gpgcheck=1` pour que les paquets soient vérifiés par signature.
`dnf repolist` montre les dépôts activés, `dnf repolist --all` tous ceux
configurés.

## Objectifs

Crée `/etc/yum.repos.d/labrepo.repo` :

- id `[labrepo]`, une `baseurl` valide ;
- `enabled=1`, `gpgcheck=1` (avec `gpgkey`) ;
- `dnf repolist` liste `labrepo`.

## Valider

```bash
dsoxlab check l2-repo-configure
```
