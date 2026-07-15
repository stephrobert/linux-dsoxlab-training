# Challenge — l3-app-constraints

## Mission

Relève la limite de fichiers ouverts d'`appuser`, durablement.

## Objectif (état attendu)

1. Un drop-in `/etc/security/limits.d/` définit `nofile` pour appuser.
2. Effectif : `su - appuser -c 'ulimit -Sn'` → **4096** (souple).
3. Effectif : `su - appuser -c 'ulimit -Hn'` → **8192** (dure).

## Contraintes

- Édite `/etc/security/limits.d/appuser.conf`. La validation lit la limite
  **effective** dans une session de login (via pam_limits), pas la commande.

## Validation

```bash
dsoxlab check l3-app-constraints
```
