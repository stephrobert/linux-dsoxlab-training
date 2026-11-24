# Turn a program into a managed service

## The situation

A small program (`/usr/local/bin/labapp.sh`) needs to run as a proper **systemd
service**: started now, restarted on failure, and brought up automatically at
boot. Right now it has no unit at all.

The point: a unit file describes *how* to run something. What is left is getting
systemd to take that description into account, then telling "runs now" apart from
"comes back at the next boot": those are two distinct moves.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/systemd/services/

## What is asked

### Mission

Turn `/usr/local/bin/labapp.sh` into a managed systemd service.

### Goal (expected state)

1. A unit `/etc/systemd/system/labapp.service` with `ExecStart=/usr/local/bin/labapp.sh`.
2. Service **active** (`is-active`).
3. Service **enabled** at boot (`is-enabled`).
4. It actually ran (`/run/labapp.status` = `running`).

### Constraints

- `daemon-reload` after writing the unit, then `systemctl enable --now labapp`.
  Validation reads the service's **actual state** (not the command).

### Validation

```bash
dsoxlab check l3-service-create-unit
```
