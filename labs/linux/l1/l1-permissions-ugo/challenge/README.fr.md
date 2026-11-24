# Donner à chaque fichier les bonnes permissions

## La situation

Tout dans ton répertoire de travail est lisible par tout le monde (`0644`), ce
qui est faux pour la moitié. Un secret doit rester privé, un script doit être
exécutable, une note d'équipe doit être lisible par le groupe seulement, et il
te faut un répertoire privé. Corrige les bits de permission : ni plus, ni moins
que nécessaire.

L'idée : un mode se pose de deux manières, l'une chiffrée, l'autre symbolique,
et il se lit toujours comme trois triplets, propriétaire, groupe et autres. Le
moindre privilège, c'est accorder exactement ce qui est nécessaire, et rien de
plus.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/

## Ce qui est demandé

### Mission

Les fichiers de `challenge/work/` sont tous en `0644`. Pose les bons bits.

### Objectif

1. `secret.txt` → `0600`.
2. `deploy.sh` → `0750`.
3. `notes.txt` → `0640`.
4. `prive/` → répertoire en `0700` (à créer).

### Contraintes

- Uniquement `chmod` (et `mkdir`) : pas besoin de `sudo`, tu es propriétaire.
- La validation lit les **bits réels** via `stat`, pas la commande tapée.

### Validation

```bash
dsoxlab check l1-permissions-ugo
```
