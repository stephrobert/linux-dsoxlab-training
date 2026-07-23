# Context — a server should boot headless

Someone left this machine defaulting to a **graphical** boot target — pointless
on a server, and a waste of resources. Bring it back to a text multi-user boot.

The point: systemd **targets** are boot states; `multi-user.target` is the
standard server state (networking + services, no GUI), `graphical.target` adds a
display manager. The system marks one of them as the default target, and that
designation, and only that, is what survives a reboot.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/
