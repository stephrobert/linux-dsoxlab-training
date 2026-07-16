# Challenge — l2-collaborative-setgid

## Mission

Fais de `/srv/partage` un répertoire collaboratif pour le groupe `devteam` avec le
bit set-GID.

## Objectif (état attendu)

1. `/srv/partage` est un répertoire de groupe `devteam`.
2. Son mode est `2775` (set-GID + `rwxrwxr-x`).
3. Un fichier créé dedans par un membre de `devteam` hérite du groupe `devteam`.

## Contraintes

- Le groupe `devteam` et les membres `alice`/`bob` existent déjà.
- On lit le mode/groupe du répertoire et on crée un fichier témoin en tant
  qu'`alice` pour vérifier le groupe hérité.

## Validation

```bash
dsoxlab check l2-collaborative-setgid
```
