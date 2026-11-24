# Un fichier d'environnement par projet

## La situation

Les vrais projets livrent un fichier d'environnement qu'on `source` pour tout
mettre en place d'un coup : quelques variables, une construite à partir d'une
autre, et un `bin/` local placé en tête de `PATH` pour que ses outils priment.
Écris ce fichier.

Le contrat, celui que les tests vérifient : `env.sh`, dans le répertoire de
travail, une fois sourcé (`source env.sh`), laisse l'environnement dans cet
état :

1. `PROJET` est exporté et vaut `dsoxlab` ;
2. `EDITOR` est exporté et vaut `vim` ;
3. `GREETING` réutilise `PROJET` : sa valeur est `Bienvenue sur dsoxlab` ;
4. `PATH` commence par `$PWD/bin`, le `bin/` du projet passant en premier.

L'idée : une variable n'existe pour les processus enfants que si elle leur est
publiée, et l'ordre de `PATH` décide quel binaire gagne quand deux portent le
même nom. Les tests sourcent ton fichier dans un sous-shell et lancent un
processus enfant pour confirmer que les variables sont réellement exportées.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/

## Ce qui est demandé

### Mission

Écris `env.sh` dans `challenge/work/`. Une fois sourcé, il configure
l'environnement du projet.

### Contrat (après `source env.sh`)

1. `PROJET` exporté = `dsoxlab`.
2. `EDITOR` exporté = `vim`.
3. `GREETING` = `Bienvenue sur dsoxlab` (construit à partir de `$PROJET`).
4. `PATH` commence par `$PWD/bin`.

### Contraintes

- `export` pour publier les variables, `$PWD/bin` en tête de `PATH`.
- La validation **source** ton fichier dans un sous-shell et lance un enfant pour
  vérifier l'export réel. Ne touche pas à ton vrai `~/.bashrc`.

### Validation

```bash
dsoxlab check l1-env-profiles
```
