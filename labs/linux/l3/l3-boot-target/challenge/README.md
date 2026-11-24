# A server should boot headless

## The situation

Someone left this machine defaulting to a **graphical** boot target — pointless
on a server, and a waste of resources. Bring it back to a text multi-user boot.

The point: systemd **targets** are boot states; `multi-user.target` is the
standard server state (networking + services, no GUI), `graphical.target` adds a
display manager. The system marks one of them as the default target, and that
designation, and only that, is what survives a reboot.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/reboot-shutdown/

## What is asked

### Mission

The default boot target is `graphical.target`. Set it back to server.

### Goal (expected state)

1. `systemctl get-default` → **`multi-user.target`**.

### Constraints

- `systemctl set-default`. Validation reads the **actual target**, not the command.

### Validation

```bash
dsoxlab check l3-boot-target
```
