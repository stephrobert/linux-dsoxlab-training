# The Debian firewall: ufw

## The situation

On Debian/Ubuntu the friendly front-end to the firewall is **`ufw`** (Uncomplicated
FireWall). A web service must be reachable, so you'll open `http` and turn the
firewall on — while keeping your SSH way in.

The point: `ufw` is the Debian counterpart to `firewall-cmd` — same idea,
deliberately minimal syntax. The firewall has an on/off state of its own,
separate from the rules it holds: both count, and the order in which you deal
with them decides whether you keep your session or not.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/ufw/

## What is asked

### Mission

Open `http` and enable ufw, keeping SSH reachable.

### Goal (expected state)

1. ufw is `active` (`ufw status`).
2. `http` / `80/tcp` is allowed.
3. `OpenSSH` is still allowed.

### Constraints

- **Never remove `OpenSSH`** — it's your access; it's already permitted.
- Use `ufw` (Debian), not `firewall-cmd`.
- Validation reads `ufw status`.

### Validation

```bash
dsoxlab check lfcs-firewall-ufw
```
