# Lab — Redirections et pipes

## Rappel

[**Redirections et pipes sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/)

Chaque commande a trois flux : l'entrée standard (0), la sortie standard (1) et
la sortie d'erreur (2). `>` envoie la sortie standard dans un fichier (écrase),
`>>` ajoute, `2>` envoie la sortie d'erreur, `2>&1` fusionne l'erreur dans la
sortie standard, et `|` passe la sortie d'une commande à la suivante. Se tromper
d'opérateur perd des données en silence.

## Le cours

Les exemples ci-dessous travaillent dans `~/demo-flux`, sur un fichier de
démonstration `releve.txt` : le challenge, lui, vous donnera un autre fichier et
vous demandera d'autres artefacts. Le but est d'apprendre la méthode, pas de
recopier une ligne.

Toutes les sorties reproduites ici ont été obtenues sur une AlmaLinux 10 avec
`bash` 5.2. Une redirection ne prévient jamais : elle écrase, elle tronque, elle
perd une erreur sans un mot. La seule parade est de savoir exactement ce que
chaque opérateur fait, et cela se vérifie en deux lignes.

### Le décor de démonstration

```bash
mkdir -p ~/demo-flux && cd ~/demo-flux
cat > releve.txt <<'EOF'
2026-07-20 OK sauvegarde quotidienne
2026-07-20 WARN espace disque faible
2026-07-21 OK sauvegarde quotidienne
2026-07-21 WARN certificat bientot expire
2026-07-22 OK sauvegarde quotidienne
EOF
```

Ce premier bloc utilise déjà une redirection : `cat > releve.txt` prend son
entrée standard (ici le document `<<'EOF'`) et l'écrit dans le fichier. Cinq
lignes, dont deux `WARN`.

Un point de vocabulaire qui évite beaucoup de confusions : **la redirection est
faite par le shell, pas par la commande**. `ls` ne sait pas qu'il écrit dans un
fichier ; c'est `bash` qui a ouvert le fichier et branché dessus le descripteur
de sortie avant de lancer `ls`. Tout ce qui suit découle de ce seul fait.

### Les trois flux, vus depuis le processus

Le tableau du guide est vérifiable directement : `/proc/self/fd` montre où
pointent les descripteurs d'un processus en cours d'exécution.

```bash
bash -c 'ls -l /proc/self/fd' > rapport.out 2> defauts.err
cat rapport.out
```

```text
total 0
lr-x------. 1 ansible ansible 64 Jul 22 14:15 0 -> pipe:[52264]
l-wx------. 1 ansible ansible 64 Jul 22 14:15 1 -> /home/ansible/demo-flux/rapport.out
l-wx------. 1 ansible ansible 64 Jul 22 14:15 2 -> /home/ansible/demo-flux/defauts.err
lr-x------. 1 ansible ansible 64 Jul 22 14:15 3 -> /proc/13792/fd
```

Le descripteur `1` (sortie standard) pointe sur `rapport.out`, le `2` (sortie
d'erreur) sur `defauts.err`. Sans redirection, les deux pointeraient sur le
terminal. Le `0` est l'entrée standard, le `3` est un descripteur temporaire
ouvert par `ls` pour lire le répertoire. `defauts.err` est resté vide : la
commande n'a produit aucune erreur.

### `>` écrase, `>>` ajoute

```bash
grep OK releve.txt > alertes.out
cat alertes.out
```

```text
2026-07-20 OK sauvegarde quotidienne
2026-07-21 OK sauvegarde quotidienne
2026-07-22 OK sauvegarde quotidienne
```

Un second `>` sur le même fichier ne complète pas le précédent, il remplace tout :

```bash
grep WARN releve.txt > alertes.out
cat alertes.out
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
```

Les trois lignes `OK` ont disparu. Avec `>>`, elles seraient venues s'ajouter :

```bash
grep OK releve.txt >> alertes.out
cat alertes.out
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
2026-07-20 OK sauvegarde quotidienne
2026-07-21 OK sauvegarde quotidienne
2026-07-22 OK sauvegarde quotidienne
```

L'entrée standard se redirige avec `<`, et le résultat n'est pas tout à fait le
même qu'un argument :

```bash
wc -l releve.txt      # 5 releve.txt
wc -l < releve.txt    # 5
```

Dans le premier cas `wc` connaît le nom du fichier et l'affiche, dans le second
il lit un flux anonyme et ne sort que le nombre. Quand on veut un fichier qui ne
contient qu'un nombre, `<` est le bon outil.

### Le piège du `>` : il vide le fichier avant que la commande démarre

C'est le point le plus coûteux de tout le sujet. Le shell ouvre (et tronque) le
fichier de destination **d'abord**, puis lance la commande. Si la commande
échoue, le fichier a quand même été vidé.

```bash
printf 'ligne A\nligne B\n' > important.txt
wc -c < important.txt                       # 16
grep MOTIF-ABSENT-XYZ absent.txt > important.txt
```

```text
grep: absent.txt: No such file or directory
```

```bash
echo $?                 # 2
wc -c < important.txt   # 0
```

Le fichier `important.txt` est vide alors que `grep` n'a rien écrit du tout, et
a même échoué. Pire, cela vaut aussi quand la commande n'existe pas :

```bash
printf 'ligne A\nligne B\n' > important.txt
commande-qui-nexiste-pas > important.txt
```

```text
bash: commande-qui-nexiste-pas: command not found
```

```bash
echo $?                 # 127
wc -c < important.txt   # 0
```

Le shell a tronqué le fichier avant de découvrir que la commande n'existait pas.
Corollaire utile : une redirection **sans commande** vide un fichier.

```bash
printf 'du contenu\n' > jetable.txt
wc -c < jetable.txt   # 11
> jetable.txt
wc -c < jetable.txt   # 0
```

`bash` sait se protéger de ces accidents avec l'option `noclobber`, qui refuse
d'écraser un fichier existant :

```bash
set -o noclobber
echo ecrase > protege.txt
```

```text
bash: protege.txt: cannot overwrite existing file
```

Le code de retour est `1` et le contenu d'origine est intact. Un `>|` force
l'écrasement malgré `noclobber`, et `set +o noclobber` revient au comportement
habituel. C'est une sécurité de session, pas une propriété du fichier : ne
comptez pas dessus sur une machine que vous ne configurez pas.

### Rediriger les erreurs avec `2>`

Une commande qui échoue n'écrit pas sur la sortie standard. Séparons les deux
flux d'une même commande :

```bash
ls releve.txt absent.txt > part1.out 2> part2.err
cat part1.out
```

```text
releve.txt
```

```bash
cat part2.err
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

Retenez les tailles, elles vont servir : 11 octets sur la sortie standard, 58
sur la sortie d'erreur.

### Fusionner les deux flux : l'ordre compte

`2>&1` ne veut pas dire « fusionne stdout et stderr », mais « fais pointer le
descripteur 2 là où pointe le descripteur 1 **à cet instant** ». Comme le shell
traite les redirections de gauche à droite, la place de `2>&1` change tout.

La forme correcte, `2>&1` **après** la redirection de sortie :

```bash
ls releve.txt absent.txt > fusion.out 2>&1
cat fusion.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
releve.txt
```

Les deux flux sont dans le fichier, rien ne reste à l'écran. Notez au passage
que l'erreur précède la sortie normale : dans un fichier fusionné, l'ordre des
lignes n'est pas celui de la ligne de commande. Ici `ls` signale l'accès
impossible avant d'imprimer sa liste, et forcer l'absence de tampon avec
`stdbuf -o0` ne change pas cet ordre.

La forme piégée, `2>&1` **avant** :

```bash
ls releve.txt absent.txt 2>&1 > fusion2.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

```bash
cat fusion2.out
```

```text
releve.txt
```

L'erreur s'est affichée à l'écran, seule la sortie standard est dans le fichier.
Au moment où `2>&1` est traité, le descripteur 1 pointe encore sur le terminal :
le descripteur 2 est donc branché sur le terminal. Le `> fusion2.out` qui suit
ne déplace que le descripteur 1, et le 2 reste où il a été mis.

On peut le prouver en capturant séparément les deux flux du shell appelant :

```bash
bash -c 'ls releve.txt absent.txt 2>&1 > fusion2.out' > echappe.out 2> reste.err
cat echappe.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

```bash
cat reste.err    # vide
```

L'erreur est bien partie sur l'**ancienne** sortie standard, pas sur la sortie
d'erreur. `reste.err` est vide.

### `> f 2> f` n'est pas `&> f`

La tentation est grande d'écrire deux redirections vers le même nom de fichier.
Le résultat est un fichier abîmé.

```bash
ls releve.txt absent.txt > double.out 2> double.out
cat double.out
```

```text
releve.txt
access 'absent.txt': No such file or directory
```

Le message d'erreur a perdu son début, `ls: cannot `, exactement 11 caractères :
la longueur de `releve.txt` plus le passage à la ligne. Les deux `>` ont ouvert
le fichier **deux fois**, chaque ouverture ayant sa propre position d'écriture,
toutes deux à zéro. Les deux flux ont donc écrit l'un par-dessus l'autre.

L'arithmétique le confirme :

```bash
wc -c < double.out    # 58
```

58 octets, la taille du seul message d'erreur, alors que les deux flux
totalisent 69 octets. Onze octets ont été perdus.

`&>` (ou la forme portable `> f 2>&1`) n'ouvre le fichier qu'une fois et fait
partager la même position aux deux descripteurs :

```bash
ls releve.txt absent.txt &> simple.out
wc -c < simple.out    # 69
cat simple.out
```

```text
ls: cannot access 'absent.txt': No such file or directory
releve.txt
```

69 octets : 58 + 11, rien n'est perdu. La version qui ajoute au lieu d'écraser
s'écrit `&>>` ou `>> fichier 2>&1`.

Un détail qui trompe : `ls -l /proc/self/fd` affiche le même fichier de
destination dans les deux cas. Ce qui diffère n'est pas la cible mais la
position d'écriture, et elle n'est visible nulle part. D'où la règle simple :
**jamais deux redirections vers le même fichier**.

### Le tube ne transporte que la sortie standard

Un `|` connecte la sortie standard de gauche à l'entrée standard de droite. La
sortie d'erreur, elle, n'entre pas dans le tube et continue vers l'écran.

```bash
bash -c 'ls releve.txt absent.txt | wc -l' 2> tube-erreurs.err
```

```text
1
```

```bash
cat tube-erreurs.err
```

```text
ls: cannot access 'absent.txt': No such file or directory
```

`wc -l` n'a compté qu'une ligne : l'erreur est passée à côté du tube. C'est ce
qui fait qu'un `commande | grep motif` ne trouvera jamais un message d'erreur, et
qu'un compte fait au bout d'un tube ignore silencieusement les échecs.

Pour faire entrer la sortie d'erreur dans le tube, il faut la fusionner avant :

```bash
ls releve.txt absent.txt 2>&1 | wc -l    # 2
ls releve.txt absent.txt |& wc -l        # 2
```

`|&` est l'abréviation `bash` de `2>&1 |`. Attention à ne pas placer le `2>&1`
du mauvais côté : dans `ls releve.txt absent.txt | grep cannot 2>&1`, la
redirection porte sur `grep`, pas sur `ls`, et `grep` ne trouve rien (code de
retour 1).

Un tube s'enchaîne autant que nécessaire, chaque maillon ne faisant qu'une
chose :

```bash
cut -d' ' -f2 releve.txt | sort | uniq -c
```

```text
      3 OK
      2 WARN
```

`cut` extrait le deuxième champ, `sort` regroupe les valeurs identiques, `uniq -c`
les compte. Aucun fichier intermédiaire n'a été créé.

### Le code de retour d'un tube, `PIPESTATUS` et `pipefail`

Le code de retour d'un tube est celui de sa **dernière** commande. Les échecs
en amont sont donc invisibles.

```bash
grep MOTIF-ABSENT-XYZ releve.txt | wc -l
echo $?
```

```text
0
0
```

`grep` n'a rien trouvé (il rend 1), mais `wc` a parfaitement réussi à compter
zéro ligne, et c'est son code qui est remonté. Un script qui teste `$?` ici
conclura que tout va bien.

`bash` conserve tous les codes dans le tableau `PIPESTATUS` :

```bash
grep MOTIF-ABSENT-XYZ releve.txt | wc -l > /dev/null
echo "${PIPESTATUS[@]}"
```

```text
1 0
```

Le cas le plus parlant est celui d'une commande absente en tête de tube :

```bash
commande-absente-xyz | wc -l > /dev/null
```

```text
bash: commande-absente-xyz: command not found
```

```bash
echo "$? / ${PIPESTATUS[@]}"
```

```text
0 / 127 0
```

Code de retour global `0` alors que la première commande a échoué avec 127.
`PIPESTATUS` doit être lu **immédiatement** : la moindre commande suivante
l'écrase.

L'option `pipefail` corrige le comportement globalement : le tube rend alors le
code du dernier maillon en échec.

```bash
bash -c 'set -o pipefail; grep MOTIF-ABSENT-XYZ releve.txt | wc -l > /dev/null; echo $?'
bash -c '                  grep MOTIF-ABSENT-XYZ releve.txt | wc -l > /dev/null; echo $?'
```

```text
1
0
```

C'est la raison pour laquelle un script sérieux commence souvent par
`set -o pipefail`, en général avec `set -euo pipefail`.

### `tee` : voir et enregistrer en même temps

Une redirection `>` envoie tout dans le fichier et plus rien à l'écran. `tee`
fait les deux : il écrit dans le fichier et recopie sur sa sortie standard.

```bash
grep WARN releve.txt | tee suivi.log
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
```

Le contenu s'est affiché, et `suivi.log` contient exactement les mêmes deux
lignes. `tee` sans option **écrase** le fichier, comme `>` ; `tee -a` ajoute,
comme `>>` :

```bash
grep OK releve.txt | tee -a suivi.log
cat suivi.log
```

```text
2026-07-20 WARN espace disque faible
2026-07-21 WARN certificat bientot expire
2026-07-20 OK sauvegarde quotidienne
2026-07-21 OK sauvegarde quotidienne
2026-07-22 OK sauvegarde quotidienne
```

`tee` est en bout de tube : il n'y voit donc que la sortie standard, comme tout
le reste du tube. Un `commande | tee journal` ne conserve pas les erreurs, sauf
à écrire `commande 2>&1 | tee journal`.

### `sudo` ne s'applique pas à la redirection

Erreur classique : on croit écrire dans un fichier protégé parce que `sudo` est
sur la ligne, et le shell refuse.

```bash
sudo mkdir -p /etc/demo-flux.d
sudo touch /etc/demo-flux.d/reglage.conf     # appartient à root, mode 0644
sudo echo "parametre=1" > /etc/demo-flux.d/reglage.conf
```

```text
bash: /etc/demo-flux.d/reglage.conf: Permission denied
```

Le code de retour est `1`, et rien n'a été écrit. La raison est celle du début
de ce cours : **la redirection est faite par le shell appelant**, qui tourne
sous votre compte. `sudo` n'élève que la commande `echo`, laquelle a déjà perdu
la partie avant de démarrer. Deux façons correctes de s'y prendre :

```bash
echo "parametre=1" | sudo tee /etc/demo-flux.d/reglage.conf
sudo sh -c 'echo parametre=2 > /etc/demo-flux.d/reglage.conf'
```

Les deux rendent `0` et le fichier contient bien la valeur. Dans le premier cas
c'est `tee`, lancé par `sudo`, qui ouvre le fichier ; dans le second c'est un
shell entier qui tourne en root, redirection comprise. `tee` affiche ce qu'il
écrit, d'où le `> /dev/null` habituel quand on ne veut pas de doublon à l'écran,
et `sudo tee -a` pour ajouter une ligne sans écraser le fichier.

### `/dev/null` : jeter la sortie, ou jeter les erreurs

`/dev/null` est un fichier spécial qui avale tout ce qu'on lui envoie. Ce qui
compte est de savoir **quel** flux on y envoie : ce n'est pas du tout le même
geste.

```bash
find /etc -name '*.conf' 2>&1 | wc -l        # 114
find /etc -name '*.conf' 2>/dev/null | wc -l # 99
bash -c "find /etc -name '*.conf' > /dev/null" 2>&1 | wc -l   # 15
```

Sur cette machine et sans privilèges : 114 lignes en tout, dont 99 résultats
utiles et 15 erreurs. `2>/dev/null` jette les 15 erreurs et garde les
résultats ; `> /dev/null` fait exactement l'inverse. Les erreurs jetées
ressemblent à ceci :

```text
find: ‘/etc/pki/rsyslog’: Permission denied
find: ‘/etc/credstore’: Permission denied
```

`> /dev/null 2>&1` jette les deux et ne laisse que le code de retour : c'est la
forme employée dans les tâches planifiées et les tests silencieux.

> Jeter la sortie d'erreur est confortable, mais `2>/dev/null` masque aussi les
> erreurs que vous n'attendiez pas. Sur une commande de diagnostic, préférez
> `2> /tmp/erreurs.err` : vous gardez un résultat lisible et vous pouvez encore
> relire ce qui a échoué.

### Récapitulatif

| Écriture | Effet |
|---|---|
| `cmd > f` | sortie standard dans `f`, `f` est tronqué d'abord |
| `cmd >> f` | sortie standard ajoutée à la fin de `f` |
| `> f` | tronque `f` (ou le crée), sans lancer de commande |
| `cmd < f` | `f` devient l'entrée standard de `cmd` |
| `cmd 2> f` | sortie d'erreur seule dans `f` |
| `cmd 2>> f` | sortie d'erreur ajoutée à `f` |
| `cmd > f 2>&1` | les deux flux dans `f`, portable |
| `cmd &> f` | les deux flux dans `f`, raccourci `bash` |
| `cmd &>> f` | les deux flux ajoutés à `f` |
| `cmd 2>&1 > f` | **piège** : seule la sortie standard va dans `f` |
| `cmd > f 2> f` | **piège** : deux ouvertures, les flux s'écrasent |
| `cmd \| autre` | sortie standard de `cmd` vers l'entrée de `autre` |
| `cmd 2>&1 \| autre` | les deux flux dans le tube (`cmd \|& autre` en `bash`) |
| `cmd \| tee f` | affiche et enregistre (écrase `f`) |
| `cmd \| tee -a f` | affiche et ajoute à `f` |
| `cmd 2>/dev/null` | jette les erreurs, garde le résultat |
| `cmd > /dev/null` | jette le résultat, garde les erreurs |
| `cmd > /dev/null 2>&1` | jette tout, ne garde que le code de retour |

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Le fichier de destination est vide et la commande a échoué | `>` tronque avant de lancer la commande ; utiliser un fichier temporaire puis `mv` |
| Le contenu précédent a disparu | `>` au lieu de `>>`, ou `tee` sans `-a` |
| L'erreur s'affiche encore à l'écran malgré `2>&1` | `2>&1` placé avant la redirection de sortie ; il doit venir après |
| Le fichier fusionné a des lignes tronquées | `> f 2> f` : deux ouvertures indépendantes, écrire `> f 2>&1` ou `&> f` |
| `grep` au bout d'un tube ne trouve pas le message d'erreur | le tube ne transporte que la sortie standard ; ajouter `2>&1` avant le `\|` |
| Un script continue alors qu'une commande du tube a échoué | le tube rend le code du dernier maillon ; lire `PIPESTATUS` ou poser `set -o pipefail` |
| `PIPESTATUS` ne contient pas ce qu'on attend | il est écrasé par la commande suivante ; le copier tout de suite dans une variable |
| `Permission denied` alors que `sudo` est sur la ligne | la redirection est faite par le shell appelant ; passer par `sudo tee` ou `sudo sh -c` |
| `cannot overwrite existing file` | l'option `noclobber` est active ; `>\|` pour forcer, `set +o noclobber` pour la retirer |
| Le fichier ne contient qu'un nombre, alors qu'on voulait aussi le nom | `wc -l < f` masque le nom ; `wc -l f` le conserve |
| Rien ne sort d'un tube | la première commande ne produit rien sur sa sortie standard ; la tester seule |

Pour tout défaire et repartir de zéro :

```bash
rm -rf ~/demo-flux
sudo rm -rf /etc/demo-flux.d
```
