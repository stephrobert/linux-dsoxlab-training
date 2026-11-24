# Donner du mordant à la politique de mots de passe

## La situation

Des mots de passe qui n'expirent jamais et peuvent tenir en un caractère, c'est
un constat d'audit assuré. Durcis la politique à trois niveaux : le compte
existant, le défaut système pour les nouveaux comptes, et la règle de complexité.

L'idée : ces trois niveaux ne se règlent pas au même endroit. L'expiration d'un
compte déjà créé, les valeurs héritées par les comptes créés ensuite et la
complexité exigée à la saisie relèvent de trois mécanismes distincts, qu'il faut
identifier avant de toucher au premier.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

## Ce qui est demandé

### Mission

Durcis la politique de mots de passe sur la VM (compte `bob` + défauts système).

### Objectif (état attendu)

1. `bob` : âge **max 60**, **min 7**, **avertissement 7** (`chage -l bob`).
2. `PASS_MAX_DAYS 60` dans `/etc/login.defs`.
3. `minlen = 12` (≥ 12) dans `/etc/security/pwquality.conf`.

### Contraintes

- `chage` pour le compte, édition de `/etc/login.defs` et `pwquality.conf` pour
  les défauts. La validation lit l'**état réel** (`chage -l`, contenu des fichiers).

### Validation

```bash
dsoxlab check l2-password-policy
```
