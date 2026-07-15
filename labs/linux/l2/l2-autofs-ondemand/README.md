# Lab — on-demand mounts with autofs

> Prepare: `dsoxlab provision` then `dsoxlab run l2-autofs-ondemand`

## Recap

[**autofs on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/)

autofs mounts a path only when it is accessed and unmounts it after an idle
`--timeout`. A **master map** (`/etc/auto.master` or a file in
`/etc/auto.master.d/`) maps a mount point to a **mount map**; the mount map lists
keys and how to mount them: `key  -fstype=xfs  :/dev/sdX1`. `systemctl restart
autofs` reloads maps.

## Objectives

- master map: `/autofs` → `/etc/auto.lab`;
- mount map `/etc/auto.lab`: `data -fstype=xfs :<partition>`;
- autofs enabled and running;
- accessing `/autofs/data` mounts it (marker.txt readable).

## Validate

```bash
dsoxlab check l2-autofs-ondemand
```
