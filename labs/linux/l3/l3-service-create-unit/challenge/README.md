# Challenge — l3-service-create-unit

## Mission

Turn `/usr/local/bin/labapp.sh` into a managed systemd service.

## Goal (expected state)

1. A unit `/etc/systemd/system/labapp.service` with `ExecStart=/usr/local/bin/labapp.sh`.
2. Service **active** (`is-active`).
3. Service **enabled** at boot (`is-enabled`).
4. It actually ran (`/run/labapp.status` = `running`).

## Constraints

- `daemon-reload` after writing the unit, then `systemctl enable --now labapp`.
  Validation reads the service's **actual state** (not the command).

## Validation

```bash
dsoxlab check l3-service-create-unit
```
