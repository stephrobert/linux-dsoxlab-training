# Amener la machine à l'état logiciel cible

## La situation

Gérer les logiciels, c'est le quotidien : installer ce dont un service a besoin,
retirer ce qui ne doit pas être là, et savoir prouver le résultat. Là, `zip` est
installé mais indésirable, et `tree` manque mais est nécessaire.

L'idée : le gestionnaire de paquets change l'état logiciel de la machine et
résout les dépendances au passage ; la base RPM en garde la trace. Les tests
lisent cette base : c'est l'état réel de la machine qui compte, pas la commande
tapée.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

## Ce qui est demandé

### Mission

Amène la machine à l'état logiciel cible.

### Objectif (état attendu)

1. Le paquet **`tree`** est **installé**.
2. Le paquet **`zip`** est **retiré**.
3. La commande `tree` est disponible.

### Contraintes

- `dnf install` / `dnf remove` ; vérifie avec `rpm -q`. La validation lit la
  **base RPM** (état réel), pas la commande tapée.

### Validation

```bash
dsoxlab check l2-package-management
```
