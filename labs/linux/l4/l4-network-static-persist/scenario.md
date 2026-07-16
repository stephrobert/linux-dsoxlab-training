# Context — a static address that survives reboot

A service needs a fixed IPv4 on this host, on a dedicated interface — and it must
come back after a reboot, not vanish. An `ip addr add` lasts until the next
reboot; the durable way on RHEL is a **NetworkManager connection profile**.

Your mission, on the VM (work on the dedicated interface `lab0`, **never touch
`enp5s0`** — that's your management link):

1. Create a NetworkManager connection named **`lab-static`** on interface
   `lab0` (type `dummy`).
2. Give it the static address **`192.0.2.50/24`** (`ipv4.method manual`).
3. **Activate** it (`nmcli con up lab-static`).

The point: `nmcli con add … ipv4.method manual ipv4.addresses …` writes a profile
under `/etc/NetworkManager/system-connections/`, which is what makes the address
survive a reboot. `ip addr add` does not.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/
