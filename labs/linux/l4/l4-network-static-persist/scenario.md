# Context — a static address that survives reboot

A service needs a fixed IPv4 on this host, on a dedicated interface — and it must
come back after a reboot, not vanish. An `ip addr add` lasts until the next
reboot; the durable way on RHEL is a **NetworkManager connection profile**.

You work on the dedicated interface `lab0`. **Never touch the management
interface** — the one carrying your default route: it is your link to the box.

The point: a NetworkManager connection profile is written on disk, and that file
is what brings the address back after a reboot. But the profile must not only
exist, it must also be active: those are two separate checks.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/
