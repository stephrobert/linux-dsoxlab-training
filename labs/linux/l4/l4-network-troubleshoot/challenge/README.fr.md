# Challenge — l4-network-troubleshoot

## Mission

`lab-net` sur `lab1` est configurée mais morte et ne survivra pas à un reboot.
Diagnostique et rétablis-la.

## Objectif (état attendu)

1. La connexion `lab-net` est `activated` (`nmcli -g GENERAL.STATE con show lab-net`).
2. `connection.autoconnect` = `yes` (persistance reboot).
3. `lab1` porte `198.51.100.10` en live.

## Contraintes

- **Ne touche jamais à l'interface de gestion** (lien de gestion). Travaille uniquement sur `lab1`.
- On lit l'état NetworkManager et l'interface active, pas ton historique.

## Validation

```bash
dsoxlab check l4-network-troubleshoot
```
