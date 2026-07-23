# Lab — chemins absolus et relatifs

## Rappel

[**Chemins absolus et relatifs sous Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/chemins-linux/)

Toute commande qui touche un fichier doit d'abord savoir où il se trouve. Un
chemin **absolu** commence par `/` : il part de la racine et désigne le même
emplacement quel que soit l'endroit d'où vous le tapez. Un chemin **relatif**
ne commence pas par `/` : le shell le résout à partir du répertoire courant,
celui que `pwd` affiche. Quatre notations complètent l'écriture des chemins :
`.` (ici), `..` (le répertoire parent), `~` (votre répertoire personnel) et `-`
(le répertoire précédent, avec `cd` uniquement).

## Le cours

Les exemples ci-dessous travaillent dans `/tmp/cours-l1-paths`, une petite
arborescence que vous fabriquez vous-même et que vous jetterez à la fin : le
challenge, lui, portera sur d'autres répertoires et d'autres fichiers. Le but
est d'apprendre à lire et à écrire un chemin, pas de recopier une ligne.

Toutes les sorties reproduites ici ont été obtenues avec
`GNU bash, version 5.2.21(1)-release` et `realpath (GNU coreutils) 9.4`.

### Le décor de démonstration

Fabriquez l'arborescence. Aucune commande de cette section n'a besoin de
`sudo` : tout se passe dans `/tmp`, où votre compte peut écrire.

```bash
mkdir -p /tmp/cours-l1-paths/atelier/notes
mkdir -p /tmp/cours-l1-paths/atelier/outils
mkdir -p /tmp/cours-l1-paths/atelier/archives/2019
echo 'Memo du mardi.' > /tmp/cours-l1-paths/atelier/notes/memo.txt
echo 'Bilan 2019.'    > /tmp/cours-l1-paths/atelier/archives/2019/bilan.md
find /tmp/cours-l1-paths | sort
```

```text
/tmp/cours-l1-paths
/tmp/cours-l1-paths/atelier
/tmp/cours-l1-paths/atelier/archives
/tmp/cours-l1-paths/atelier/archives/2019
/tmp/cours-l1-paths/atelier/archives/2019/bilan.md
/tmp/cours-l1-paths/atelier/notes
/tmp/cours-l1-paths/atelier/notes/memo.txt
/tmp/cours-l1-paths/atelier/outils
```

Chaque ligne de cette sortie est un chemin absolu : elle commence par `/`.

### Absolu ou relatif : la différence se mesure

Un chemin relatif ne veut rien dire tant qu'on ne sait pas d'où on le tape. La
même commande, lancée depuis deux répertoires différents, ne fait donc pas la
même chose. Voici la démonstration.

```bash
cd /tmp/cours-l1-paths/atelier/notes
pwd
cat memo.txt
cd /tmp/cours-l1-paths/atelier/outils
pwd
cat memo.txt
```

```text
/tmp/cours-l1-paths/atelier/notes
Memo du mardi.
/tmp/cours-l1-paths/atelier/outils
cat: memo.txt: No such file or directory
```

Le fichier n'a pas bougé et la commande n'a pas changé d'une lettre. Seul
`pwd` a changé, et cela suffit à la faire échouer.

Le chemin absolu, lui, ne dépend de rien. Même depuis la racine :

```bash
cd /
pwd
cat /tmp/cours-l1-paths/atelier/notes/memo.txt
```

```text
/
Memo du mardi.
```

### `..`, le répertoire parent

`..` remonte d'un niveau. On le chaîne autant de fois que nécessaire, et on
peut redescendre dans la foulée. Chaque `cd` est suivi d'un `pwd` pour voir où
l'on a atterri :

```bash
cd /tmp/cours-l1-paths/atelier/notes
pwd
cd ..
pwd
cd ..
pwd
```

```text
/tmp/cours-l1-paths/atelier/notes
/tmp/cours-l1-paths/atelier
/tmp/cours-l1-paths
```

En une seule commande, on remonte puis on redescend dans une autre branche :

```bash
cd /tmp/cours-l1-paths/atelier/notes
cd ../archives/2019
pwd
```

```text
/tmp/cours-l1-paths/atelier/archives/2019
```

Lisez `../archives/2019` de gauche à droite : remonter dans `atelier`, puis
descendre dans `archives`, puis dans `2019`. C'est exactement le raisonnement
qu'on fait pour construire un chemin relatif entre deux points.

Un cas particulier à connaître : **la racine n'a pas de parent**. `cd ..`
depuis `/` ne produit ni erreur ni déplacement.

```bash
cd /
pwd
cd ..
pwd
```

```text
/
/
```

### `.`, `~` et `-`

`.` désigne le répertoire courant. Son usage le plus fréquent est de servir de
destination : « copie ce fichier ici ».

```bash
cd /tmp/cours-l1-paths/atelier/notes
pwd
cp /tmp/cours-l1-paths/atelier/archives/2019/bilan.md .
ls
```

```text
/tmp/cours-l1-paths/atelier/notes
bilan.md
memo.txt
```

`~` est remplacé par votre répertoire personnel, quel que soit l'endroit où
vous êtes. Il vaut la même chose que la variable `$HOME` :

```bash
cd /tmp/cours-l1-paths/atelier/outils
echo "$HOME"
cd ~
pwd
```

```text
/home/student
/home/student
```

Sur la machine qui a produit cette sortie, l'utilisateur s'appelle `student` :
chez vous, `pwd` affichera votre propre répertoire personnel.

Le tiret `-` ramène au dernier répertoire visité, et `cd -` affiche au passage
le répertoire où il vous emmène :

```bash
cd /tmp/cours-l1-paths/atelier/archives
pwd
cd /tmp/cours-l1-paths/atelier/outils
pwd
cd -
pwd
```

```text
/tmp/cours-l1-paths/atelier/archives
/tmp/cours-l1-paths/atelier/outils
/tmp/cours-l1-paths/atelier/archives
/tmp/cours-l1-paths/atelier/archives
```

La troisième ligne est affichée par `cd -` lui-même, la quatrième par le `pwd`
qui suit : c'est bien le même répertoire.

### `./script` et `script` ne sont pas la même commande

C'est le seul endroit où le `.` est obligatoire plutôt que décoratif. Créez un
script et lancez-le des deux façons :

```bash
printf '#!/bin/bash\necho "script lance depuis $(pwd)"\n' \
  > /tmp/cours-l1-paths/atelier/outils/bonjour.sh
chmod +x /tmp/cours-l1-paths/atelier/outils/bonjour.sh
cd /tmp/cours-l1-paths/atelier/outils
./bonjour.sh
bonjour.sh
```

```text
script lance depuis /tmp/cours-l1-paths/atelier/outils
bash: bonjour.sh: command not found
```

`./bonjour.sh` est un chemin, le shell ouvre le fichier. `bonjour.sh` sans
préfixe est un **nom de commande** : le shell le cherche dans les répertoires
du `PATH`, et le répertoire courant n'en fait pas partie. Vérifiez-le : la
recherche ci-dessous ne renvoie aucune ligne, et le code retour 1 de `grep`
signifie « aucune correspondance ».

```bash
echo "$PATH" | tr ':' '\n' | grep -x '\.'
echo "code retour = $?"
```

```text
code retour = 1
```

> **C'est délibéré.** Si le répertoire courant était dans le `PATH`, un fichier
> nommé `ls` déposé dans un répertoire où vous passez serait exécuté à la place
> du vrai `ls`. Le `./` obligatoire rend l'intention explicite.

Ce script affiche `pwd`. Appelé par son chemin absolu depuis
`/tmp/cours-l1-paths/atelier/notes` puis depuis `/tmp`, il répond
`script lance depuis /tmp/cours-l1-paths/atelier/notes`, puis
`script lance depuis /tmp`. Tout chemin relatif écrit à l'intérieur se
résoudrait donc à deux endroits différents selon l'appel : c'est pourquoi le
guide recommande les chemins absolus dans les scripts.

### Savoir où l'on est vraiment : `pwd -P` et `realpath`

Ajoutez un lien symbolique et entrez dedans :

```bash
ln -s atelier/notes /tmp/cours-l1-paths/raccourci
cd /tmp/cours-l1-paths/raccourci
pwd
pwd -P
```

```text
/tmp/cours-l1-paths/raccourci
/tmp/cours-l1-paths/atelier/notes
```

`pwd` affiche le chemin **logique**, celui par lequel vous êtes arrivé. `pwd -P`
affiche le chemin **physique**, liens résolus. Tant qu'aucun lien n'est traversé,
les deux sont identiques ; ici ils divergent.

Conséquence directe, et piège classique : `cd ..` suit le chemin logique.

```bash
cd ..
pwd
```

```text
/tmp/cours-l1-paths
```

Vous remontez dans le parent du **lien**, pas dans celui du répertoire réel.
Pour raisonner en physique, entrez avec `cd -P /tmp/cours-l1-paths/raccourci` :
le `cd ..` suivant mène alors à `/tmp/cours-l1-paths/atelier`.

`realpath` fait le travail inverse de ce que vous faites de tête : il traduit
un chemin relatif en chemin absolu, en tenant compte du répertoire courant.

```bash
cd /tmp/cours-l1-paths/atelier/notes
realpath memo.txt
cd /tmp/cours-l1-paths/atelier/outils
realpath memo.txt
```

```text
/tmp/cours-l1-paths/atelier/notes/memo.txt
/tmp/cours-l1-paths/atelier/outils/memo.txt
```

Deux réponses différentes pour le même argument : c'est la définition même
d'un chemin relatif. La seconde concerne d'ailleurs un fichier qui n'existe
pas, et `realpath` répond quand même : il calcule le chemin sans exiger la
cible. Ajoutez `-e` pour qu'il refuse un chemin inexistant (`realpath -e
memo.txt` renvoie alors `realpath: memo.txt: No such file or directory` et un
code retour de 1).

`readlink -f` donne le même résultat et résout en plus les liens symboliques,
là où `realpath -s` s'en abstient :

```bash
cd /tmp/cours-l1-paths
readlink -f raccourci
realpath -s raccourci
```

```text
/tmp/cours-l1-paths/atelier/notes
/tmp/cours-l1-paths/raccourci
```

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `cat: fichier: No such file or directory` sur un chemin relatif | vous n'êtes pas dans le répertoire que vous croyez | `pwd`, puis retenter en absolu |
| `cat: /chemin/…: No such file or directory` sur un chemin absolu | faute de frappe dans le chemin | complétez avec **Tab**, ou `ls` sur le répertoire parent |
| `bash: commande: command not found` pour un script local | le répertoire courant n'est pas dans le `PATH` | préfixez par `./` |
| `bash: ./script.sh: Permission denied` | le script n'est pas exécutable | `ls -l script.sh`, puis `chmod +x script.sh` |
| `bash: cd: notes/memo.txt: Not a directory` | vous avez donné un fichier à `cd` | `ls -ld` sur la cible |
| `pwd` et `pwd -P` ne disent pas la même chose | vous avez traversé un lien symbolique | `ls -l` sur le maillon suspect |
| `~` n'est pas interprété dans un script | tilde entre guillemets | utilisez `$HOME` |

Pour tout effacer et repartir de zéro, un seul chemin absolu suffit :

```bash
cd ~
rm -rf /tmp/cours-l1-paths
```
