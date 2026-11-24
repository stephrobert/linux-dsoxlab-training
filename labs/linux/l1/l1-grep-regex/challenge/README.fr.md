# Lire un journal d'accès avec grep seul

## La situation

Tu as `acces.log`, dix lignes de la forme `IP - METHODE /chemin CODE`. Avec
uniquement `grep` et des expressions régulières, extrais quatre faits précis
dans des fichiers séparés : les erreurs serveur, tout ce qui n'est pas un
succès, les adresses IP distinctes, et le nombre de requêtes POST.

L'idée : le même fichier livre quatre faits différents selon la façon dont on
l'interroge. Sélectionner des lignes, les exclure, n'extraire qu'une portion de
ligne, ou ne rendre qu'un nombre, sont quatre usages distincts d'un seul outil.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/regex-base/

## Ce qui est demandé

### Mission

À partir de `acces.log` (dans `challenge/work/`), produis quatre fichiers avec
`grep` et des expressions régulières.

### Objectif (fichiers à produire)

1. `erreurs5xx.txt` — uniquement les lignes dont le **code HTTP est 5xx**.
2. `sans-200.txt` — toutes les lignes **sauf** les `200`.
3. `ips.txt` — les **IP distinctes**, triées.
4. `nb-post.txt` — le **nombre** de requêtes POST.

### Contraintes

- Uniquement `grep` (et `sort -u` pour dédoublonner les IP) : pas d'éditeur.
- La validation lit le **contenu réel** des fichiers, pas la commande tapée, et
  recalcule chaque attendu depuis `acces.log`.

### Validation

```bash
dsoxlab check l1-grep-regex
```
