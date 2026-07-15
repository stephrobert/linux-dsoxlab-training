# Lab — persistent NFS mount

> Prepare (provisions BOTH hosts): `dsoxlab provision` then
> `dsoxlab run l2-nfs-mount-persist`

## Recap

[**NFS on the companion guide**](https://blog.stephane-robert.info/docs/services/stockage/nfs/)

A server exports a directory via `/etc/exports`; a client mounts it with
`mount -t nfs <server>:/path /mnt`. Persist it in `/etc/fstab` with type `nfs`
and the **`_netdev`** option (so the boot waits for the network). `nfs-utils`
provides the client; `showmount -e <server>` lists exports.

## Objectives

On the **client** (`alma-rhcsa-1`):

- mount the server's `/srv/export` on `/mnt/nfs`;
- persist it in fstab as `nfs` with `_netdev`;
- `mount -a`, and `/mnt/nfs/hello.txt` must be readable.

The server address is in `/root/nfs-server.env`.

## Validate

```bash
dsoxlab check l2-nfs-mount-persist
```
