# Challenge — l2-acl-posix

## Mission

Accorde des accès fins par ACL sur `/srv/projet` sans toucher au propriétaire ni
aux droits ugo.

## Objectif (état attendu)

1. `carol` a `rw` (ACL utilisateur) sur `/srv/projet/report.txt`.
2. `auditors` a `r-x` (ACL groupe) sur `/srv/projet`.
3. Une ACL **par défaut** donne `r` à `auditors` sur les futurs fichiers de `/srv/projet`.

## Contraintes

- `setfacl -m` pour ajouter, `d:` pour l'ACL par défaut. Vérifie avec `getfacl`.
- La validation lit les **ACL réelles** (`getfacl`), pas la commande tapée.

## Validation

```bash
dsoxlab check l2-acl-posix
```
