# Contexte — un fichier d'environnement par projet

Les vrais projets livrent un fichier d'environnement qu'on `source` pour tout
mettre en place d'un coup : quelques variables, une construite à partir d'une
autre, et un `bin/` local placé en tête de `PATH` pour que ses outils priment.
Écris ce fichier.

Ta mission — écris `env.sh` dans le répertoire de travail pour qu'une fois sourcé
(`source env.sh`) :

1. `PROJET` soit exporté et vaille `dsoxlab` ;
2. `EDITOR` soit exporté et vaille `vim` ;
3. `GREETING` réutilise `PROJET` : sa valeur est `Bienvenue sur dsoxlab` ;
4. `PATH` commence par `$PWD/bin` (le `bin/` du projet passe en premier).

L'idée : `export NOM=valeur` publie une variable vers les processus enfants, une
variable peut être construite à partir d'une autre (`"...$PROJET"`), et préfixer
`PATH` (`export PATH="$PWD/bin:$PATH"`) donne la priorité aux outils locaux. Les
tests sourcent ton fichier dans un sous-shell et lancent même un processus enfant
pour confirmer que les variables sont réellement exportées.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/
