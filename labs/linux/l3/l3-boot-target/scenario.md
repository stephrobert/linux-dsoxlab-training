# Context — a server should boot headless

Someone left this machine defaulting to a **graphical** boot target — pointless
on a server, and a waste of resources. Bring it back to a text multi-user boot.

Your mission, on the VM:

1. Check the current default (`systemctl get-default`).
2. Set the default to **`multi-user.target`** (no graphical layer).

The point: systemd **targets** are boot states; `multi-user.target` is the
standard server state (networking + services, no GUI), `graphical.target` adds a
display manager. `systemctl set-default` changes the `/etc/systemd/system/
default.target` symlink, so it survives a reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/
