# Challenge — lfcs-mount-cifs

## Mission

Mount the SMB share served by the second host, persistently, without leaking the
password.

## Goal (expected state)

1. `//<server>/labshare` is mounted on `/mnt/labshare`, type `cifs`.
2. The served file `README.txt` is readable through the mount.
3. `/etc/fstab` makes it persistent, with `_netdev`.
4. The password is **not** in `/etc/fstab`; it lives in a `0600` credentials
   file referenced by `credentials=`.

## Constraints

- Server address and credentials: `/root/smb-server.env`.
- Validation reads `findmnt`, the served file, `/etc/fstab` and the mode of the
  credentials file.

## Validation

```bash
dsoxlab check lfcs-mount-cifs
```
