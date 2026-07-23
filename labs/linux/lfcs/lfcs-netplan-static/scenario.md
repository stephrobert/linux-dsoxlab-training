# Context — static networking the Ubuntu way: netplan

Debian and Ubuntu describe the network in **netplan** YAML files under
`/etc/netplan/`. You need a fixed address and a static route on a dedicated
interface, and both must come back after a reboot.

You work on the dedicated interface `lab0`. **Never touch the management
interface** — the one carrying your default route: it is your link to the box.

The point: netplan is declarative, you describe the wanted state in YAML instead
of chaining `ip` commands. Writing the file is not enough: until it has been
rendered to the network backend, nothing changes on the machine. And getting that
content wrong on a remote host means losing your hand on it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/
