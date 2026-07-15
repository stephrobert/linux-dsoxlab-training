# Context — mount a share from an NFS server

This lab uses **two machines**: a server (`alma-rhcsa-2`) already exports an NFS
share `/srv/export`, and your client (`alma-rhcsa-1`) must mount it. This is the
everyday "attach the shared storage" task — and the classic reboot trap is
forgetting `_netdev`, so the mount is attempted before the network is up.

Your mission, on the **client** VM:

1. Find the server's address (it is recorded in `/root/nfs-server.env`).
2. Mount its `/srv/export` on `/mnt/nfs`.
3. Make it **persistent** in `/etc/fstab`, type `nfs`, with the **`_netdev`**
   option so it waits for the network at boot.
4. Validate with `mount -a` — `/mnt/nfs/hello.txt` should become readable.

The point: a network filesystem is mounted like any other but needs `_netdev`
(and `nfs-utils`). `showmount -e <server>` lists a server's exports.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/stockage/nfs/
