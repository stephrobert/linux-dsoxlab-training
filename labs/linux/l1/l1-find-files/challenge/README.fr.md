# Challenge — l1-find-files

## Mission

Extrais `projet.tar.gz` et localise des fichiers avec `find`.

## Objectif (fichiers à produire dans le work dir)

1. `logs.txt` — tous les chemins `*.log` sous `projet/`.
2. `gros.txt` — les fichiers réguliers de plus de 1000 octets.
3. `prives.txt` — les fichiers réguliers aux permissions exactement `600`.

## Contraintes

- Extrais avec `tar xpzf projet.tar.gz` (le `p` conserve les permissions).
- Utilise `find` (un sous-shell/éditeur n'aide pas). `-type f` restreint aux
  fichiers.
- On lit le contenu des fichiers et on recalcule chaque liste depuis l'arbre réel
  `projet/` : l'ordre importe peu mais l'ensemble des chemins doit être exact.

## Validation

```bash
dsoxlab check l1-find-files
```
