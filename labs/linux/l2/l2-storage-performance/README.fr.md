# Lab — optimiser un montage avec noatime

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-storage-performance`

## Rappel

[**Performances disques sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/)

Les options de montage changent le comportement d'un filesystem. `noatime`
désactive les mises à jour de date d'accès — un gain courant pour les charges
très lues ou avec beaucoup de petits fichiers. Mets-le dans `/etc/fstab` (4ᵉ
champ) pour la persistance, et `mount -o remount <mnt>` pour l'appliquer à chaud.
`findmnt <mnt>` montre les options actives.

## Objectifs

Sur `/srv/data` :

- ajoute `noatime` aux options fstab (`defaults,noatime`) ;
- `mount -o remount /srv/data` pour l'activer ;
- `findmnt /srv/data` doit montrer `noatime`.

## Valider

```bash
dsoxlab check l2-storage-performance
```
