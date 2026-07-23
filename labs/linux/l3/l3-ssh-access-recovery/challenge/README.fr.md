# Challenge — l3-ssh-access-recovery

## Mission

Un drop-in sshd a une directive invalide (`sshd -t` échoue). Répare avant qu'un
reload ne coupe l'accès.

## Objectif (état attendu)

1. `sshd -t` retourne 0 (config valide).
2. sshd tourne.
3. La valeur fautive (`beaucoup-trop`) a disparu.
4. `PermitRootLogin no` est **effectif** (`sshd -T`).

## Contraintes

- Corrige `/etc/ssh/sshd_config.d/99-lab.conf` (MaxAuthTries = nombre), garde
  `PermitRootLogin no`, valide avec `sshd -t`, puis `systemctl reload sshd`.
  Ne recharge jamais une config que `sshd -t` rejette.
- Supprimer le fichier n'est pas une réparation : la valeur de sécurité
  disparaîtrait avec lui.
- Garde une **seconde session SSH ouverte** pendant toute la manipulation :
  aucun compte de la VM n'a de mot de passe, donc la console série ne te
  rattraperait pas.

## Validation

```bash
dsoxlab check l3-ssh-access-recovery
```
