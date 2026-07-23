# Lab — grep et expressions régulières

## Rappel

[**Filtrer du texte avec grep sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/)

`grep MOTIF fichier` garde les lignes qui correspondent. Les expressions
régulières rendent le motif précis : `^` et `$` ancrent au début/à la fin d'une
ligne, `[0-9]` est une classe de caractères, `-E` active le regex étendu, `-v`
inverse le filtre, `-o` n'affiche que le texte correspondant, et `-c` compte les
lignes au lieu de les afficher.

## Le cours

Les exemples ci-dessous travaillent sur un inventaire de parc (`parc.csv`) et un
journal d'atelier (`notes.txt`), que vous fabriquez vous-même : le challenge,
lui, vous donnera un tout autre fichier, d'autres champs et d'autres questions.
Le but est d'apprendre la méthode, pas de recopier une ligne.

Toutes les sorties reproduites ici ont été obtenues sur une VM AlmaLinux 10.2
avec **GNU grep 3.11** et la locale `en_US.UTF-8`. Une section entière est
consacrée aux résultats qui changent avec la locale.

### Le décor de démonstration

Fabriquez le décor plutôt que de fouiller `/var/log` : vous maîtrisez ainsi les
cas limites, et vos sorties sont reproductibles.

```bash
mkdir -p ~/atelier-grep/config && cd ~/atelier-grep

{
  printf '# parc de demonstration - atelier grep\n'
  printf 'nom;service;port;version;etat\n'
  printf 'web-01;frontal;8080;1.2.3;actif\n'
  printf 'web-02;frontal;8080;1.10.0;ARRETE\n'
  printf 'db-01;base;5432;15.4;actif \n'
  printf 'cache-01;cache;6379;7.2;Actif\n'
  printf '\tproxy-01;frontal;3128;3.5;actif\n'
  printf '\n'
  printf 'bastion-01;acces;22;9.6;maintenance\n'
  printf 'export-nuit;sauvegarde;2049;4.0;actif\n'
  printf 'supervision;metrologie;9090;2.51;arrêté\n'
} > parc.csv

{
  printf 'Journal de l atelier\n'
  printf '\n'
  printf '2026-07-22 [INFO] [web-01] redemarrage planifie puis controle du redemarrage\n'
  printf '2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee\n'
  printf '2026-07-22 [INFO] [proxy-01] fichier proxyXconf ignore par erreur\n'
  printf '2026-07-22 [ERREUR] [cache-01] le modele proxy-conf.tpl reste a jour\n'
  printf 'Le café de la salle est prêt, CAFÉ en majuscules aussi.\n'
  printf '\tcette ligne commence par une tabulation\n'
} > notes.txt

printf 'timeout=30\nupstream=web-01\n' > config/proxy.conf
printf 'timeout=15\nworkers=4\n'       > config/web.conf
ln -s config lien-config
```

Ce fichier contient volontairement six pièges : une ligne de commentaire, une
ligne d'en-tête, une ligne **vide**, une ligne indentée par une **tabulation**,
une ligne avec une **espace finale** invisible, et des états écrits en trois
casses différentes plus un accent. `cat -A` les rend visibles (`$` marque la fin
de ligne, `^I` une tabulation) :

```bash
cat -A parc.csv
```

```text
# parc de demonstration - atelier grep$
nom;service;port;version;etat$
web-01;frontal;8080;1.2.3;actif$
web-02;frontal;8080;1.10.0;ARRETE$
db-01;base;5432;15.4;actif $
cache-01;cache;6379;7.2;Actif$
^Iproxy-01;frontal;3128;3.5;actif$
$
bastion-01;acces;22;9.6;maintenance$
export-nuit;sauvegarde;2049;4.0;actif$
supervision;metrologie;9090;2.51;arrM-CM-*tM-CM-)$
```

Retenez la ligne 5 : `actif $`, avec une espace après le mot. Elle va nous
servir.

### Chercher un motif littéral

Le cas le plus simple. `-n` préfixe chaque résultat par son numéro de ligne,
`-i` ignore la casse.

```bash
grep -n actif parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
5:db-01;base;5432;15.4;actif 
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

Quatre lignes seulement, alors que le fichier en compte cinq qui parlent d'un
service en marche. `cache-01` est écrit `Actif` : `grep` est sensible à la casse.

```bash
grep -in actif parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

Le réflexe : quand un résultat vous paraît trop court, rejouez avec `-i` avant
de conclure que la donnée est absente.

### Ancrer avec `^` et `$`

Une ancre ne consomme aucun caractère, elle fixe **où** la correspondance doit
se produire : `^` au début de la ligne, `$` à la fin.

```bash
grep -n "^web" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
```

L'ancre écarte tout ce qui contient `web` ailleurs sur la ligne. Sans elle, la
même recherche élargie aux trois fichiers ramène des lignes qui ne sont pas des
entrées d'inventaire :

```bash
grep -n web parc.csv notes.txt config/proxy.conf
```

```text
parc.csv:3:web-01;frontal;8080;1.2.3;actif
parc.csv:4:web-02;frontal;8080;1.10.0;ARRETE
notes.txt:3:2026-07-22 [INFO] [web-01] redemarrage planifie puis controle du redemarrage
config/proxy.conf:2:upstream=web-01
```

Quand `grep` reçoit plusieurs fichiers, il préfixe chaque ligne du nom du
fichier. C'est `-h` qui supprime ce préfixe, `-H` qui le force sur un fichier
unique.

Deux ancres collées l'une à l'autre, `^$`, décrivent une ligne vide :

```bash
grep -n "^$" parc.csv
```

```text
8:
```

Maintenant le piège. Cherchons les machines dont l'état, **en fin de ligne**,
est `actif` :

```bash
grep -n "actif$" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

La ligne 5 a disparu. Le motif nu `grep actif` la trouvait, l'ancre `$` la
perd : cette ligne se termine par une espace, donc `actif` n'est pas le dernier
caractère. Ce genre de bug est invisible à l'écran, d'où le premier geste de
diagnostic :

```bash
grep -n actif parc.csv | cat -A
```

```text
3:web-01;frontal;8080;1.2.3;actif$
5:db-01;base;5432;15.4;actif $
7:^Iproxy-01;frontal;3128;3.5;actif$
10:export-nuit;sauvegarde;2049;4.0;actif$
```

La correction consiste à tolérer les blancs finaux :

```bash
grep -nE "actif[[:blank:]]*$" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
5:db-01;base;5432;15.4;actif 
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
```

La même mésaventure existe au début de ligne. `^proxy` ne trouve rien, parce
que la ligne 7 commence par une tabulation :

```bash
grep -n "^proxy" parc.csv ; echo "code=$?"
```

```text
code=1
```

```bash
grep -nE "^[[:blank:]]*proxy" parc.csv
```

```text
7:	proxy-01;frontal;3128;3.5;actif
```

`[[:blank:]]` couvre l'espace et la tabulation, ce que `" "` seul ne fait pas.

### Le point, les classes, et l'échappement

`.` correspond à **n'importe quel caractère**. C'est pratique, et c'est le piège
le plus fréquent : il attrape aussi ce qu'on ne voulait pas. Cherchons les
lignes du journal qui parlent du fichier `proxy.conf` :

```bash
grep -n "proxy.conf" notes.txt
```

```text
4:2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee
5:2026-07-22 [INFO] [proxy-01] fichier proxyXconf ignore par erreur
6:2026-07-22 [ERREUR] [cache-01] le modele proxy-conf.tpl reste a jour
```

Trois lignes, dont deux qui ne parlent pas du bon fichier : le `.` a accepté le
`X` et le `-`. Pour un point **littéral**, il faut l'échapper :

```bash
grep -n "proxy\.conf" notes.txt
```

```text
4:2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee
```

Une classe `[...]` correspond à **un seul** caractère parmi ceux listés. Les
classes POSIX sont portables d'une distribution à l'autre :

| Classe | Équivalent | Usage |
|---|---|---|
| `[[:digit:]]` | `[0-9]` | chiffres |
| `[[:alpha:]]` | `[a-zA-Z]` | lettres |
| `[[:alnum:]]` | `[a-zA-Z0-9]` | lettres et chiffres |
| `[[:blank:]]` | espace et tabulation | blancs horizontaux |
| `[[:space:]]` | `[ \t\n]` | tous les blancs |
| `[[:upper:]]` / `[[:lower:]]` | `[A-Z]` / `[a-z]` | casse |

Le `^` en **première position dans les crochets** signifie « aucun parmi » :
`[^;]` correspond à tout caractère qui n'est pas un point-virgule. Ne le
confondez pas avec l'ancre `^` en début de motif.

```bash
grep -nE "^[[:alpha:]]+;" parc.csv
```

```text
2:nom;service;port;version;etat
11:supervision;metrologie;9090;2.51;arrêté
```

Seules deux lignes ont un premier champ fait uniquement de lettres : toutes les
autres contiennent un chiffre ou un tiret.

Enfin, un accent est un caractère comme un autre : il ne se devine pas.

```bash
grep -n "arrete" parc.csv ; echo "code=$?"
```

```text
code=1
```

```bash
grep -n "arr.t." parc.csv
```

```text
11:supervision;metrologie;9090;2.51;arrêté
```

Le motif sans accent ne trouve rien, alors que la ligne 11 existe. Notez au
passage que `.` a bien traversé `ê` et `é` : en locale UTF-8, `.` compte des
**caractères**, pas des octets. Nous y revenons plus bas.

### BRE contre ERE : ce que `-E` change

`grep` connaît deux dialectes d'expressions régulières :

| Dialecte | Activé par | Quantificateurs, alternance et groupes |
|---|---|---|
| **BRE** (basique) | `grep` par défaut | à **échapper** : `\+` `\?` `\{n,m\}`, la barre verticale et `\(\)` |
| **ERE** (étendu) | `grep -E` | s'écrivent **tels quels** : `+` `?` `{n,m}`, la barre verticale et `()` |

Dans les tableaux ci-dessus et ci-dessous, la barre verticale est écrite en
toutes lettres : c'est le caractère `|`, l'alternance « ou ».

La démonstration tient en deux lignes. Cherchons les machines arrêtées **ou** en
maintenance :

```bash
grep -n "ARRETE|maintenance" parc.csv ; echo "code=$?"
```

```text
code=1
```

Aucun résultat, et aucune erreur : en BRE, `|` n'est pas l'alternance, `grep` a
cherché la chaîne littérale `ARRETE|maintenance`. C'est le pire des cas, un
faux négatif silencieux. Les deux écritures correctes :

```bash
grep -n "ARRETE\|maintenance" parc.csv    # BRE, avec échappement
grep -nE "ARRETE|maintenance" parc.csv    # ERE, plus lisible
```

```text
4:web-02;frontal;8080;1.10.0;ARRETE
9:bastion-01;acces;22;9.6;maintenance
```

Même histoire avec `+` :

```bash
grep -n "web-0[0-9]+" parc.csv ; echo "code=$?"
```

```text
code=1
```

En BRE, `+` est un caractère ordinaire : le motif demandait littéralement un
`+` après le chiffre. Les deux formes qui marchent, et qui rendent exactement la
même liste, les noms faits de lettres puis d'un tiret puis de chiffres :

```bash
grep -n  "^[a-z]\+-[0-9]\+" parc.csv   # BRE
grep -nE "^[a-z]+-[0-9]+"   parc.csv   # ERE
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
9:bastion-01;acces;22;9.6;maintenance
```

Le quantificateur borné suit la même règle, `{n,m}` en ERE et `\{n,m\}` en BRE.
Les deux commandes ci-dessous donnent exactement le même résultat, les ports à
quatre chiffres :

```bash
grep -nE ";[0-9]{4};" parc.csv
grep -n  ";[0-9]\{4\};" parc.csv
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
7:	proxy-01;frontal;3128;3.5;actif
10:export-nuit;sauvegarde;2049;4.0;actif
11:supervision;metrologie;9090;2.51;arrêté
```

`bastion-01` manque à l'appel : son port est `22`, deux chiffres.

Le `?` (zéro ou un) se vérifie sur trois mots fabriqués :

```bash
printf 'arret\narrete\narretee\n' | grep -E "arrete?$"
```

```text
arret
arrete
```

Enfin les parenthèses, qui groupent :

```bash
grep -nE "^(web|db)-" parc.csv     # ERE
grep -n  "^\(web\|db\)-" parc.csv  # BRE, même résultat
```

```text
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
```

La règle de conduite : dès que votre motif contient `+`, `?`, `{n,m}`, `|` ou
`()`, passez en `-E`. Vous éviterez la moitié des faux négatifs.

### `-w` : le mot entier

`grep` cherche une **sous-chaîne**, pas un mot. Cherchons le champ `port` :

```bash
grep -n port parc.csv
```

```text
2:nom;service;port;version;etat
10:export-nuit;sauvegarde;2049;4.0;actif
```

La ligne 10 est un faux positif : `export` contient `port`. `-w` impose une
frontière de mot de part et d'autre du motif :

```bash
grep -nw port parc.csv
```

```text
2:nom;service;port;version;etat
```

Le point-virgule fait office de frontière, le `x` de `export` non. `-w`
équivaut au motif BRE `\<port\>` et rend le même service que `\b` dans d'autres
langages.

### `-o` : n'afficher que ce qui correspond

Par défaut, `grep` affiche la ligne entière. `-o` n'affiche que la portion
correspondante, une par ligne. Extrayons les niveaux de gravité du journal :

```bash
grep -oE "\[[^]]+\]" notes.txt
```

```text
[INFO]
[web-01]
[WARN]
[db-01]
[INFO]
[proxy-01]
[ERREUR]
[cache-01]
```

Pourquoi `[^]]+` plutôt que `.*` ? Parce que les quantificateurs sont
**gourmands** : ils prennent le plus possible.

```bash
grep -oE "\[.*\]" notes.txt
```

```text
[INFO] [web-01]
[WARN] [db-01]
[INFO] [proxy-01]
[ERREUR] [cache-01]
```

`.*` a avalé le crochet fermant, l'espace et le crochet ouvrant suivants : une
seule correspondance par ligne au lieu de deux. La parade POSIX est toujours la
même, remplacer `.` par une **classe négative** qui exclut le délimiteur :
`[^]]` ici, `[^;]` pour un champ CSV, `[^>]` pour une balise.

`-o` sert surtout à extraire un champ pour le compter ensuite. Le dernier champ
de chaque ligne, c'est-à-dire tout ce qui suit le dernier `;` :

```bash
grep -v "^#" parc.csv | grep -oE "[^;]+$" | sort | uniq -c | sort -rn
```

```text
      3 actif
      1 maintenance
      1 etat
      1 arrêté
      1 ARRETE
      1 Actif
      1 actif 
```

Sept catégories pour quatre états réels : `Actif` et `actif ` sont comptés à
part, et l'en-tête `etat` s'est glissé dedans. Une extraction n'est jamais un
comptage : il faut d'abord écarter les lignes de service, puis normaliser la
casse et les blancs. C'est le vrai travail.

### `-c` compte des lignes, jamais des occurrences

Le journal contient le mot `redemarrage` deux fois, sur une seule ligne.

```bash
grep -c redemarrage notes.txt
```

```text
1
```

```bash
grep -o redemarrage notes.txt | wc -l
```

```text
2
```

`-c` répond « une ligne contient le motif », pas « le motif apparaît une fois ».
Pour compter les **occurrences**, il faut passer par `-o` puis `wc -l`. La
confusion est classique et fausse silencieusement les rapports.

Sur plusieurs fichiers, `-c` donne un compte par fichier, préfixé du nom :

```bash
grep -c timeout config/*.conf
```

```text
config/proxy.conf:1
config/web.conf:1
```

### `-v` : garder ce qui ne correspond pas

`-v` inverse la sélection. Combiné avec une ancre, c'est le nettoyeur de
fichiers de configuration :

```bash
grep -vnE "^[[:blank:]]*(#|$)" parc.csv
```

```text
2:nom;service;port;version;etat
3:web-01;frontal;8080;1.2.3;actif
4:web-02;frontal;8080;1.10.0;ARRETE
5:db-01;base;5432;15.4;actif 
6:cache-01;cache;6379;7.2;Actif
7:	proxy-01;frontal;3128;3.5;actif
9:bastion-01;acces;22;9.6;maintenance
10:export-nuit;sauvegarde;2049;4.0;actif
11:supervision;metrologie;9090;2.51;arrêté
```

Le motif se lit : début de ligne, des blancs éventuels, puis un `#` **ou** la
fin de ligne. Les lignes 1 et 8, le commentaire et la ligne vide, sont écartées.
Notez que `-v` s'applique à la ligne entière : il n'y a pas de « tout sauf ce
mot » à l'intérieur d'une ligne.

### Chercher dans une arborescence : `-r`, `-R`, `-l`

`-r` descend récursivement dans les sous-répertoires :

```bash
grep -rn timeout .
```

```text
./config/proxy.conf:1:timeout=30
./config/web.conf:1:timeout=15
```

Le lien symbolique `lien-config` pointe pourtant sur ce même répertoire
`config`, et ses fichiers n'apparaissent pas. Ce n'est pas un oubli : **`-r` ne
suit pas les liens symboliques rencontrés pendant le parcours**. `-R` les suit
tous :

```bash
grep -Rn timeout .
```

```text
./config/proxy.conf:1:timeout=30
./config/web.conf:1:timeout=15
./lien-config/proxy.conf:1:timeout=30
./lien-config/web.conf:1:timeout=15
```

Chaque fichier est trouvé deux fois, une par chemin. Nuance à retenir : `-r`
suit quand même un lien **nommé explicitement** sur la ligne de commande.

```bash
grep -rn timeout lien-config
```

```text
lien-config/proxy.conf:1:timeout=30
lien-config/web.conf:1:timeout=15
```

Sur un lien qui remonte dans l'arborescence, `-R` détecte la boucle et le dit,
mais après avoir déjà parcouru les fichiers une fois de plus :

```bash
mkdir -p boucle && ln -s .. boucle/remonte
grep -Rn timeout boucle
```

```text
boucle/remonte/config/proxy.conf:1:timeout=30
boucle/remonte/config/web.conf:1:timeout=15
boucle/remonte/lien-config/proxy.conf:1:timeout=30
boucle/remonte/lien-config/web.conf:1:timeout=15
grep: boucle/remonte/boucle: warning: recursive directory loop
```

Rien ne se bloque, mais les résultats sont dupliqués et un avertissement se
glisse dans la sortie d'erreur. Préférez `-r`, et n'utilisez `-R` que si vous
savez pourquoi.

Deux options qui vont avec la récursion. `-l` ne rend que les noms de fichiers,
ce qui sert à enchaîner avec `xargs` :

```bash
grep -rl timeout .
```

```text
./config/proxy.conf
./config/web.conf
```

`--include` restreint le parcours à un motif de **nom de fichier**, à ne pas
confondre avec le motif recherché :

```bash
grep -rn --include="*.conf" timeout .
```

```text
./config/proxy.conf:1:timeout=30
./config/web.conf:1:timeout=15
```

### Les codes de retour, et `grep -q` dans un test

C'est ce qui rend `grep` utilisable dans un script. Trois valeurs :

| Code | Signification |
|---|---|
| `0` | au moins une ligne correspond |
| `1` | aucune ligne ne correspond (ce n'est **pas** une erreur) |
| `2` | erreur : fichier illisible, regex invalide |

```bash
grep -q actif parc.csv;    echo "trouve      -> $?"
grep -q inconnu parc.csv;  echo "pas trouve  -> $?"
grep -q actif absent.csv;  echo "erreur      -> $?"
```

```text
trouve      -> 0
pas trouve  -> 1
grep: absent.csv: No such file or directory
erreur      -> 2
```

`-q` (quiet) n'affiche rien sur la sortie standard : c'est la forme à employer
dans un test, où seul le code compte. Attention, il ne tait
pas les **erreurs**, qui partent sur la sortie d'erreur : le message
`No such file or directory` ci-dessus a bien été émis malgré `-q`. Pour le
faire taire aussi, ajoutez `-s`, mais le code reste `2` :

```bash
grep -qs actif absent.csv ; echo "code=$?"
```

```text
code=2
```

`-q` s'arrête aussi **dès la première correspondance**, ce qui se prouve sur un
flux infini : la commande de gauche rend la main tout de suite, celle de droite
ne s'arrête jamais et se fait tuer par `timeout` au bout de 3 secondes (code
`124`).

```bash
timeout 5 bash -c 'yes correspondance | grep -q correspondance'      ; echo "code=$?"
timeout 3 bash -c 'yes correspondance | grep correspondance >/dev/null' ; echo "code=$?"
```

```text
code=0
code=124
```

Le motif d'usage courant :

```bash
if grep -q "^bastion-01;" parc.csv; then
  echo "bastion-01 est inventorie"
else
  echo "absent"
fi

if grep -q "^switch-01;" parc.csv; then
  echo "switch-01 est inventorie"
else
  echo "switch-01 absent de l inventaire"
fi
```

```text
bastion-01 est inventorie
switch-01 absent de l inventaire
```

Distinguer `1` de `2` compte : un script qui teste seulement « code non nul »
confond « la machine n'est pas dans l'inventaire » avec « le fichier
d'inventaire est introuvable ». Le second cas mérite une alerte, pas une
branche `else`.

### La locale change le sens des classes

Sur cette VM, `locale` renvoie `LANG=en_US.UTF-8` et `LC_ALL` est vide. Les
résultats suivants en dépendent : préfixer une commande par `LC_ALL=C` ne change
la locale que pour elle.

```bash
echo "café prêt" | grep -oE "[[:alpha:]]+"
```

```text
café
prêt
```

```bash
echo "café prêt" | LC_ALL=C grep -oE "[[:alpha:]]+"
```

```text
caf
pr
t
```

En locale `C`, `é` et `ê` ne sont pas des lettres : chaque mot accentué est
coupé en morceaux. Même effet sur le repliage de casse, où `-i` cesse de
rapprocher `CAFÉ` de `café` :

```bash
grep -oi "CAFÉ" notes.txt
```

```text
café
CAFÉ
```

```bash
LC_ALL=C grep -oi "CAFÉ" notes.txt
```

```text
CAFÉ
```

Et sur le point, qui compte des caractères en UTF-8 et des octets en `C` :

```bash
echo "café" | grep -c "^c.f.$"
echo "café" | LC_ALL=C grep -c "^c.f.$"
```

```text
1
0
```

Le motif `^c.f.$` demande quatre caractères. En UTF-8, `é` en est un et la ligne
correspond ; en locale `C`, `é` en vaut deux (`0xC3 0xA9`), la ligne en compte
cinq et le motif échoue.

L'écart n'est pas que sémantique, il est aussi spectaculaire en temps de calcul.
Sur un fichier de 138 Mio fabriqué pour l'occasion, le même `grep` avec une
classe POSIX met 7,7 secondes en UTF-8 et 0,12 seconde en locale `C` :

```bash
yes "ligne de test avec du texte accentué café prêt et des chiffres 12345" \
  | head -2000000 > /tmp/gros.txt
time grep -c "[[:alpha:]]\+345" /tmp/gros.txt
time LC_ALL=C grep -c "[[:alpha:]]\+345" /tmp/gros.txt
rm -f /tmp/gros.txt
```

Trois mesures de chaque, sur la VM du lab : `7,73 / 7,73 / 7,70 s` contre
`0,13 / 0,12 / 0,12 s`, soit un facteur soixante. En UTF-8, `grep` doit décoder
chaque caractère multi-octets ; en `C` il compare des octets.

Conséquence pratique : dans un script, forcer `LC_ALL=C` accélère `grep` et rend
le tri reproductible, mais casse tout motif reposant sur des lettres accentuées.
Choisissez en connaissance de cause, et écrivez-le dans le script.

### Le motif doit être protégé du shell

Le shell interprète `*`, `?`, `$`, `[` et l'espace **avant** que `grep` ne les
voie. Dans un répertoire qui contient `proxy.conf` et `web.conf` :

```bash
printf 'inclure *.conf au demarrage\n' > config/liste.txt
cd config
grep *.conf liste.txt ; echo "code=$?"
```

```text
code=1
```

Rien, alors que la chaîne `*.conf` est bien dans le fichier. Le shell a remplacé
`*.conf` par la liste des fichiers correspondants : `grep` a reçu
`grep proxy.conf web.conf liste.txt`, donc il a cherché le motif `proxy.conf`
dans les deux autres fichiers. Un motif entre guillemets, ou `-F` pour une
recherche strictement littérale, corrigent le tir :

```bash
grep "\*\.conf" liste.txt
grep -F "*.conf" liste.txt
cd ..
```

```text
inclure *.conf au demarrage
inclure *.conf au demarrage
```

Une ligne par commande : les deux écritures trouvent la même chose.

Le même réflexe vaut pour `$` :

```bash
printf 'prix: 10$\n' > /tmp/prix.txt
grep    "prix: 10$" /tmp/prix.txt ; echo "code=$?"
grep -F "prix: 10$" /tmp/prix.txt ; echo "code=$?"
```

```text
code=1
prix: 10$
code=0
```

Sans `-F`, le `$` est lu comme l'ancre de fin de ligne, et le motif devient
impossible à satisfaire. Règle simple : **toujours mettre le motif entre
guillemets simples**, et passer `-F` quand il ne contient aucune expression
régulière.

Dernier classique du genre, `grep` qui se trouve lui-même :

```bash
ps -ef | grep chronyd
```

```text
chrony       707       1  0 13:30 ?        00:00:00 /usr/sbin/chronyd -n -F 2
ansible    15077   15075  0 14:01 ?        00:00:00 grep chronyd
```

(Les numéros de processus et les heures diffèrent chez vous, pas la deuxième
ligne.) Le processus `grep` figure dans la liste que `ps` vient de produire. On
l'écarte avec un second filtre :

```bash
ps -ef | grep chronyd | grep -v grep
```

```text
chrony       707       1  0 13:30 ?        00:00:00 /usr/sbin/chronyd -n -F 2
```

### Voir le contexte d'une correspondance

Sur un journal, la ligne trouvée ne suffit souvent pas : `-A N` affiche N lignes
après, `-B N` N lignes avant, `-C N` des deux côtés. Les lignes de contexte sont
préfixées par `-` au lieu de `:`, ce qui permet de les distinguer :

```bash
grep -n -A1 "WARN" notes.txt
```

```text
4:2026-07-22 [WARN] [db-01] sauvegarde de /etc/proxy.conf effectuee
5-2026-07-22 [INFO] [proxy-01] fichier proxyXconf ignore par erreur
```

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Aucun résultat alors que la donnée existe | casse différente : rejouer avec `-i` |
| Aucun résultat avec un motif contenant `+`, `?`, `{}`, `()` ou la barre verticale | motif ERE joué en BRE : ajouter `-E` (ou échapper) |
| Une ancre `$` perd des lignes | espaces finaux invisibles : vérifier avec `cat -A`, tolérer avec `[[:blank:]]*$` |
| Une ancre `^` perd des lignes | ligne indentée : accepter `^[[:blank:]]*` |
| Trop de résultats, motif contenant un point | `.` accepte tout : écrire `\.` pour un point littéral |
| Trop de résultats, correspondance partielle | sous-chaîne au lieu du mot : ajouter `-w` |
| `-o` ne rend qu'une correspondance par ligne | gourmandise de `.*` : utiliser une classe négative `[^X]*` |
| Le compte est plus petit que prévu | `-c` compte les lignes : passer par `grep -o` puis `wc -l` |
| Résultats absurdes, motif contenant `*` ou `$` | motif interprété par le shell : mettre entre guillemets simples, ou `-F` |
| Un accent n'est pas trouvé, ou un mot est coupé | locale : comparer avec et sans `LC_ALL=C` |
| Les fichiers derrière un lien symbolique sont ignorés | `-r` ne suit pas les liens du parcours : utiliser `-R` en connaissance de cause |
| `grep: ...: No such file or directory` | code de retour `2`, ce n'est pas « aucune correspondance » |
| `grep: Invalid regular expression` | crochet ou parenthèse non fermé, ou syntaxe ERE en BRE |
| `Binary file ... matches` | fichier vu comme binaire : forcer avec `-a` |

### Défaire le décor

```bash
rm -rf ~/atelier-grep /tmp/prix.txt
```
