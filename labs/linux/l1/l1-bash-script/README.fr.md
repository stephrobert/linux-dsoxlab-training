# Lab — un premier script Bash

## Rappel

[**Écrire son premier script sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/premier-script/)

Un script commence par un shebang (`#!/usr/bin/env bash`) et doit être exécutable
(`chmod +x`). `$1` est le premier argument. Une boucle `while read` parcourt un
fichier ligne par ligne, des variables accumulent les compteurs, `if` teste une
condition, et `exit <n>` fixe le code de retour que l'appelant vérifie avec `$?`.

## Le cours

Les exemples ci-dessous travaillent sur un journal de sauvegardes,
`journal-sauvegardes.txt`, dont les lignes valent `date site ok` ou
`date site echec`, et sur un script de démonstration `bilan.sh` : le challenge,
lui, vous demandera un autre fichier, d'autres états et d'autres compteurs. Le
but est d'apprendre la méthode, pas de recopier une ligne.

Toutes les sorties reproduites ici ont été obtenues sur une machine AlmaLinux 10
avec `bash 5.2.26`. Le fichier de démonstration :

```text
2026-07-19 comptabilite ok
2026-07-19 messagerie echec
2026-07-20 comptabilite ok
2026-07-20 messagerie ok
2026-07-21 comptabilite echec
2026-07-21 messagerie ok
```

### Trois gestes, et un script tourne

Un script est un simple fichier texte. Ce qui le rend exécutable, c'est un bit
de permission ; ce qui le rend lançable par son nom, c'est un chemin.

```bash
cat > bonjour.sh <<'EOF'
#!/bin/bash
echo "Bonjour, $USER, sur $(hostname -s)"
EOF
ls -l bonjour.sh
```

```text
-rw-r--r--. 1 ansible ansible 54 Jul 22 13:35 bonjour.sh
```

Le fichier n'a aucun `x`. Le lancer échoue :

```bash
./bonjour.sh
echo $?
```

```text
bash: ./bonjour.sh: Permission denied
126
```

`chmod +x` ajoute le droit d'exécution, et le script part :

```bash
chmod +x bonjour.sh
ls -l bonjour.sh
./bonjour.sh
```

```text
-rwxr-xr-x. 1 ansible ansible 54 Jul 22 13:35 bonjour.sh
Bonjour, ansible, sur atelier
```

Le `./` n'est pas décoratif. Sans lui, le shell cherche le nom dans les
répertoires du `PATH`, où le répertoire courant ne figure pas :

```bash
bonjour.sh
echo $?
```

```text
bash: bonjour.sh: command not found
127
```

Retenez ces deux codes, ils reviennent souvent : **126** signifie « trouvé mais
pas exécutable », **127** signifie « pas trouvé ».

### Le shebang, et ce qui se passe vraiment quand il manque

La première ligne du fichier désigne l'interpréteur. Elle doit être la toute
première, sans espace ni ligne vide avant.

Que se passe-t-il si on l'oublie ? Le guide annonce que le système ne saura pas
qu'il s'agit d'un script Bash. La machine est plus nuancée. Avec le même
contenu, sans shebang :

```bash
printf 'echo "shell effectif : $0"\n' > sans-shebang.sh
chmod +x sans-shebang.sh
./sans-shebang.sh
```

```text
shell effectif : ./sans-shebang.sh
```

Le script tourne quand même. Ce n'est pas le noyau qui l'a accepté, c'est le
shell appelant qui a rattrapé son refus. On le voit en demandant l'exécution
directement au noyau, sans passer par un shell :

```bash
python3 -c "import os; os.execv('./sans-shebang.sh', ['./sans-shebang.sh'])"
```

```text
OSError: [Errno 8] Exec format error
```

La même commande sur un fichier muni d'un shebang passe sans broncher. La leçon :
sans shebang, votre script ne dépend plus de lui-même mais de qui le lance. Tout
ce qui l'appellera autrement qu'un shell (`cron`, un service, un autre
programme) recevra cette erreur. Le shebang n'est pas une politesse.

Un shebang qui désigne un interpréteur inexistant donne, sur AlmaLinux 10 :

```bash
printf '#!/bin/bsh\necho coucou\n' > mauvais-shebang.sh
chmod +x mauvais-shebang.sh
./mauvais-shebang.sh
echo $?
```

```text
bash: ./mauvais-shebang.sh: cannot execute: required file not found
127
```

> **Ce message ne dit pas `bad interpreter`.** Beaucoup de documentations
> annoncent `bad interpreter: No such file or directory` : c'est la formulation
> des versions plus anciennes de Bash. Avec `bash 5.2`, c'est
> `cannot execute: required file not found`. Le diagnostic reste le même :
> relisez la première ligne.

Piège jumeau, et le plus vicieux : un fichier écrit sous Windows. Chaque ligne
se termine par un `\r`, y compris le shebang, qui désigne alors un interpréteur
nommé `/bin/bash\r`.

```bash
cat -A crlf.sh
```

```text
#!/bin/bash^M$
etat="ok"^M$
if [ "$etat" = "ok" ]; then^M$
  echo EGAL^M$
fi^M$
```

```bash
./crlf.sh            # bash: ./crlf.sh: cannot execute: required file not found
bash crlf.sh         # crlf.sh: line 6: syntax error: unexpected end of file
sed -i 's/\r$//' crlf.sh
./crlf.sh            # EGAL
```

Le `$` de fin de ligne est normal dans `cat -A`, le `^M` ne l'est pas. Notez que
forcer `bash crlf.sh` contourne bien le shebang, mais échoue plus loin : le
`fi\r` n'est pas reconnu comme un `fi`.

`#!/bin/bash` et `#!/usr/bin/env bash` sont tous deux acceptés. Sur cette
machine ils aboutissent au même binaire, `/bin` étant un lien vers `usr/bin` :

```text
lrwxrwxrwx. 1 root root 7 Apr  2  2025 /bin -> usr/bin
```

### Les variables, et les deux erreurs qui coûtent le plus cher

Une variable se déclare **sans espace** autour du `=`, et se relit avec `$`.
L'espace n'est pas une faute de style, c'est un changement de sens : le shell
comprend alors un nom de commande suivi d'arguments.

```bash
nom = "alice"
echo "[$nom]"
echo $?
```

```text
bash: nom: command not found
[]
0
```

Regardez le dernier `0` : la ligne fautive n'a rien cassé de visible, la
variable est simplement restée vide et le script a continué. C'est le genre de
panne qu'on ne trouve qu'au bout d'une heure.

La seconde erreur, ce sont les guillemets manquants. Soit un fichier dont le nom
contient un espace :

```bash
f="journal du soir.txt"
wc -l $f
```

```text
wc: journal: No such file or directory
wc: du: No such file or directory
wc: soir.txt: No such file or directory
0 total
```

Sans guillemets, le shell a découpé la valeur en trois mots avant de les passer
à `wc`. Avec guillemets, un seul argument :

```bash
wc -l "$f"
```

```text
2 journal du soir.txt
```

Le même piège dans un test produit une erreur, puis une **mauvaise réponse** :

```bash
if [ -f $f ]; then echo trouve; else echo "pas trouve"; fi
```

```text
bash: [: too many arguments
pas trouve
```

```bash
if [ -f "$f" ]; then echo trouve; else echo "pas trouve"; fi
```

```text
trouve
```

À noter : les doubles crochets `[[ ]]` ne découpent pas le contenu d'une
variable, `[[ -f $f ]]` répond correctement `trouve` même sans guillemets. Ce
n'est pas une raison de s'en passer, `[ ]` reste partout, mais cela explique
pourquoi le même test se comporte différemment selon la syntaxe employée.

### Les arguments : `$1`, `$#`, `$0`

Un script reçoit ce qu'on écrit après son nom.

```bash
cat > args.sh <<'EOF'
#!/bin/bash
echo "\$0 = $0"
echo "\$1 = $1"
echo "\$2 = $2"
echo "\$# = $#"
echo "\$@ = $@"
EOF
chmod +x args.sh
./args.sh journal-sauvegardes.txt comptabilite
```

```text
$0 = ./args.sh
$1 = journal-sauvegardes.txt
$2 = comptabilite
$# = 2
$@ = journal-sauvegardes.txt comptabilite
```

Sans aucun argument, `$1` n'est pas une erreur : c'est une chaîne vide, et `$#`
vaut `0`.

```text
$0 = ./args.sh
$1 =
$2 =
$# = 0
$@ =
```

Les guillemets à l'appel groupent un argument contenant des espaces :

```bash
./args.sh "journal du soir.txt"
```

```text
$0 = ./args.sh
$1 = journal du soir.txt
$2 =
$# = 1
$@ = journal du soir.txt
```

### Valider avant d'agir

Un script sérieux refuse de travailler sur une entrée absurde, et le dit sur la
**sortie d'erreur** (`>&2`) pour ne pas polluer sa sortie utile.

```bash
if [ "$#" -ne 1 ]; then
    echo "Usage : $0 <journal>" >&2
    exit 2
fi

journal="$1"

if [ ! -f "$journal" ]; then
    echo "Erreur : '$journal' n'est pas un fichier lisible." >&2
    exit 2
fi
```

Le code `2` est la convention pour « mauvaise utilisation », distincte du `1`
d'une erreur de traitement. Séparer les deux permet à l'appelant de savoir s'il
doit corriger sa ligne de commande ou regarder les données.

### Parcourir un fichier ligne par ligne

Le patron est `while read`, alimenté par une **redirection** placée après le
`done` :

```bash
n=0
while read -r date site etat; do
    n=$((n + 1))
    echo "tour $n : date=$date site=$site etat=$etat"
done < journal-sauvegardes.txt
echo "total apres la boucle : n=$n"
```

```text
tour 1 : date=2026-07-19 site=comptabilite etat=ok
tour 2 : date=2026-07-19 site=messagerie etat=echec
tour 3 : date=2026-07-20 site=comptabilite etat=ok
tour 4 : date=2026-07-20 site=messagerie etat=ok
tour 5 : date=2026-07-21 site=comptabilite etat=echec
tour 6 : date=2026-07-21 site=messagerie etat=ok
total apres la boucle : n=6
```

`read` découpe la ligne sur les espaces et remplit les variables dans l'ordre.
`-r` désactive l'interprétation des antislashs : mettez-le toujours.

Trois comportements de `read` méritent d'être connus.

**La dernière variable ramasse tout le reste.** Une ligne à quatre champs lue
avec trois variables donne :

```text
date=[2026-07-19] site=[comptabilite] etat=[ok archive-froide]
```

C'est pratique pour un champ « commentaire » en fin de ligne, et c'est un piège
si vous comparez ensuite `"$etat"` à une valeur exacte.

**Une dernière ligne sans saut de ligne final est perdue.** Le fichier suivant
contient trois lignes, mais son dernier octet est `c`, pas `\n` :

```bash
od -c sans-newline.txt
```

```text
0000000   a       o   k  \n   b       o   k  \n   c       e   c   h   e
0000020   c
0000021
```

```text
lu: a ok
lu: b ok
lignes lues = 2  (le fichier en contient 3)
```

Le garde-fou consiste à continuer tant que la variable n'est pas vide :

```bash
while read -r nom etat || [ -n "$nom" ]; do ...; done < sans-newline.txt
```

```text
lu: a ok
lu: b ok
lu: c echec
lignes lues = 3
```

**`IFS=` conserve les espaces de tête.** Sur une ligne indentée :

```text
sans IFS= : [indente ok]
avec IFS= : [   indente ok]
```

Quand vous découpez en champs, laissez `IFS` par défaut. Quand vous voulez la
ligne brute, écrivez `while IFS= read -r ligne`.

### Le piège qui coûte le plus d'heures : la boucle dans un sous-shell

Voici deux scripts qui ne diffèrent que par la façon d'alimenter la boucle.

```bash
#!/bin/bash
n=0
while read -r date site etat; do
    n=$((n + 1))
done < "$1"                   # redirection
echo "total apres la boucle : n=$n"
```

```text
total apres la boucle : n=6
```

```bash
#!/bin/bash
n=0
cat "$1" | while read -r date site etat; do
    n=$((n + 1))
done                          # pipe
echo "total apres la boucle : n=$n"
```

```text
total apres la boucle : n=0
```

Aucune erreur, aucun message : simplement un compteur resté à zéro. Chaque
maillon d'un pipeline s'exécute dans un **sous-shell**, un processus enfant. La
boucle a bien compté, mais dans une copie des variables, qui meurt avec le
sous-shell. Le `echo` final lit l'originale, restée à `0`.

Deux façons correctes de faire :

```bash
done < "$fichier"             # redirection, quand la source est un fichier
done < <(sort "$fichier")     # substitution de processus, quand il faut une commande
```

La seconde forme donne bien le résultat attendu :

```text
echecs comptes apres un sort : n=2
```

### Compter, tester, décider

Deux compteurs, un `case` pour trier les états, et l'incrément arithmétique
`$(( ))` :

```bash
reussies=0
echouees=0

while read -r date site etat; do
    [ -z "$date" ] && continue
    case "$etat" in
        ok)    reussies=$((reussies + 1)) ;;
        echec) echouees=$((echouees + 1)) ;;
    esac
done < "$journal"
```

Un `if` ferait tout aussi bien pour deux cas ; `case` restera lisible quand il y
en aura cinq. La ligne `[ -z "$date" ] && continue` saute les lignes vides.

### Le code de retour

`exit <n>` fixe le code que l'appelant recevra, et l'appelant le lit dans `$?`.

```bash
if [ "$echouees" -gt 0 ]; then
    exit 3
fi
exit 0
```

Quatre choses à savoir, toutes vérifiables en une ligne.

**`$?` ne survit pas à la commande suivante.** Il contient le code de la
**dernière** commande exécutée, `echo` compris :

```text
premier  echo $? : 3
deuxieme echo $? : 0
```

Si vous devez en faire quoi que ce soit, mémorisez-le immédiatement :

```bash
./bilan.sh journal-sauvegardes.txt > /dev/null
code=$?
```

**Les codes sont bornés à 0-255.** Un `exit 256` est repris modulo 256 et
signale donc un succès :

```text
exit 256 -> $? = 0
exit -1  -> $? = 255
```

**Un script sans `exit` renvoie le code de sa dernière commande.** Le même
script, avec un simple `echo "fin"` ajouté à la fin, ment sur son résultat :

```text
sans exit                     -> $? = 1
sans exit, mais un echo final -> $? = 0
```

C'est la raison pour laquelle un script se termine par un `exit` explicite.

**Un code de retour se consomme sans `$?`.** `if`, `&&` et `||` prennent
directement la commande :

```bash
if ./bilan.sh journal-sauvegardes.txt > /dev/null; then
    echo "toutes les sauvegardes sont passees"
else
    echo "au moins un echec (code $?)"
fi

./bilan.sh journal-parfait.txt      > /dev/null && echo "rien a signaler"
./bilan.sh journal-sauvegardes.txt  > /dev/null || echo "il faut regarder le journal"
```

```text
au moins un echec (code 3)
rien a signaler
il faut regarder le journal
```

C'est là tout l'intérêt d'un code de retour honnête : il rend le script
utilisable dans une chaîne (cron, CI, `&&`) sans que personne n'ait à relire sa
sortie.

### L'exemple complet

```bash
#!/bin/bash
# bilan.sh : compte les sauvegardes reussies et echouees d'un journal.
# Usage : ./bilan.sh <journal>

if [ "$#" -ne 1 ]; then
    echo "Usage : $0 <journal>" >&2
    exit 2
fi

journal="$1"

if [ ! -f "$journal" ]; then
    echo "Erreur : '$journal' n'est pas un fichier lisible." >&2
    exit 2
fi

reussies=0
echouees=0

while read -r date site etat; do
    [ -z "$date" ] && continue
    case "$etat" in
        ok)    reussies=$((reussies + 1)) ;;
        echec) echouees=$((echouees + 1)) ;;
    esac
done < "$journal"

echo "REUSSIES=$reussies"
echo "ECHOUEES=$echouees"

if [ "$echouees" -gt 0 ]; then
    exit 3
fi
exit 0
```

Les quatre exécutions, telles que la machine les a produites :

```bash
./bilan.sh journal-sauvegardes.txt ; echo "code : $?"
```

```text
REUSSIES=4
ECHOUEES=2
code : 3
```

```bash
./bilan.sh journal-parfait.txt ; echo "code : $?"
```

```text
REUSSIES=2
ECHOUEES=0
code : 0
```

```bash
./bilan.sh ; echo "code : $?"
```

```text
Usage : ./bilan.sh <journal>
code : 2
```

```bash
./bilan.sh /tmp/pas-la.txt ; echo "code : $?"
```

```text
Erreur : '/tmp/pas-la.txt' n'est pas un fichier lisible.
code : 2
```

Le deuxième cas est le seul qui prouve quelque chose sur la logique : un script
qui sortirait toujours en erreur passerait le premier test et échouerait
celui-là. Testez toujours le vôtre sur un jeu de données qui doit renvoyer `0`.

### Déboguer : `bash -x`, puis `shellcheck`

`bash -x` affiche chaque commande, variables déjà substituées, préfixée d'un
`+`. Sur un journal réduit à deux lignes :

```bash
bash -x ./bilan.sh court.txt
```

```text
+ '[' 1 -ne 1 ']'
+ journal=court.txt
+ '[' '!' -f court.txt ']'
+ reussies=0
+ echouees=0
+ read -r date site etat
+ '[' -z 2026-07-22 ']'
+ case "$etat" in
+ reussies=1
+ read -r date site etat
+ '[' -z 2026-07-22 ']'
+ case "$etat" in
+ echouees=1
+ read -r date site etat
+ echo REUSSIES=1
REUSSIES=1
+ echo ECHOUEES=1
ECHOUEES=1
+ '[' 1 -gt 0 ']'
+ exit 3
```

On y lit la boucle tour par tour, et surtout la **valeur réelle** des variables
au moment du test. `set -x` et `set +x` limitent la trace à une portion du
script.

`shellcheck` fait le même travail sans exécuter le script. Sur AlmaLinux 10 il
n'est pas dans les dépôts de base :

```bash
sudo dnf list --available ShellCheck
# Error: No matching Packages to list
sudo dnf -y install epel-release
sudo dnf -y install ShellCheck
```

Passons-lui une version fragile de la boucle :

```bash
#!/bin/bash
fichier=$1
n=0
cat $fichier | while read ligne; do
    n=$((n+1))
done
echo "lignes : $n"
```

```text
In fragile.sh line 4:
cat $fichier | while read ligne; do
    ^------^ SC2086 (info): Double quote to prevent globbing and word splitting.
                     ^--^ SC2162 (info): read without -r will mangle backslashes.
                          ^---^ SC2034 (warning): ligne appears unused.

In fragile.sh line 5:
    n=$((n+1))
    ^-- SC2030 (info): Modification of n is local (to subshell caused by pipeline).

In fragile.sh line 7:
echo "lignes : $n"
               ^-- SC2031 (info): n was modified in a subshell. That change might be lost.
```

Il a trouvé les quatre défauts vus plus haut, dont le sous-shell, sans rien
lancer. Sur `bilan.sh`, il ne reste qu'un avertissement :

```text
In bilan.sh line 20:
while read -r date site etat; do
                   ^--^ SC2034 (warning): site appears unused.
```

C'est exact : le champ du milieu est lu mais jamais utilisé. La convention pour
le dire explicitement est de le nommer `_` ; `shellcheck` se tait alors
complètement, et le script donne le même résultat :

```bash
while read -r date _ etat; do
```

### Quand `set -euo pipefail` n'attrape pas ce qu'on croit

`set -e` arrête le script à la première commande qui échoue, `set -u` interdit
les variables non définies, `set -o pipefail` propage l'échec d'un maillon de
pipeline. C'est la bonne ligne à placer juste après le shebang d'un script de
production. Encore faut-il savoir ce qu'elle **ne** fait **pas**.

**`set -e` ignore ce qui est déjà testé.** Une commande dont on exploite le
résultat n'est pas considérée comme un échec :

```bash
#!/bin/bash
set -e
if grep -q "introuvable" journal-sauvegardes.txt; then
    echo "trouve"
else
    echo "1. grep a echoue, le script vit toujours"
fi
grep -q "introuvable" journal-sauvegardes.txt && echo "trouve"
echo "2. a gauche de && non plus, le script vit toujours"
grep -q "introuvable" journal-sauvegardes.txt
echo "3. cette ligne ne doit jamais s'afficher"
```

```text
1. grep a echoue, le script vit toujours
2. a gauche de && non plus, le script vit toujours
code=1
```

La troisième ligne ne s'affiche pas : c'est le seul `grep` non testé qui a tué
le script. Les deux premiers, eux, sont passés sans bruit.

**`set -e` tue le script sur un incrément.** Le piège le plus déroutant de tous,
parce qu'il frappe précisément le code d'un compteur :

```bash
#!/bin/bash
set -e
n=0
echo "avant"
((n++))
echo "apres : n=$n"
```

```text
avant
code=1
```

Le script s'est arrêté, sans le moindre message. `((n++))` renvoie la valeur
**avant** incrément, donc `0`, et une expression arithmétique nulle vaut un code
de retour non nul. `set -e` en conclut à un échec. La forme d'affectation n'a
pas ce défaut :

```bash
n=$((n + 1))
```

```text
avant
apres : n=1
code=0
```

**`$?` après un pipe ne parle que du dernier maillon.**

```bash
cat fichier-inexistant.txt | wc -l
echo "sans pipefail : $?"
set -o pipefail
cat fichier-inexistant.txt | wc -l
echo "avec pipefail : $?"
```

```text
cat: fichier-inexistant.txt: No such file or directory
0
sans pipefail : 0
cat: fichier-inexistant.txt: No such file or directory
0
avec pipefail : 1
```

Sans `pipefail`, le pipeline se déclare en succès alors que `cat` a échoué :
`wc -l` a fait son travail sur une entrée vide, et c'est lui qui a le dernier
mot. Le détail maillon par maillon reste disponible dans le tableau
`PIPESTATUS` :

```text
PIPESTATUS = 1 0
```

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `Permission denied`, code 126 | le bit `x` manque : `chmod +x` |
| `command not found` sur son propre script, code 127 | le `./` manque devant le nom |
| `cannot execute: required file not found`, code 127 | shebang pointant vers un interpréteur inexistant, ou fins de ligne CRLF |
| `syntax error: unexpected end of file` avec `bash script.sh` | fins de ligne CRLF ; vérifier par `cat -A`, corriger par `sed -i 's/\r$//'` |
| `nom: command not found` sur une ligne d'affectation | des espaces autour du `=` |
| `[: too many arguments` | variable non quotée contenant un espace : écrire `[ -f "$f" ]` |
| Le compteur vaut `0` après la boucle | boucle alimentée par un pipe, donc exécutée dans un sous-shell : `done < fichier` ou `done < <(commande)` |
| La dernière ligne du fichier n'est jamais lue | pas de saut de ligne final : ajouter `\|\| [ -n "$var" ]` à la condition du `while` |
| Le script s'arrête sans message juste après un `((n++))` | `set -e` plus une expression arithmétique valant `0` : écrire `n=$((n + 1))` |
| `$?` vaut `0` alors que la première commande du pipe a échoué | seul le dernier maillon compte : `set -o pipefail`, ou lire `${PIPESTATUS[0]}` |
| Le code de retour vaut `0` alors que le script fait `exit 256` | les codes sont bornés à 0-255, rester dans 1-255 |
| Le code de retour vaut `0` alors qu'une commande a échoué | pas d'`exit` explicite : le code est celui du dernier `echo`, qui a réussi |
| `shellcheck: command not found` sur AlmaLinux 10 | absent des dépôts de base : `sudo dnf -y install epel-release` puis `sudo dnf -y install ShellCheck` |

Pour tout défaire et repartir de zéro :

```bash
rm -rf ~/atelier-scripts
```
