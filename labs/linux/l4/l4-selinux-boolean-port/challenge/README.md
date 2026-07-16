# Challenge — l4-selinux-boolean-port

## Mission

Under enforcing SELinux, allow the app: enable a boolean persistently and label a
non-standard port.

## Goal (expected state)

1. `getsebool httpd_can_network_connect` → `on`, and it survives reboot (`-P`).
2. `8404/tcp` is labeled `http_port_t` (`semanage port -l`).

## Constraints

- Do **not** disable SELinux (`setenforce 0` / permissive is a fail).
- Validation reads `getsebool` and `semanage port`, not your history.

## Validation

```bash
dsoxlab check l4-selinux-boolean-port
```
