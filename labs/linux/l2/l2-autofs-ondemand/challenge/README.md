# Challenge — l2-autofs-ondemand

## Mission

Configure autofs to mount the extra disk on demand under `/autofs/data`.

## Goal (expected state)

1. The **autofs** service is running.
2. A **master** map maps `/autofs` to `/etc/auto.lab`.
3. The **mount** map `/etc/auto.lab` describes `data` as `xfs` toward the
   partition.
4. Accessing `/autofs/data` **triggers** the mount (`marker.txt` readable, xfs
   type).

## Constraints

- Target partition in `/root/autofs-disk.env`. `systemctl restart autofs` after
  editing the maps. Validation **triggers the access** and reads the real state.

## Validation

```bash
dsoxlab check l2-autofs-ondemand
```
