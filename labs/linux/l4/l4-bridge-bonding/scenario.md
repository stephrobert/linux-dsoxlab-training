# Context — aggregate two links for redundancy

Two network links should act as one, with failover: if the active one drops, the
other takes over. That's a **bond** in `active-backup` mode. On top of it sits a
**bridge** — the layer where VMs or containers would attach. Build both with
NetworkManager, on dedicated interfaces, and make it persistent.

Your mission, on the VM (work on `dummy1`/`dummy2`/`bond0`/`br0`, **never touch
`enp5s0`** — management):

1. Create a bond **`bond0`**, mode **`active-backup`** with `miimon=100`
   (`nmcli con add type bond ... bond.options "mode=active-backup,miimon=100"`).
2. Enslave **two** interfaces to it — `dummy1` and `dummy2`
   (`nmcli con add type dummy ... master bond0`).
3. Create a bridge **`br0`** and make **`bond0` a port** of it
   (`nmcli con mod bond0 master br0 slave-type bridge`), then bring it all up.

The point: a bond aggregates links (`active-backup` = redundancy, one active at a
time, `miimon` polls link state); a bridge sits above to give a single L2 domain.
NetworkManager stores each as a persistent connection profile, so it survives a
reboot. `/proc/net/bonding/bond0` shows the mode and slaves;
`/sys/class/net/br0/brif/` lists the bridge ports.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/
