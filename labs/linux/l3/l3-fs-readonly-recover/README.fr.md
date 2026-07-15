# Lab — récupérer un filesystem en lecture seule

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-fs-readonly-recover`

## Rappel

[**Récupération filesystem en lecture seule sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/)

`findmnt <mnt>` montre les options actives d'un montage (`ro` vs `rw`).
`mount -o remount,rw <mnt>` le bascule sans démonter. Une mauvaise option dans
`/etc/fstab` fait échouer `mount -a` — et un vrai boot tomberait en mode urgence —
donc teste toujours fstab avec `mount -a` après l'avoir édité.

## Objectifs

- `/srv/data` remonté en **lecture-écriture** et inscriptible ;
- `/etc/fstab` corrigé pour que `mount -a` ne renvoie plus d'erreur.

## Valider

```bash
dsoxlab check l3-fs-readonly-recover
```
