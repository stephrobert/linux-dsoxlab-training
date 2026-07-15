# Lab — expiration et complexité des mots de passe

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-password-policy`

## Rappel

[**Utilisateurs et groupes sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`chage -M <max> -m <min> -W <warn> <user>` règle l'expiration par compte
(`chage -l` l'affiche). `/etc/login.defs` contient `PASS_MAX_DAYS` et consorts —
les défauts appliqués aux comptes nouvellement créés. `/etc/security/pwquality.conf`
impose la complexité, ex. `minlen` pour la longueur minimale.

## Objectifs

- `bob` : max 60, min 7, avert. 7 (`chage`) ;
- `PASS_MAX_DAYS 60` dans `/etc/login.defs` ;
- `minlen = 12` dans `/etc/security/pwquality.conf`.

## Valider

```bash
dsoxlab check l2-password-policy
```
