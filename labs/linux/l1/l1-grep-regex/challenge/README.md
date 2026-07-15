# Challenge — l1-grep-regex

## Mission

À partir de `acces.log` (dans `challenge/work/`), produis quatre fichiers avec
`grep` et des expressions régulières.

## Objectif (fichiers à produire)

1. `erreurs5xx.txt` — uniquement les lignes dont le **code HTTP est 5xx**.
2. `sans-200.txt` — toutes les lignes **sauf** les `200`.
3. `ips.txt` — les **IP distinctes**, triées.
4. `nb-post.txt` — le **nombre** de requêtes POST.

## Contraintes

- Uniquement `grep` (et `sort -u` pour dédoublonner les IP) : pas d'éditeur.
- La validation lit le **contenu réel** des fichiers, pas la commande tapée, et
  recalcule chaque attendu depuis `acces.log`.

## Validation

```bash
dsoxlab check l1-grep-regex
```
