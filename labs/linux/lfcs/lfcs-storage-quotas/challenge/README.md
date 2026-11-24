# Capping disk usage with XFS quotas

## The situation

A shared filesystem with no quota is a filesystem one user can fill on their own.
**Quotas** cap how much space an account may consume — and on XFS they are not a
service you start: they are enabled **at mount time**, by a mount option. Forget
that option in `/etc/fstab` and your quotas silently vanish at the next reboot.

A dedicated 5 GB disk, **`/dev/vdb`**, is attached to the VM and still blank. The
user **`devops`** already exists.

The point: accounting and enforcing are two different things. Quota accounting
that is on but not enforced protects nothing: the filesystem's quota state must
show both. And it is the `/etc/fstab` entry that makes the whole thing survive a
reboot.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/quotas/

## What is asked

### Mission

Enable XFS user quotas on a dedicated disk and enforce a limit on `devops`.

### Goal (expected state)

1. `/dev/vdb` is formatted XFS and mounted on `/srv/data`.
2. User quotas are ON — both `Accounting` and `Enforcement`.
3. `/etc/fstab` makes the mount **and** the quota option persistent.
4. `devops` is capped at **40M soft / 50M hard**.

### Constraints

- The quota is enabled by a **mount option**, not by a service.
- Validation reads `findmnt`, `xfs_quota -x -c "state -u"`, `/etc/fstab` and
  `xfs_quota -x -c "report -u -b"`.

### Validation

```bash
dsoxlab check lfcs-storage-quotas
```
