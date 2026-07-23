# Lab — lire et décoder une commande

## Rappel

[**Anatomie d'une commande Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/anatomie-commande/)

Toute commande Linux suit le même schéma : `commande [options] [arguments]`.
La **commande** est le programme à exécuter, les **options** modifient son
comportement, les **arguments** disent sur quoi elle agit. Le guide en tire une
promesse : comprendre cette structure, c'est pouvoir lire **toutes** les
commandes que vous rencontrerez, sans les apprendre par cœur. Ce lab ajoute ce
que la structure seule ne dit pas : que le shell transforme votre ligne
**avant** que la commande ne la voie, et qu'une ligne de synopsis se lit comme
une notation, pas comme une phrase.

Interroger la documentation (`--help`, `man`, `apropos`, `type`) est traité dans
le lab voisin `l1-get-help` : rien de tout cela n'est repris ici.

## Le cours

Les exemples ci-dessous travaillent dans `/tmp/cours-l1-anatomie`, un petit
décor que vous fabriquez vous-même et que vous jetterez à la fin. Le challenge,
lui, porte sur d'autres fichiers et d'autres commandes : le but est d'apprendre
à décomposer une ligne, pas de recopier la solution.

Toutes les sorties reproduites ici ont été relevées sur **Ubuntu 24.04.2 LTS**
avec `GNU bash, version 5.2.21(1)-release` et `coreutils 9.4`, **sans un seul
`sudo`** : tout se passe dans `/tmp`, où votre compte peut écrire. La machine
est en locale française, d'où les dates de la forme `juil. 22 18:43`. Le
comportement décrit est celui de **bash** : d'autres shells (zsh notamment)
traitent différemment certains des cas ci-dessous, c'est signalé quand ça
compte. Plantez le décor :

```bash
mkdir -p /tmp/cours-l1-anatomie/bilans
cd /tmp/cours-l1-anatomie
printf 'lundi\nmardi\nmercredi\njeudi\nvendredi\nsamedi\ndimanche\n' > journal-01.log
printf 'janvier\nfevrier\nmars\n' > journal-02.log
printf 'note interne\n' > rapport.md
touch bilans/.cache-vide
```

### Les trois parties, et l'ordre qui compte

`ls -l journal-01.log` répond
`-rw-rw-r-- 1 student student 52 juil. 22 18:43 journal-01.log`, et cette ligne se
décompose en trois blocs :

```text
  ls          -l          journal-01.log
  ──          ──          ──────────────
  │           │                 │
  │           │                 └─ argument : ce sur quoi on agit
  │           └─ option : comment on le fait (format détaillé)
  └─ commande : le programme lancé
```

Ces trois blocs sont séparés par des **espaces**, et c'est le shell qui découpe
la ligne dessus. Une commande ne reçoit donc pas une phrase : elle reçoit une
**liste de mots**. Tout ce qui suit découle de là.

L'ordre des options entre elles n'a aucune importance, et le shell ne les
réordonne pas : c'est la commande qui les traite toutes avant d'agir. Les trois
lignes suivantes donnent la même sortie :

```bash
ls -l -a bilans
ls -a -l bilans
ls -al bilans
```

```text
total 8
drwxrwxr-x 2 student student 4096 juil. 22 18:43 .
[...]
-rw-rw-r-- 1 student student    0 juil. 22 18:43 .cache-vide
```

L'ordre des **arguments**, lui, compte presque toujours, parce que chaque
position a un rôle. `grep` attend le motif en premier, les fichiers ensuite :
inversez-les, et `grep journal-01.log mardi` répond
`grep: mardi: No such file or directory`. Le motif cherché est devenu
`journal-01.log` et `mardi` a été pris pour un nom de fichier. La commande n'a
rien deviné : elle a lu les mots dans l'ordre.

Dernier point, spécifique aux outils GNU : `ls bilans -la` fonctionne, options
après l'argument, alors que la norme POSIX voudrait que `-la` soit pris pour un
nom de fichier. C'est vérifiable en rebasculant `ls` en mode POSIX :
`POSIXLY_CORRECT=1 ls bilans -la` répond
`ls: cannot access '-la': No such file or directory`. Gardez donc l'ordre
canonique du guide : options d'abord, arguments ensuite.

### Options courtes, longues, regroupées, à valeur

Une option courte est un tiret et **une lettre** (`-l`), une option longue deux
tirets et **un mot** (`--all`). Les courtes se regroupent derrière un seul
tiret : `-la` vaut exactement `-l -a`, comme la section précédente l'a montré.
Les longues ne se regroupent jamais.

Certaines options attendent une **valeur**. Il existe quatre écritures, et elles
sont équivalentes :

```bash
head -n 2 journal-01.log      # court, valeur séparée
head -n2 journal-01.log       # court, valeur collée
head --lines=2 journal-01.log # long, avec le signe égal
head --lines 2 journal-01.log # long, valeur séparée
```

```text
lundi
mardi
```

Une option à valeur **consomme le mot suivant**, quel qu'il soit. Oubliez la
valeur et c'est le nom de fichier qui la remplace : `head -n journal-01.log`
répond `head: invalid number of lines: ‘journal-01.log’`.

Même règle dans un groupe : l'option à valeur doit être la **dernière** du
paquet, sinon tout ce qui la suit est avalé comme valeur. Ainsi
`head -vn2 journal-01.log` affiche bien les deux premières lignes, précédées de
`==> journal-01.log <==` ; les mêmes lettres dans l'autre ordre,
`head -n2v journal-01.log`, répondent `head: invalid number of lines: ‘2v’`.

> **Aucune option n'est universelle.** Le guide insiste sur ce point, et les
> aides le confirment : `-r` vaut `--recursive` pour `grep`, mais `--reverse`
> pour `sort`. De même `--lines=2`, que `head` comprend, fait répondre
> `ls: unrecognized option '--lines=2'`. Chaque commande définit les siennes.

### `--` : la fin des options

Le shell découpe la ligne en mots, et la commande décide ensuite quels mots sont
des options : ceux qui commencent par un tiret. Un fichier dont le nom commence
par un tiret devient donc illisible. Fabriquez-en un :

```bash
printf 'contenu piege\n' > ./-journal.log
head -n1 -journal.log
```

```text
head: invalid option -- 'j'
Try 'head --help' for more information.
```

`head` n'a pas cherché de fichier : il a lu `-journal.log` comme le groupe
d'options `-j -o -u -r ...` et s'est arrêté sur la première inconnue. Deux
solutions, toutes deux valables :

```bash
head -n1 -- -journal.log   # -- : tout ce qui suit est un argument
head -n1 ./-journal.log    # le nom ne commence plus par un tiret
```

```text
contenu piege
contenu piege
```

Le cas le plus dangereux est celui d'un fichier nommé `-f`, parce que
`rm` connaît cette option. Le guide annonce une erreur ; la machine fait pire :

```bash
mkdir piege && cd piege
touch ./-f
rm -f
echo "code retour = $?"
ls
```

```text
code retour = 0
-f
```

Aucun message, un code retour `0`, et le fichier **toujours là** : `rm -f` a été
compris comme « supprime, sans rien demander, aucun fichier ». Une commande qui
échoue en silence coûte plus cher qu'une commande qui refuse. `rm -- -f` le
supprime pour de bon (`ls -A` ne renvoie plus rien) ; revenez ensuite au décor
avec `cd ..`. Avec une lettre inconnue de `rm`, le message est d'ailleurs très
bien fait : `rm -x` répond `rm: invalid option -- 'x'`, puis
`Try 'rm ./-x' to remove the file '-x'.`

### Ce que le shell fait avant que la commande démarre

C'est le point que la structure `commande [options] [arguments]` cache : la ligne
que vous tapez n'est **pas** celle que la commande reçoit. Le shell la
transforme d'abord. `echo` permet de tout observer sans rien casser, puisqu'il
se contente d'afficher les mots qu'on lui donne.

```bash
echo *.log
echo "*.log"
echo '*.log'
```

```text
journal-01.log journal-02.log -journal.log
*.log
*.log
```

Le joker `*` est développé par le **shell**, pas par la commande : `echo` n'a
jamais vu d'étoile, il a reçu trois mots. Entre guillemets, simples ou doubles,
l'étoile n'est plus un joker et le mot passe tel quel.

Conséquence directe, et c'est le piège du jour : le développement peut fabriquer
un argument qui commence par un tiret. `ls *.log`, commande pourtant correcte,
répond `ls: invalid option -- 'j'` : c'est `-journal.log`, ramassé par l'étoile,
qui a été lu comme des options. `ls -l -- *.log` liste bien les trois fichiers.
Pour voir ce que la commande reçoit vraiment, `set -x` affiche la ligne
**après** transformation, précédée d'un `+` :

```bash
set -x
head -n1 *.log
set +x
```

```text
+ head -n1 journal-01.log journal-02.log -journal.log
head: invalid option -- 'j'
```

Quand le motif ne correspond à **aucun** fichier, bash ne le développe pas et
passe le motif littéral, ce qui produit un message déroutant :
`head -n1 *.csv` répond
`head: cannot open '*.csv' for reading: No such file or directory`. Le fichier
`*.csv` n'existe pas, en effet : personne n'a jamais demandé à `head` de
comprendre l'étoile. (Sous zsh, la même ligne échoue plus tôt, avec
`zsh:1: no matches found: *.csv`.)

Reste la différence entre les deux guillemets. Les **doubles** laissent le shell
remplacer les variables, les **simples** bloquent tout :

```bash
echo "$HOME"
echo '$HOME'
```

```text
/home/student
$HOME
```

Ils ont un second rôle : sans eux, les espaces multiples disparaissent au
découpage en mots. `echo bonjour     tout   le monde` affiche
`bonjour tout le monde`, la même ligne entre guillemets doubles garde ses
espaces. D'où le classique, sur un fichier dont le nom contient une espace :

```bash
printf 'brouillon\n' > "mon rapport.md"
head -n1 mon rapport.md
```

```text
head: cannot open 'mon' for reading: No such file or directory
==> rapport.md <==
note interne
```

Deux mots, donc deux arguments, donc deux fichiers demandés : `head` a affiché
le second en le coiffant de son nom, comme il le fait dès qu'il reçoit plusieurs
fichiers. `head -n1 "mon rapport.md"` répond `brouillon`.

### Lire une ligne de synopsis

La première ligne d'un `--help` (et la section `SYNOPSIS` d'une page de manuel)
n'est pas une phrase : c'est une notation, la même partout.

| Notation | Sens |
|---|---|
| `mot` en majuscules | à remplacer par votre valeur |
| `[ ]` | facultatif |
| `...` | répétable |
| `\|` | au choix, l'un **ou** l'autre |
| `or:` | une autre forme d'appel, complète |

Prenez un cas réel, la première ligne de `grep --help` :

```text
Usage: grep [OPTION]... PATTERNS [FILE]...
```

Mot à mot : `grep` accepte **zéro, une ou plusieurs** options (`[OPTION]` entre
crochets donc facultatif, suivi de `...` donc répétable) ; puis **exactement
un** `PATTERNS`, sans crochets, donc **obligatoire** ; puis **autant de** `FILE`
**que vous voulez, y compris aucun**. Les deux prédictions se vérifient :

```bash
grep
grep mardi journal-01.log journal-02.log
```

```text
Usage: grep [OPTION]... PATTERNS [FILE]...
Try 'grep --help' for more information.
journal-01.log:mardi
```

Sans motif, `grep` refuse et vous **renvoie sa propre ligne de synopsis** : ce
message n'est pas un rejet sec, c'est la réponse à votre question. Avec deux
fichiers, il préfixe chaque résultat du nom du fichier. Comparez avec `mkdir`,
dont l'argument est obligatoire **et** répétable (`DIRECTORY...`, sans
crochets) : `mkdir` seul répond `mkdir: missing operand`, tandis que
`mkdir -p bilans/2024 bilans/2025` crée les deux.

La barre verticale et les formes multiples se lisent sur les deux premières
lignes de `date --help` :

```text
Usage: date [OPTION]... [+FORMAT]
  or:  date [-u|--utc|--universal] [MMDDhhmm[[CC]YY][.ss]]
```

Deux usages distincts : afficher la date, ou la régler. Dans le second,
`-u|--utc|--universal` annonce trois écritures d'une même option, et
`[MMDDhhmm[[CC]YY][.ss]]` des crochets **imbriqués** : le siècle, l'année et les
secondes sont chacun facultatifs à l'intérieur d'un argument lui-même
facultatif. La barre verticale se vérifie en une ligne :
`date -u +%H:%M`, `date --utc +%H:%M` et `date --universal +%H:%M` ont répondu
`16:37` toutes les trois.

### Dépannage

Un dernier réflexe avant le tableau : `echo $?` donne le code de retour de la
dernière commande. Le guide en donne la liste ; les quatre que vous croiserez
sont `0` (succès), `1` (erreur), `2` (mauvaise utilisation) et `127` (commande
introuvable).

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `invalid option -- 'x'` sur une commande correcte | un argument commence par un tiret | relancer avec `--` avant les arguments |
| `command not found`, code `127` | faute de frappe ou paquet absent | vérifier l'orthographe, puis `type` |
| `No such file or directory` sur un nom que vous voyez | espace dans le nom, ou chemin faux | encadrer l'argument de guillemets |
| `invalid number of lines: 'fichier'` | option à valeur sans sa valeur | remettre la valeur juste après l'option |
| une commande agit sur plus de fichiers que prévu | un joker a été développé par le shell | rejouer la ligne avec `echo` devant |
| `cannot open '*.ext'` | le joker n'a rien trouvé, le motif est passé tel quel | vérifier avec `ls` que des fichiers existent |
| la commande ne fait rien et rend `0` | l'argument a été pris pour une option | `set -x` pour voir la ligne réelle |

Pour finir, effacez le décor :

```bash
cd ~ && rm -rf /tmp/cours-l1-anatomie
```
