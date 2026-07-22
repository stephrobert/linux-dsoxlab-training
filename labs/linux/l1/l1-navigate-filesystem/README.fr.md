# Lab — naviguer dans le système de fichiers

## Rappel

[**Naviguer et gérer des fichiers sous Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/)

Trois commandes forment le trépied de la navigation : `pwd` dit où vous êtes,
`cd` vous déplace, `ls` montre ce qu'il y a autour. Le guide en tire une règle :
après chaque opération, vérifiez le résultat. Ce lab travaille donc autant le
regard que le déplacement : lire `ls -l` colonne par colonne, distinguer le
contenu d'un répertoire du répertoire lui-même, et savoir quoi demander à `file`
et à `stat` quand `ls` ne suffit plus.

L'écriture des chemins (`.`, `..`, `~`, absolu contre relatif) est traitée dans
le lab voisin `l1-paths-absolute-relative` : elle n'est pas reprise ici.

## Le cours

Les exemples ci-dessous travaillent dans `/tmp/cours-l1-navigate`, une petite
arborescence que vous fabriquez vous-même et que vous jetterez à la fin. Le
challenge, lui, portera sur d'autres répertoires et d'autres fichiers : le but
est d'apprendre à regarder, pas de recopier une ligne.

Toutes les sorties reproduites ici ont été obtenues sur Ubuntu 24.04 avec
`GNU bash 5.2.21(1)`, `ls (GNU coreutils) 9.4` et `file-5.45`, sans un seul
`sudo` : tout se passe dans `/tmp`, où votre compte peut écrire. La machine est
en locale française, d'où les dates de la forme `juil. 22 17:48` ; en anglais
vous lirez `Jul 22 17:48`.

### Le décor de démonstration

```bash
mkdir -p /tmp/cours-l1-navigate/bibliotheque/{catalogue,emprunts,archives/2018}
cd /tmp/cours-l1-navigate/bibliotheque
printf 'titre;auteur;annee\nLe Horla;Maupassant;1887\n' > catalogue/inventaire.csv
printf 'note courte\n'                   > catalogue/memo.md
head -c 120     /dev/urandom             > catalogue/vignette.png
head -c 74000   /dev/urandom             > catalogue/affiche.jpg
head -c 2500000 /dev/urandom             > emprunts/registre.dat
printf 'Fiche de la salle de lecture.\n' > notice.md
printf 'archive 2018\n'                  > archives/2018/bilan.txt
printf 'cache\n'                         > .horaires
ln -s catalogue/inventaire.csv dernier-inventaire
```

Pour voir l'ensemble d'un coup, le réflexe est `tree`. Encore faut-il qu'il soit
installé, ce qui n'est pas garanti : sur la machine qui a produit ce cours, il ne
l'était pas. `command -v tree` n'y affiche aucune ligne et renvoie le code retour
1, la preuve que la commande n'existe pas. `find` la remplace sans rien
installer, et il montre en prime les fichiers cachés, que `ls` sans option passe
sous silence.

```bash
cd /tmp/cours-l1-navigate
find bibliotheque | sort
```

```text
bibliotheque
bibliotheque/archives
bibliotheque/archives/2018
bibliotheque/archives/2018/bilan.txt
[...]
bibliotheque/.horaires
bibliotheque/notice.md
```

`find bibliotheque -type d` ne garde que les répertoires, `-type f` que les
fichiers. Le guide cite aussi `ls -R`, qui liste récursivement.

### `pwd` et `cd` : se situer, se déplacer

`pwd` (print working directory) affiche le répertoire courant, `cd` (change
directory) en change. Le guide donne la règle : après chaque `cd`, un `pwd`
confirme la position.

```bash
cd /tmp/cours-l1-navigate/bibliotheque/archives/2018 ; pwd
cd                                                   ; pwd
```

```text
/tmp/cours-l1-navigate/bibliotheque/archives/2018
/home/student
```

`cd` sans argument ramène dans votre répertoire personnel. Sur la machine qui a
produit cette sortie, l'utilisateur s'appelle `student` ; chez vous, `pwd` affichera
le vôtre. Une erreur revient souvent, donner un fichier à `cd` : la réponse est
alors `bash: cd: notice.md: Not a directory`, et le code retour vaut 1.

### Lire `ls -l` colonne par colonne

Sans option, `ls` ne donne que des noms. Dans un terminal il les répartit sur
plusieurs colonnes ; dès que sa sortie part dans un tube ou un fichier, il
bascule à un nom par ligne. C'est son comportement par défaut, pas un réglage.

`-l` (format long) est l'option qui fait tout le travail :

```bash
cd /tmp/cours-l1-navigate/bibliotheque
ls -l
```

```text
total 16
drwxrwxr-x 3 student student 4096 juil. 22 17:48 archives
drwxrwxr-x 2 student student 4096 juil. 22 17:48 catalogue
lrwxrwxrwx 1 student student   24 juil. 22 17:48 dernier-inventaire -> catalogue/inventaire.csv
drwxrwxr-x 2 student student 4096 juil. 22 17:48 emprunts
-rw-rw-r-- 1 student student   30 juil. 22 17:48 notice.md
```

Voici la dernière ligne, décomposée colonne par colonne :

```text
-rw-rw-r--  1  student  student  30  juil. 22 17:48  notice.md
│           │  │        │        │   │               │
│           │  │        │        │   │               └─ nom
│           │  │        │        │   └─ date de dernière modification (mtime)
│           │  │        │        └─ taille en octets
│           │  │        └─ groupe propriétaire
│           │  └─ utilisateur propriétaire
│           └─ nombre de liens
└─ type et permissions
```

Le tout premier caractère donne le **type**, et il ne fait pas partie des droits :
`-` pour un fichier ordinaire, `d` pour un répertoire, `l` pour un lien
symbolique. Les trois cas figurent ci-dessus, et le lien affiche en prime sa
cible après une flèche.

Trois valeurs se lisent de travers. La **taille** d'un répertoire (ici 4096) est
celle de l'entrée d'annuaire, pas celle de ce qu'il contient. Celle du lien vaut
24 : c'est la longueur du chemin qu'il contient, `catalogue/inventaire.csv`, soit
exactement 24 caractères. Et **`total 16`** est un total de blocs disque, pas un
nombre de fichiers.

### Les options de `ls` qui changent la vue

`-a` (all) ajoute les entrées commençant par un point : `.` (le répertoire
lui-même), `..` (son parent) et les fichiers de configuration.

```text
drwxrwxr-x 5 student student 4096 juil. 22 17:48 .              # ls -la
drwxrwxr-x 3 student student 4096 juil. 22 17:48 ..
[...]
-rw-rw-r-- 1 student student    6 juil. 22 17:48 .horaires
```

`-h` (human readable) traduit les octets en unités lisibles. La même ligne, sans
puis avec `-h`, montre que rien d'autre ne change :

```text
-rw-rw-r-- 1 student student 2500000 juil. 22 17:48 registre.dat     # ls -l  emprunts
-rw-rw-r-- 1 student student    2,4M juil. 22 17:48 registre.dat     # ls -lh emprunts
```

`-h` seul ne sert à rien : il ne s'applique qu'aux tailles affichées par `-l`.
`-S`, lui, trie par taille décroissante, et `-r` inverse n'importe quel tri
(`ls -lhSr` donnerait exactement l'ordre inverse des quatre lignes ci-dessous) :

```text
-rw-rw-r-- 1 student student 73K juil. 22 17:48 affiche.jpg     # ls -lhS catalogue
-rw-rw-r-- 1 student student 120 juil. 22 17:48 vignette.png
-rw-rw-r-- 1 student student  44 juil. 22 17:48 inventaire.csv
-rw-rw-r-- 1 student student  12 juil. 22 17:48 memo.md
```

`-t` trie par date de modification, le plus récent en premier. Combiné à `-r`, il
donne `ls -ltr`, la commande la plus utile du lot : le fichier modifié en dernier
arrive juste au-dessus de votre prompt. Modifiez-en un, regardez-le descendre :

```bash
ls -ltr
echo 'Fermeture exceptionnelle le 15.' >> notice.md
ls -ltr
```

```text
[...]
-rw-rw-r-- 1 student student   30 juil. 22 17:48 notice.md   <- avant : 3e ligne sur 5
[...]
-rw-rw-r-- 1 student student   62 juil. 22 17:49 notice.md   <- apres : dernière ligne
```

### `ls -l` contre `ls -ld` : le contenu ou le répertoire lui-même

C'est le piège qui déroute tout le monde. Donnez un répertoire à `ls -l` : il
liste ce qu'il y a **dedans**. Ajoutez `-d` (directory) : il décrit le répertoire
**lui-même**.

```bash
ls -l  archives
ls -ld archives
```

```text
total 4
drwxrwxr-x 2 student student 4096 juil. 22 17:48 2018       <- le CONTENU de archives
drwxrwxr-x 3 student student 4096 juil. 22 17:48 archives   <- archives LUI-MEME
```

C'est donc `ls -ld` qu'il faut employer dès qu'on veut vérifier les droits ou le
propriétaire d'un répertoire : sans `-d`, on lit ceux de son contenu et l'on
conclut à l'envers. La différence va plus loin qu'un affichage : lister le
contenu exige le droit de lecture sur le répertoire, le décrire n'exige rien de
lui. Sur un répertoire mis à `chmod 000`, les deux commandes divergent donc :

```text
ls: cannot open directory 'reserve': Permission denied   # ls -l,  rc=2
d--------- 2 student student 4096 juil. 22 17:51 reserve         # ls -ld, rc=0
```

**Le compteur de liens d'un répertoire n'est pas un nombre de fichiers.** Il vaut
2 plus le nombre de sous-répertoires : 1 pour son nom dans le parent, 1 pour son
propre `.`, et 1 par `..` de chaque sous-répertoire. Regardez-le monter :

```bash
mkdir -p /tmp/cours-l1-navigate/compteur && cd /tmp/cours-l1-navigate/compteur
ls -ld .
mkdir salle1 ; ls -ld .
mkdir salle2 ; ls -ld .
touch fichier1 fichier2 ; ls -ld .
```

```text
drwxrwxr-x 2 student student 4096 juil. 22 17:51 .   <- vide
drwxrwxr-x 3 student student 4096 juil. 22 17:51 .   <- 1 sous-repertoire
drwxrwxr-x 4 student student 4096 juil. 22 17:51 .   <- 2 sous-repertoires
drwxrwxr-x 4 student student 4096 juil. 22 17:51 .   <- + 2 fichiers : inchange
```

Il part de 2, monte avec les sous-répertoires et ne bouge pas quand on ajoute des
fichiers ordinaires : un répertoire dont `ls -ld` affiche 5 contient donc 3
sous-répertoires, quel que soit le nombre de fichiers qu'il porte.

### `file` et `stat` : ce qu'est réellement un fichier

`ls` ne montre qu'une vue. `file` inspecte le **contenu** et ne se fie pas au
nom : copiez un fichier texte sous une extension d'image, `ls` vous croira,
`file` non.

```bash
cd /tmp/cours-l1-navigate/bibliotheque/catalogue
cp ../notice.md photo.png
file photo.png affiche.jpg /bin/ls ../dernier-inventaire
```

```text
photo.png:             ASCII text
affiche.jpg:           data
/bin/ls:               ELF 64-bit LSB pie executable, x86-64, [...] stripped
../dernier-inventaire: symbolic link to catalogue/inventaire.csv
```

Le fichier nommé `.png` est du texte ; celui nommé `.jpg`, rempli d'octets
aléatoires, ne correspond à aucune signature connue et `file` répond `data`.

`stat` donne les **métadonnées** complètes, celles que `ls -l` ne fait que
résumer : type, droits en octal **et** en symbolique, propriétaire avec son UID
numérique, inode, compteur de liens et quatre dates.

```bash
cd /tmp/cours-l1-navigate/bibliotheque
stat catalogue
```

```text
  File: catalogue
  Size: 4096      	Blocks: 8          IO Block: 4096   directory
Device: 252,0	Inode: 8558931     Links: 2
Access: (0775/drwxrwxr-x)  Uid: ( 1000/     student)   Gid: ( 1000/     student)
Access: 2026-07-22 17:48:20.420444140 +0200
Modify: 2026-07-22 17:51:06.808771424 +0200
Change: 2026-07-22 17:51:06.808771424 +0200
 Birth: 2026-07-22 17:48:20.389441849 +0200
```

`-c` n'extrait que ce qu'on demande, ce qui rend `stat` utilisable dans un
script : `stat -c '%n : %F, %s octets, %A (%a), %U:%G, %h lien(s)' catalogue`
répond `catalogue : directory, 4096 octets, drwxrwxr-x (775), student:student, 2 lien(s)`.

**Les trois horodatages ne mesurent pas la même chose**, et la seule façon de
s'en convaincre est de les faire bouger un par un :

```bash
F='mtime %y\nctime %z\natime %x\n'
printf 'Bulletin du mois.\n' > bulletin.txt ; stat --printf="$F" bulletin.txt
echo 'Ouverture le jeudi.' >> bulletin.txt  ; stat --printf="$F" bulletin.txt
chmod 640 bulletin.txt                      ; stat --printf="$F" bulletin.txt
cat bulletin.txt > /dev/null                ; stat --printf="$F" bulletin.txt
```

Un `sleep 2` a été glissé entre chaque étape pour que les secondes se lisent :

```text
mtime 2026-07-22 18:00:02.953754056 +0200   <- etat initial
ctime 2026-07-22 18:00:02.953754056 +0200
atime 2026-07-22 18:00:02.953754056 +0200
mtime 2026-07-22 18:00:04.955903833 +0200   <- le CONTENU a change
ctime 2026-07-22 18:00:04.955903833 +0200
atime 2026-07-22 18:00:02.953754056 +0200
mtime 2026-07-22 18:00:04.955903833 +0200   <- les DROITS ont change
ctime 2026-07-22 18:00:06.958053611 +0200
atime 2026-07-22 18:00:02.953754056 +0200
mtime 2026-07-22 18:00:04.955903833 +0200   <- on a LU le fichier
ctime 2026-07-22 18:00:06.958053611 +0200
atime 2026-07-22 18:00:08.963203616 +0200
```

| Horodatage | Ce qui le fait bouger | Observé ci-dessus |
|---|---|---|
| `mtime` (Modify) | le **contenu** change | bouge à l'ajout de ligne, pas au `chmod` |
| `ctime` (Change) | le contenu **ou** les métadonnées changent | bouge à l'ajout **et** au `chmod` |
| `atime` (Access) | le fichier est **lu** | ne bouge qu'au `cat` |

C'est `mtime` que `ls -l` affiche, et donc `mtime` que `ls -lt` trie. Vérifié sur
la machine d'essai : après un `chmod 775 catalogue`, `ls -ltr` laisse `catalogue`
à sa place avec sa date de 17:48, alors que `ls -ltr --time=ctime` le fait passer
en dernier avec 17:50.

> **`atime` n'est pas fiable pour dater une lecture.** La racine de la machine
> d'essai est montée en `relatime` (`findmnt -no OPTIONS /` répond `rw,relatime`),
> un mode où le noyau n'écrit `atime` que s'il est plus ancien que `mtime` ou
> vieux de plus de 24 heures ; en `noatime`, il ne bouge jamais. La quatrième
> date, `Birth`, est celle de la création de l'inode : elle n'existe que sur les
> systèmes de fichiers qui la stockent.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `ls: cannot access 'x': No such file or directory` | faute de frappe ou mauvais répertoire | `pwd`, puis complétez avec **Tab** |
| `bash: cd: x: Not a directory` | vous avez donné un fichier à `cd` | `file x` ou `ls -ld x` |
| `bash: cd: x: Permission denied` | droit de traversée manquant sur le répertoire | `ls -ld x` |
| `ls: cannot open directory 'x': Permission denied` | droit de lecture manquant, alors que `ls -ld x` passe | `ls -ld x` |
| `ls -l rep` n'affiche pas ce que vous attendiez | il liste le contenu, pas le répertoire | ajoutez `-d` |
| `tree: command not found` | `tree` n'est pas installé | `find . -type d` |
| un fichier « disparu » de `ls` | son nom commence par un point | `ls -a` |
| `ls -lt` ignore un `chmod` récent | `-t` trie sur `mtime`, pas sur `ctime` | `stat <fichier>` |
| l'extension ment sur le contenu | le nom n'engage à rien | `file <fichier>` |
| `ls` sort une seule colonne | la sortie part dans un tube ou un fichier | comportement normal |

Pour tout effacer et repartir de zéro, un seul chemin absolu suffit :

```bash
cd ~
rm -rf /tmp/cours-l1-navigate
```
