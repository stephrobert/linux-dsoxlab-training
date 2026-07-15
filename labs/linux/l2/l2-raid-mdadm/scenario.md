# Context — Add redundant storage with software RAID

On **alma-rhcsa-1.lab**, a small service stores data that must survive a single
disk failure. You don't have a hardware RAID controller, so you'll use **Linux
software RAID** with `mdadm`.

Two spare disks are attached. Your mission:

1. Assemble them into a **RAID 1** mirror.
2. Put a filesystem on it and mount it.
3. Make the array reassemble automatically after a reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/
