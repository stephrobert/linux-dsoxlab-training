# Context — SELinux is enforcing, and it's saying no

SELinux is in **enforcing** mode. A web app needs two things the policy forbids by
default: it must open outbound network connections, and it must listen on the
non-standard port **8404/tcp**. You won't disable SELinux — you'll grant exactly
what's needed, persistently.

Your mission, on the VM:

1. Turn the boolean **`httpd_can_network_connect`** on, **persistently**
   (`setsebool -P`).
2. Label port **`8404/tcp`** as **`http_port_t`**
   (`semanage port -a -t http_port_t -p tcp 8404`).

The point: SELinux booleans toggle policy switches — `-P` makes them survive a
reboot; without it they revert. Non-standard ports must be **labeled** with
`semanage port` or a confined service can't bind them. `getsebool` and
`semanage port -l` read the state.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
