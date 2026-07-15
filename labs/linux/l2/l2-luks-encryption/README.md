# Lab — Encrypt a disk with LUKS

> Prepare the VM: `dsoxlab run l2-luks-encryption`

## Reminder

[**Disk encryption with LUKS**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/)

LUKS encrypts a block device: without the key, the data is unreadable. The
order is always format -> open -> mkfs on the mapping -> mount. Persistence is
declared in `/etc/crypttab` (which creates `/dev/mapper/...`) plus `/etc/fstab`.

## Objectives

- Format a disk as **LUKS2** and open it.
- Put a filesystem on the mapping and mount it.
- Make it unlock at boot via **`/etc/crypttab`**.

## Run and validate

```bash
dsoxlab run   l2-luks-encryption
dsoxlab check l2-luks-encryption
```
