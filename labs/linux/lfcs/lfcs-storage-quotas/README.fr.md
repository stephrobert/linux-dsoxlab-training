# Lab — quotas utilisateur XFS

> Préparer : `dsoxlab provision` puis `dsoxlab run lfcs-storage-quotas`

## Rappel

[**Les quotas sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/)

Sur XFS, les quotas s'activent par une **option de montage**, pas par un service :
`uquota` (utilisateurs) ou `gquota` (groupes). `xfs_quota -x -c "state -u"
<montage>` montre deux choses distinctes — `Accounting` (mesurer) et
`Enforcement` (plafonner). Les limites se posent avec
`xfs_quota -x -c "limit bsoft=… bhard=… <user>" <montage>` et se relisent avec
`report -u -b`.

L'option de montage doit figurer dans `/etc/fstab`, sinon les quotas sont perdus
au prochain reboot.

## Objectifs

- `/dev/vdb` formaté en XFS et monté sur `/srv/data` ;
- quotas utilisateur ON (comptabilité **et** application), persistants via
  `/etc/fstab` ;
- `devops` plafonné à 40M souple / 50M dur.

## Valider

```bash
dsoxlab check lfcs-storage-quotas
```
