# Lab — reclaim a full filesystem

> Prepare: `dsoxlab provision` then `dsoxlab run l2-disk-space-troubleshoot`

## Recap

[**Disk space on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/)

`df -h` lists filesystems and their usage; `du -h --max-depth=1 <dir>` shows how
much each subdirectory holds, so you can walk down to the culprit. If `df` says
full but `du` disagrees, `lsof +L1` finds a deleted-but-open file held by a
process.

## Objectives

On the full `/srv/data`:

- find the big consumer (`df`, then `du`);
- remove the junk (the bloated cache) to drop usage **below 50%**;
- keep `/srv/data/app.log` and leave the filesystem mounted.

## Validate

```bash
dsoxlab check l2-disk-space-troubleshoot
```
