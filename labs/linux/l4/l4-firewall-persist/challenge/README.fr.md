# Challenge — l4-firewall-persist

## Mission

Ouvre `http` à travers firewalld pour que ça survive au reload et au reboot.
Garde `ssh` ouvert.

## Objectif (état attendu)

1. `http` dans `firewall-cmd --list-services` (runtime).
2. `http` dans `firewall-cmd --permanent --list-services` (persistance reboot).
3. `ssh` toujours autorisé.

## Contraintes

- **Ne retire jamais `ssh`** — c'est ton accès de gestion.
- On lit la config runtime et permanente de firewalld, pas ton historique.

## Validation

```bash
dsoxlab check l4-firewall-persist
```
