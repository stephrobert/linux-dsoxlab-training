# Context — the interface is configured but dead

A connection called `lab-net` exists on interface `lab1` with a correct static
address, yet the interface carries no IP and it won't come back after a reboot.
Something's off with its state — find it and bring the link back to life.

Your mission, on the VM (work on `lab1`, **never touch `enp5s0`** — management):

1. **Diagnose** why `lab-net` is dead (`nmcli con show lab-net`, `nmcli device`,
   `ip addr show lab1`). It's configured but inactive.
2. **Bring it up** (`nmcli con up lab-net`).
3. Make it **auto-connect** so it survives a reboot
   (`nmcli con mod lab-net connection.autoconnect yes`).

The point: a connection can be fully configured yet **inactive**, and one with
`autoconnect no` will not come back on boot — the two failure modes you must read
from `nmcli` output, not guess.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/
