# Challenge — lfcs-firewall-ufw

## Mission

Ouvre `http` et active ufw, en gardant SSH joignable.

## Objectif (état attendu)

1. ufw est `active` (`ufw status`).
2. `http` / `80/tcp` est autorisé.
3. `OpenSSH` est toujours autorisé.

## Contraintes

- **Ne retire jamais `OpenSSH`** — c'est ton accès ; il est déjà autorisé.
- Utilise `ufw` (Debian), pas `firewall-cmd`.
- On lit `ufw status`.

## Validation

```bash
dsoxlab check lfcs-firewall-ufw
```
