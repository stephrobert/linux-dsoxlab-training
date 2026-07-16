# Context — static networking the Ubuntu way: netplan

Debian/Ubuntu describe the network in **netplan** YAML files under `/etc/netplan/`;
`netplan apply` renders them to the backend (systemd-networkd or NetworkManager)
and brings them up — and they persist across reboots. You need a fixed address and
a static route on a dedicated interface.

Your mission, on the Ubuntu VM (use the dedicated interface `lab0`, **never touch
`enp5s0`** — that's management):

1. Create **`/etc/netplan/99-lab.yaml`** (mode `0600`) that declares, on a
   `dummy-devices` interface **`lab0`**:
   - the static address **`192.0.2.50/24`**;
   - a static **route** to **`198.51.100.0/24` via `192.0.2.1`**.
2. **Apply** it: `sudo netplan apply` (check first with `sudo netplan generate`).

The point: netplan is declarative — you edit YAML, not `ip` commands, and
`netplan apply` makes it live and persistent. `netplan generate` validates the
syntax before you apply. `ip addr` / `ip route` show the result.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/
