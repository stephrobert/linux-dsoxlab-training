# SELinux is enforcing, and it's saying no

## The situation

SELinux is in **enforcing** mode. A web app needs two things the policy forbids by
default: it must open outbound network connections, and it must listen on the
non-standard port **8404/tcp**. You won't disable SELinux — you'll grant exactly
what's needed, persistently.

The point: SELinux booleans are policy switches, and a switch flipped live
reverts on its own at reboot unless you explicitly ask otherwise. Non-standard
ports, on the other hand, must be **labeled**: without a label, a confined
service simply has no right to bind them.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/selinux/

## What is asked

### Mission

Under enforcing SELinux, allow the app: enable a boolean persistently and label a
non-standard port.

### Goal (expected state)

1. `getsebool httpd_can_network_connect` → `on`, and it survives reboot (`-P`).
2. `8404/tcp` is labeled `http_port_t` (`semanage port -l`).

### Constraints

- Do **not** disable SELinux (`setenforce 0` / permissive is a fail).
- Validation reads `getsebool` and `semanage port`, not your history.

### Validation

```bash
dsoxlab check l4-selinux-boolean-port
```
