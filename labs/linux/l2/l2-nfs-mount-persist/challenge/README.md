# Challenge — l2-nfs-mount-persist

## Mission

An NFS server (`alma-rhcsa-2`) exports `/srv/export`. On the **client**
(`alma-rhcsa-1`), mount this export persistently.

## Goal (expected state, client side)

1. `/mnt/nfs` is **mounted** (type **nfs**).
2. `/mnt/nfs/hello.txt` is **readable** (the mount does serve the server).
3. `/etc/fstab` has an `nfs` entry for `/mnt/nfs` with the **`_netdev`** option.

## Constraints

- The server IP is in `/root/nfs-server.env`. `nfs-utils` is installed.
- Reboot trap: without `_netdev`, the network mount is attempted too early at boot.
- Validation reads the **real state** of the client (mount, content, fstab).

## Validation

```bash
dsoxlab check l2-nfs-mount-persist
```
