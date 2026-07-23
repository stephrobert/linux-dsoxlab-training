# Context — Protect data at rest with LUKS

On **alma-rhcsa-1.lab**, a removable disk will hold sensitive exports. If the
disk leaves the building, its content must remain unreadable. You'll encrypt it
with **LUKS2** and make it unlock automatically at boot via a key file.

The spare disk to work on is named in `/root/luks-disk.env`, and the key that
will open it is already on the machine.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/
