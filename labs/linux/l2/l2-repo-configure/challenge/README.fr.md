# Challenge — l2-repo-configure

## Mission

Déclare un dépôt `labrepo` sous `/etc/yum.repos.d/`.

## Objectif (état attendu)

1. `/etc/yum.repos.d/labrepo.repo` définit une section `[labrepo]`.
2. Une `baseurl` http(s) valide.
3. `enabled=1`.
4. `gpgcheck=1` (avec `gpgkey`).
5. `dnf repolist --all` liste `labrepo`.

## Contraintes

- Fichier INI, une `[section]` par dépôt ; ne retire pas `gpgcheck`. La
  validation **parse le fichier** et interroge `dnf repolist`.

## Validation

```bash
dsoxlab check l2-repo-configure
```
