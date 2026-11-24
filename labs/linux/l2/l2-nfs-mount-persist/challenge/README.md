# Mount a share from an NFS server

## The situation

This lab uses **two machines**: a server (`alma-rhcsa-2`) already exports an NFS
share `/srv/export`, and your client (`alma-rhcsa-1`) must mount it. This is the
everyday "attach the shared storage" task, with its classic reboot trap: a
network mount attempted before the network is up, and the whole boot goes
sideways.

The point: a network filesystem is declared like any other, but it depends on
something the others do not need, the network. Boot does not infer that
dependency on its own: it has to be declared.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/nfs/

## What is asked

### Mission

An NFS server (`alma-rhcsa-2`) exports `/srv/export`. On the **client**
(`alma-rhcsa-1`), mount this export persistently.

### Goal (expected state, client side)

1. `/mnt/nfs` is **mounted** (type **nfs**).
2. `/mnt/nfs/hello.txt` is **readable** (the mount does serve the server).
3. `/etc/fstab` has an `nfs` entry for `/mnt/nfs` with the **`_netdev`** option.

### Constraints

- The server IP is in `/root/nfs-server.env`. `nfs-utils` is installed.
- Reboot trap: without `_netdev`, the network mount is attempted too early at boot.
- Validation reads the **real state** of the client (mount, content, fstab).

### Validation

```bash
dsoxlab check l2-nfs-mount-persist
```
