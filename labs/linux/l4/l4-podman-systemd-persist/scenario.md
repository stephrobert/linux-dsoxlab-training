# Context — a container that comes back after reboot

A container running with `podman run` dies with the machine and never returns.
On RHEL the modern way to make a container a first-class, boot-persistent service
is **Quadlet**: a `.container` unit that systemd turns into a real service.

Your mission, on the VM:

1. Write `/etc/containers/systemd/weblab.container` describing a container named
   `weblab` from `registry.access.redhat.com/ubi9/ubi-micro`, running
   `sleep infinity`, with an `[Install]` section so it starts at boot.
2. `systemctl daemon-reload` (Quadlet generates `weblab.service`).
3. Start it: `systemctl start weblab.service`.

The point: Quadlet reads `/etc/containers/systemd/*.container` and generates
systemd services at `daemon-reload`; the `[Install] WantedBy=` is what wires it to
start on boot. This is what the RHCSA objective "start a container at boot" means
today — not a hand-rolled `podman run` in rc.local.

Method in the companion guide:
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/
