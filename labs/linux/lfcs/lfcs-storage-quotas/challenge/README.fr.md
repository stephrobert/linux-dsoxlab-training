# Challenge — lfcs-storage-quotas

## Mission

Active les quotas utilisateur XFS sur un disque dédié et impose une limite à
`devops`.

## Objectif (état attendu)

1. `/dev/vdb` est formaté en XFS et monté sur `/srv/data`.
2. Les quotas utilisateur sont ON — `Accounting` **et** `Enforcement`.
3. `/etc/fstab` rend le montage **et** l'option de quota persistants.
4. `devops` est plafonné à **40M souple / 50M dur**.

## Contraintes

- Le quota s'active par une **option de montage**, pas par un service.
- On lit `findmnt`, `xfs_quota -x -c "state -u"`, `/etc/fstab` et
  `xfs_quota -x -c "report -u -b"`.

## Validation

```bash
dsoxlab check lfcs-storage-quotas
```
