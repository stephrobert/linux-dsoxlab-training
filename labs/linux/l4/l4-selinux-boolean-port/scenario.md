# Context — SELinux is enforcing, and it's saying no

SELinux is in **enforcing** mode. A web app needs two things the policy forbids by
default: it must open outbound network connections, and it must listen on the
non-standard port **8404/tcp**. You won't disable SELinux — you'll grant exactly
what's needed, persistently.

The point: SELinux booleans are policy switches, and a switch flipped live
reverts on its own at reboot unless you explicitly ask otherwise. Non-standard
ports, on the other hand, must be **labeled**: without a label, a confined
service simply has no right to bind them.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
