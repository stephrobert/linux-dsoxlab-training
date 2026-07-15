# Context — Protect data at rest with LUKS

On **alma-rhcsa-1.lab**, a removable disk will hold sensitive exports. If the
disk leaves the building, its content must remain unreadable. You'll encrypt it
with **LUKS2** and make it unlock automatically at boot via a key file.

Your mission:

1. Encrypt the disk (LUKS2) and open it.
2. Put a filesystem on it and mount it.
3. Make it unlock at boot through `/etc/crypttab`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/
