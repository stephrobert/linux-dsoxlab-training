# Challenge — l4-ssh-key-auth-harden

## Mission

`deploy` a sa clé dans `authorized_keys` mais `sshd` la refuse — corrige le
propriétaire et les permissions.

## Objectif (état attendu)

1. L'utilisateur `deploy` existe.
2. `~deploy/.ssh` → répertoire, `0700`, détenu `deploy:deploy`.
3. `~deploy/.ssh/authorized_keys` → `0600`, détenu `deploy:deploy`, clé conservée.

## Contraintes

- Ne change pas le contenu de la clé — seuls le propriétaire et les permissions
  sont faux.
- On lit l'état du système de fichiers (`stat`), pas ton historique.

## Validation

```bash
dsoxlab check l4-ssh-key-auth-harden
```
