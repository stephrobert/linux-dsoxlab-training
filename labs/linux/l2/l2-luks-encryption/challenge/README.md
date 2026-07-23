# Challenge — l2 : Encrypt a disk with LUKS

## Mission

A spare disk is available on **alma-rhcsa-1.lab** (its name is in
`/root/luks-disk.env`), with a key file `/root/luks.key`. Encrypt it so its
data is unreadable if the disk is stolen.

1. Format the disk as **LUKS2** (use the key file).
2. **Open** it as `/dev/mapper/coffre`.
3. Put an **xfs** filesystem on it and mount it on `/mnt/coffre`.
4. Declare it in **`/etc/crypttab`** so it unlocks at boot.

## Constraints

- The disk must be **LUKS version 2**.
- `/dev/mapper/coffre` must be open and mounted on `/mnt/coffre`.
- `/etc/crypttab` must contain the `coffre` entry.

## Useful approach

The steps follow from the companion guide linked in the course's
`## Reminder`. If you get stuck, `dsoxlab hint` spells them out, at the
stated cost.

## Validation

```bash
dsoxlab check l2-luks-encryption
```
