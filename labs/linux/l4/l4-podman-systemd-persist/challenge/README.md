# Challenge — l4-podman-systemd-persist

## Mission

Make container `weblab` a boot-persistent systemd service with Quadlet.

## Goal (expected state)

1. `/etc/containers/systemd/weblab.container` exists and has `[Install] WantedBy`.
2. `weblab.service` is active.
3. Container `weblab` is running.

## Constraints

- It must be a Quadlet unit (not a manual `podman run`): the on-disk
  `.container` file with an `[Install]` section is what survives a reboot.
- Validation reads systemd and Podman state, not your history.

## Validation

```bash
dsoxlab check l4-podman-systemd-persist
```
