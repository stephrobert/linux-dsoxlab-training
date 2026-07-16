# Challenge — lfcs-package-apt

## Mission

Installe et fige un paquet Debian avec apt.

## Objectif (état attendu)

1. `tree` est installé.
2. `tree` est figé (`apt-mark showhold` le liste).
3. `dpkg -S /usr/bin/tree` renvoie `tree`.

## Contraintes

- Utilise `apt`/`dpkg` (outillage Debian), pas `dnf`.
- On lit l'état du paquet et la liste des holds.

## Validation

```bash
dsoxlab check lfcs-package-apt
```
