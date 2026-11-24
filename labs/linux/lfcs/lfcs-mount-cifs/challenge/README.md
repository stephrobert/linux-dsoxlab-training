# Mounting an SMB share without leaking the password

## The situation

SMB/CIFS is how Linux talks to Windows file servers — and to any Samba server.
Mounting a share is easy; mounting it **persistently and safely** is where people
slip. Two traps wait for you:

- at boot, a network filesystem is not mounted at the same moment as a local
  disk, and ignoring that is enough to make the mount fail at startup;
- **`/etc/fstab` is world-readable** (`0644`). Put the SMB account's password in
  it and every user on the box can read it.

A second host serves the share **`//<server>/labshare`**. Its address and
credentials are in **`/root/smb-server.env`** on your client.

The point: a mount that works today but breaks at reboot is not done, and a
mount that works but leaks a password is worse than no mount at all.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/smb/

## What is asked

### Mission

Mount the SMB share served by the second host, persistently, without leaking the
password.

### Goal (expected state)

1. `//<server>/labshare` is mounted on `/mnt/labshare`, type `cifs`.
2. The served file `README.txt` is readable through the mount.
3. `/etc/fstab` makes it persistent, with `_netdev`.
4. The password is **not** in `/etc/fstab`; it lives in a `0600` credentials
   file referenced by `credentials=`.

### Constraints

- Server address and credentials: `/root/smb-server.env`.
- Validation reads `findmnt`, the served file, `/etc/fstab` and the mode of the
  credentials file.

### Validation

```bash
dsoxlab check lfcs-mount-cifs
```
