# Lab — persistent SMB/CIFS mount

> Prepare: `dsoxlab provision` then `dsoxlab run lfcs-mount-cifs`

## Recap

[**SMB on the companion guide**](https://blog.stephane-robert.info/docs/services/stockage/smb/)

A CIFS mount needs the `cifs-utils` package and an authenticated share:
`mount -t cifs //<server>/<share> <mountpoint> -o credentials=<file>`.

Two things make it production-grade:

- **`_netdev`** in `/etc/fstab` — the mount waits for the network at boot;
- a **credentials file** (`username=` / `password=` lines) in `0600`, because
  `/etc/fstab` is world-readable and must never hold a password.

The server address and credentials are in `/root/smb-server.env`.

## Objectives

- `//<server>/labshare` mounted on `/mnt/labshare`, type `cifs`;
- the served file readable through the mount;
- `/etc/fstab` entry persistent with `_netdev`;
- password absent from `/etc/fstab`, held in a `0600` credentials file.

## Validate

```bash
dsoxlab check lfcs-mount-cifs
```
