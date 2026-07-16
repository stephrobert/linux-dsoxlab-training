# Challenge — lfcs-storage-quotas

## Mission

Enable XFS user quotas on a dedicated disk and enforce a limit on `devops`.

## Goal (expected state)

1. `/dev/vdb` is formatted XFS and mounted on `/srv/data`.
2. User quotas are ON — both `Accounting` and `Enforcement`.
3. `/etc/fstab` makes the mount **and** the quota option persistent.
4. `devops` is capped at **40M soft / 50M hard**.

## Constraints

- The quota is enabled by a **mount option**, not by a service.
- Validation reads `findmnt`, `xfs_quota -x -c "state -u"`, `/etc/fstab` and
  `xfs_quota -x -c "report -u -b"`.

## Validation

```bash
dsoxlab check lfcs-storage-quotas
```
