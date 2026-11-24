# Apprendre un nouveau dépôt à dnf

## La situation

Les logiciels viennent de quelque part. Quand un paquet n'est pas dans les dépôts
par défaut, il faut apprendre à `dnf` où le chercher, en lui déclarant un dépôt
supplémentaire. Fais-le bien : un identifiant clair, une vraie `baseurl`, le
dépôt activé, et **vérifié GPG** pour que les paquets soient authentifiés.

L'idée : un dépôt se décrit dans un fichier de configuration au format INI, une
`[section]` par dépôt. La vérification des signatures est le défaut de sécurité :
on ne la désactive pas pour se simplifier la vie. Reste à trouver où déposer ce
fichier, et comment demander à dnf de confirmer qu'il a bien pris le dépôt en
compte.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

## Ce qui est demandé

### Mission

Déclare un dépôt `labrepo` sous `/etc/yum.repos.d/`.

### Objectif (état attendu)

1. `/etc/yum.repos.d/labrepo.repo` définit une section `[labrepo]`.
2. Une `baseurl` http(s) valide.
3. `enabled=1`.
4. `gpgcheck=1` (avec `gpgkey`).
5. `dnf repolist --all` liste `labrepo`.

### Contraintes

- Fichier INI, une `[section]` par dépôt ; ne retire pas `gpgcheck`. La
  validation **parse le fichier** et interroge `dnf repolist`.

### Validation

```bash
dsoxlab check l2-repo-configure
```
