# Let the web service through the firewall

## The situation

A web server is about to run on this host, but `firewalld` blocks HTTP. Open the
`http` service — and make it stick after a reload and after a reboot, not just
until the firewall is next reloaded.

The point: a firewall has two states, the one that runs and the one written on
disk. A rule added live is lost at the first reload, and at reboot. In the end
**both** lists, runtime and permanent, must show `http`.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/firewalld/

## What is asked

### Mission

Open `http` through firewalld so it survives reload and reboot. Keep `ssh` open.

### Goal (expected state)

1. `http` in `firewall-cmd --list-services` (runtime).
2. `http` in `firewall-cmd --permanent --list-services` (reboot persistence).
3. `ssh` still allowed.

### Constraints

- **Never remove `ssh`** — it's your management access.
- Validation reads firewalld's runtime and permanent config, not your history.

### Validation

```bash
dsoxlab check l4-firewall-persist
```
