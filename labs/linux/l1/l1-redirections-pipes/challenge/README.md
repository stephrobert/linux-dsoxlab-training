# Challenge — l1-redirections-pipes

## Mission

À partir de `journal.log` (dans `challenge/work/`), produis quatre fichiers avec
les bons opérateurs de redirection.

## Objectif (fichiers à produire)

1. `total.txt` — le **nombre de lignes** de `journal.log`.
2. `erreurs.txt` — uniquement les lignes contenant **`ERROR`**.
3. `stderr.txt` — le **message d'erreur** d'une commande qui échoue (lis un
   fichier absent).
4. `tout.txt` — la sortie standard **et** l'erreur d'une commande, **fusionnées**.

## Contraintes

- Aucun éditeur : uniquement des redirections (`>`, `2>`, `2>&1`) et des pipes (`|`).
- La validation lit le **contenu réel** des fichiers, pas la commande tapée.

## Validation

```bash
dsoxlab check l1-redirections-pipes
```
