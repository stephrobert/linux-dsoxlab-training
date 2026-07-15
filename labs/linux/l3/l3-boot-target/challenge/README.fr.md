# Challenge — l3-boot-target

## Mission

La cible de démarrage par défaut est `graphical.target`. Remets-la en serveur.

## Objectif (état attendu)

1. `systemctl get-default` → **`multi-user.target`**.

## Contraintes

- `systemctl set-default`. La validation lit la **cible réelle**, pas la commande.

## Validation

```bash
dsoxlab check l3-boot-target
```
