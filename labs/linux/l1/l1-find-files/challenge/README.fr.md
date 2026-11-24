# Trouver ce qu'il faut dans une arborescence de projet

## La situation

Tu as reçu `projet.tar.gz`, un petit répertoire de projet. Sans ouvrir les
fichiers un par un, utilise **`find`** pour localiser exactement ce qui compte :
les logs, les gros fichiers, et ceux aux permissions privées.

L'idée : `find` parcourt toute une arborescence, récursivement, et sait filtrer
sur autre chose que le nom. Reste à savoir quel critère demander pour chaque
question, et comment l'exprimer.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/

## Ce qui est demandé

### Mission

Extrais `projet.tar.gz` et localise des fichiers avec `find`.

### Objectif (fichiers à produire dans le work dir)

1. `logs.txt` — tous les chemins `*.log` sous `projet/`.
2. `gros.txt` — les fichiers réguliers de plus de 1000 octets.
3. `prives.txt` — les fichiers réguliers aux permissions exactement `600`.

### Contraintes

- Extrais avec `tar xpzf projet.tar.gz` (le `p` conserve les permissions).
- Utilise `find` (un sous-shell/éditeur n'aide pas). `-type f` restreint aux
  fichiers.
- On lit le contenu des fichiers et on recalcule chaque liste depuis l'arbre réel
  `projet/` : l'ordre importe peu mais l'ensemble des chemins doit être exact.

### Validation

```bash
dsoxlab check l1-find-files
```
