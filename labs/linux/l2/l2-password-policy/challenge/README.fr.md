# Challenge — l2-password-policy

## Mission

Durcis la politique de mots de passe sur la VM (compte `bob` + défauts système).

## Objectif (état attendu)

1. `bob` : âge **max 60**, **min 7**, **avertissement 7** (`chage -l bob`).
2. `PASS_MAX_DAYS 60` dans `/etc/login.defs`.
3. `minlen = 12` (≥ 12) dans `/etc/security/pwquality.conf`.

## Contraintes

- `chage` pour le compte, édition de `/etc/login.defs` et `pwquality.conf` pour
  les défauts. La validation lit l'**état réel** (`chage -l`, contenu des fichiers).

## Validation

```bash
dsoxlab check l2-password-policy
```
