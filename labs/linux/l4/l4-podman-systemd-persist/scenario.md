# Context — a container that comes back after reboot

A container running with `podman run` dies with the machine and never returns.
On RHEL the modern way to make a container a first-class, boot-persistent service
is **Quadlet**: a `.container` unit that systemd turns into a real service.

The point: Quadlet describes a container in a declarative unit that systemd
converts into an ordinary service, wireable to boot like any other. This is what
the RHCSA objective "start a container at boot" means today — not a hand-rolled
`podman run` in rc.local.

Method in the companion guide:
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/
