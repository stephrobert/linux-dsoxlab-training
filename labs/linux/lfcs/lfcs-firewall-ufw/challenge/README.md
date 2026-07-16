# Challenge — lfcs-firewall-ufw

## Mission

Open `http` and enable ufw, keeping SSH reachable.

## Goal (expected state)

1. ufw is `active` (`ufw status`).
2. `http` / `80/tcp` is allowed.
3. `OpenSSH` is still allowed.

## Constraints

- **Never remove `OpenSSH`** — it's your access; it's already permitted.
- Use `ufw` (Debian), not `firewall-cmd`.
- Validation reads `ufw status`.

## Validation

```bash
dsoxlab check lfcs-firewall-ufw
```
