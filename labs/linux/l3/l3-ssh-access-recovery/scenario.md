# Context — a landmine in the sshd config

Someone dropped a config snippet with a typo: the sshd configuration no longer
passes its syntax check. The **running** sshd still works (it only re-reads on
reload), so you can still get in — but the next `systemctl reload sshd` or reboot
would leave the server unreachable. Defuse it before that happens.

The point: a broken sshd config is how admins lock themselves out. The daemon can
check its configuration *offline*, before any reload, and can also print the
settings it would really apply. That reflex is what's missing here.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/
