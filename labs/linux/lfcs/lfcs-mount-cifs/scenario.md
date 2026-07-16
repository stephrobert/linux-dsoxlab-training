# Context — mounting an SMB share without leaking the password

SMB/CIFS is how Linux talks to Windows file servers — and to any Samba server.
Mounting a share is easy; mounting it **persistently and safely** is where people
slip. Two traps wait for you:

- a network filesystem mounted without **`_netdev`** is attempted before the
  network is up at boot;
- **`/etc/fstab` is world-readable** (`0644`). Put `password=…` in it and every
  user on the box can read the SMB account's password.

A second host serves the share **`//<server>/labshare`**. Its address and
credentials are in **`/root/smb-server.env`** on your client.

Your mission, on the Ubuntu client:

1. **Mount** `//<server>/labshare` on **`/mnt/labshare`**, type `cifs`.
2. Make it **persistent** in `/etc/fstab` with the **`_netdev`** option.
3. Keep the password **out of `/etc/fstab`**: put it in a **credentials file**
   readable only by root (`0600`) and reference it with `credentials=<path>`.
4. Prove the entry is valid with `sudo mount -a`.

The point: a mount that works today but breaks at reboot is not done, and a
mount that works but leaks a password is worse than no mount at all.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/stockage/smb/
