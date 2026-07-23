# Context — Add redundant storage with software RAID

On **alma-rhcsa-1.lab**, a small service stores data that must survive a single
disk failure. You don't have a hardware RAID controller, so you'll use **Linux
software RAID** with `mdadm`.

Two spare disks are attached to the machine; their device names are recorded in
`/root/raid-disks.env`, and they are the only ones you may touch. What you need
out of them is a mirror that holds up, and that is still there after a reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/
