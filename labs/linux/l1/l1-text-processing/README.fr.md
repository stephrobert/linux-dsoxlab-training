# Lab — cut, sort, uniq, sed, awk

## Rappel

[**Transformer du texte sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/transformer-texte/)

`cut -d<sep> -f<N>` extrait la colonne N d'un fichier à champs délimités. `sort`
ordonne les lignes (`-n` pour un tri numérique, `-u` pour dédoublonner au
passage), `uniq -c` compte les répétitions **consécutives** et exige donc une
entrée déjà triée. `tr` convertit ou supprime des caractères depuis l'entrée
standard, `wc` mesure, `sed 's/motif/remplacement/g'` réécrit un flux, et
`awk -F<sep>` raisonne champ par champ et sait calculer. Tous se composent par
tubes, et aucun ne modifie le fichier source.

Guides complémentaires : [trier et compter](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/trier-compter/),
[sed](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/sed/) et [awk](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/awk/).

## Le cours

Les exemples ci-dessous travaillent sur un relevé d'interventions fictif, à
champs séparés par des deux-points : le challenge, lui, vous donnera un autre
fichier, un autre séparateur, d'autres colonnes et d'autres calculs. Le but est
d'apprendre l'enchaînement, pas de recopier une ligne.

Toutes les sorties affichées ont été produites sur Ubuntu 24.04 avec GNU
coreutils 9.4, GNU sed 4.9 et GNU Awk 5.2.1. Le fichier d'exemple étant donné
en entier, vous pouvez rejouer chaque commande et retrouver les mêmes lignes.

### Le décor de démonstration

```bash
mkdir -p /tmp/demo-texte && cd /tmp/demo-texte
cat > interventions.txt <<'EOF'
2026-03-02:reseau:Adrien:35
2026-03-02:stockage:elodie:120
2026-03-03:sauvegarde:bruno:9
2026-03-03:sauvegarde:Adrien:10
2026-03-04:messagerie:Zoe:5
2026-03-04:stockage:elodie:12
2026-03-05:reseau:Émile:90

2026-03-05:reseau:bruno:10
2026-03-06:messagerie:adrien:15
2026-03-07:stockage:Émile:60
2026-03-08:reseau:elodie:120
2026-03-08:sauvegarde:elodie:20
2026-03-09:reseau:Adrien:5

2026-03-10:messagerie:bruno:9
2026-03-11:reseau:Zoe:30
2026-03-12:stockage:adrien:9
2026-03-13:reseau:bruno:12
2026-03-14:sauvegarde:Zoe:35
EOF
```

Le format est `date:service:agent:minutes`. Les deux lignes vides sont
volontaires : les vrais exports en contiennent toujours, et elles se glissent
dans les comptages si on les oublie.

```bash
wc -l interventions.txt      # lignes, lignes vides comprises
grep -c . interventions.txt  # lignes réellement remplies
```

```text
20 interventions.txt
18
```

`wc -l` compte les fins de ligne sans juger du contenu ; `grep -c .` ne retient
que les lignes ayant au moins un caractère. L'écart de deux, ce sont les vides.

### Découper une colonne avec `cut`

`cut` a besoin de deux choses : le délimiteur (`-d`) et le ou les champs (`-f`).

```bash
cut -d: -f2 interventions.txt | head -8
```

```text
reseau
stockage
sauvegarde
sauvegarde
messagerie
stockage
reseau

```

La ligne vide traverse le découpage sans broncher : `cut` ne filtre rien, il
découpe. Plusieurs champs se demandent par une liste (`-f2,4`) ou par une plage
(`-f3-` signifie « du champ 3 jusqu'à la fin »), et `cut` recopie le même
délimiteur en sortie :

```bash
cut -d: -f2,4 interventions.txt | head -4
```

```text
reseau:35
stockage:120
sauvegarde:9
sauvegarde:10
```

### Trier et dédoublonner, et le piège du tri alphabétique

`sort -u` trie et supprime les doublons en une passe. Sur la colonne des
services :

```bash
cut -d: -f2 interventions.txt | sort -u
```

```text

messagerie
reseau
sauvegarde
stockage
```

La première ligne du résultat est vide : pour `sort`, une ligne vide est une
valeur comme une autre. Insérez `grep .` dans le tube pour l'écarter.

Le piège numéro un vient ensuite. Sans option, `sort` compare du **texte** :

```bash
cut -d: -f4 interventions.txt | grep . | sort -u  | tr '\n' ' '   # texte
cut -d: -f4 interventions.txt | grep . | sort -nu | tr '\n' ' '   # nombres
```

```text
10 12 120 15 20 30 35 5 60 9 90
5 9 10 12 15 20 30 35 60 90 120
```

`10` passe avant `9` parce que le caractère `1` précède le caractère `9`. Dès
qu'une colonne contient des nombres, `-n` n'est pas une option de confort. Le
même piège se tend quand on trie le fichier entier sur une colonne, avec `-t`
pour le délimiteur et `-k` pour le champ : `sort -t: -k4 -rn` remonte bien les
interventions de 120 minutes, tandis que `sort -t: -k4 -r` place `90` en tête.

Deuxième piège, moins connu : **la locale change l'ordre**. Le tri suit
`LC_COLLATE`, ici `fr_FR.UTF-8`, qui range majuscules et accents comme un
dictionnaire. `LC_ALL=C` force l'ordre des octets :

```bash
cut -d: -f3 interventions.txt | grep . | sort -u          # fr_FR.UTF-8
```

```text
adrien
Adrien
bruno
elodie
Émile
Zoe
```

```bash
cut -d: -f3 interventions.txt | grep . | LC_ALL=C sort -u # octets ASCII
```

```text
Adrien
Zoe
adrien
bruno
elodie
Émile
```

Mêmes six valeurs, ordre différent : en `C`, toutes les majuscules passent
avant toutes les minuscules, et `Émile` finit dernier parce que ses octets
UTF-8 valent plus que ceux des lettres ASCII. Dans un script dont la sortie est
comparée à un attendu, ou avant un `comm` qui exige deux fichiers triés à
l'identique, fixez `LC_ALL=C` des deux côtés. Notez au passage que `Adrien` et
`adrien` restent deux valeurs distinctes dans les deux ordres : `sort -u`
compare des chaînes, pas des identités (`sort -uf` replie la casse).

### Compter avec `uniq -c`, et pourquoi le tri est obligatoire

`uniq` ne regarde **que la ligne précédente**. Sur des données non triées, il ne
regroupe donc que ce qui se touche :

```bash
cut -d: -f2 interventions.txt | uniq -c | head -8
```

```text
      1 reseau
      1 stockage
      2 sauvegarde     ← les deux seules lignes voisines identiques
      1 messagerie
      1 stockage
      1 reseau
      1
      1 reseau
```

Les occurrences de `reseau` sont comptées une par une parce qu'elles ne se
suivent pas, tandis que les deux `sauvegarde` voisines fusionnent. C'est la
preuve du mécanisme : `uniq` n'a aucune mémoire, il compare des voisins. Il
suffit donc de trier avant pour rendre voisines toutes les valeurs identiques :

```bash
cut -d: -f2 interventions.txt | sort | uniq -c
```

```text
      2
      3 messagerie
      7 reseau
      4 sauvegarde
      4 stockage
```

Le comptage devient exact, et les deux lignes vides apparaissent au grand jour
avec leur propre compteur. L'indentation variable devant les nombres est
normale : `uniq -c` aligne sur la largeur du plus grand compte.

### Le pipeline complet, celui qu'on écrit tous les jours

Ajoutez un second tri, numérique et décroissant, puis `head` pour ne garder que
le haut du classement :

```bash
cut -d: -f2 interventions.txt | grep . | sort | uniq -c | sort -rn | head -3
```

```text
      7 reseau
      4 stockage
      4 sauvegarde
```

Chaque maillon a un rôle et un seul : `cut` isole la colonne, `grep .` jette les
lignes vides, `sort` rend voisines les valeurs identiques, `uniq -c` compte,
`sort -rn` classe du plus fréquent au plus rare, `head -3` coupe. Changez le
seul numéro de champ (`-f3`) et la même ligne classe les agents : `4 elodie`,
`4 bruno`, `3 Zoe`, `3 Adrien`, `2 Émile`, `2 adrien`.

Deux variantes utiles du dernier maillon : `tail` quand c'est le bas du
classement qui vous intéresse, et `wc -l` quand la question est « combien de
valeurs distinctes ? ». Ici, la variante `... | sort -u | wc -l` répond `6`.

### Quand `cut` ne suffit plus : `tr`, `sed` et `awk`

`cut -d' '` découpe sur **un** espace. Face à des colonnes alignées par des
espaces multiples, il renvoie des champs vides :

```bash
printf '%-12s %6s %s\n' serveur-01 12 reseau serveur-2 4 stockage \
  > charges.txt
cut -d' ' -f2 charges.txt | cat -A   # cat -A montre les lignes vides
```

```text
$
$
```

```bash
awk '{print $2}' charges.txt         # séparateur : suites d'espaces
```

```text
12
4
```

`cut` n'a rien trouvé et a rendu deux lignes vides ; `awk` a bon du premier
coup, parce que son séparateur par défaut est « une ou plusieurs espaces ».
L'autre solution consiste à normaliser d'abord avec `tr -s` (squeeze), qui
réduit les répétitions consécutives à une seule occurrence :

```bash
tr -s ' ' < charges.txt | cut -d' ' -f2
```

```text
12
4
```

`tr` sert aussi à réécrire un délimiteur caractère par caractère, et `sed` fait
la même chose par substitution. Le flag `g` de `sed` n'est pas décoratif :

```bash
sed 's/:/|/' interventions.txt | head -2      # sans g
```

```text
2026-03-02|reseau:Adrien:35
2026-03-02|stockage:elodie:120
```

```bash
sed 's/:/|/g' interventions.txt | head -2     # avec g
tr ':' '|' < interventions.txt | head -2      # même résultat, autre outil
```

```text
2026-03-02|reseau|Adrien|35
2026-03-02|stockage|elodie|120
```

Enfin, dès qu'il faut **calculer** sur un champ, `cut` s'arrête et `awk` prend
le relais. `-F` fixe le séparateur, une variable accumule, le bloc `END`
s'exécute après la dernière ligne :

```bash
awk -F: '{total += $4} END {print total}' interventions.txt
awk -F: 'NF {m[$2] += $4} END {for (s in m) print m[s], s}' \
    interventions.txt | sort -rn
```

```text
606
302 reseau
201 stockage
74 sauvegarde
29 messagerie
```

Le garde-fou `NF` ignore les lignes vides (zéro champ). Et comme `awk` ne
garantit pas l'ordre des clés d'un tableau, on repasse par `sort` en sortie.

### Dépannage

| Problème | Cause probable | Solution |
|---|---|---|
| `uniq -c` ne compte que des 1 | Entrée non triée, les identiques ne se touchent pas | Insérer `sort` avant `uniq` |
| `10` classé avant `9` | Tri alphabétique par défaut | Ajouter `-n` (ou `-V` pour des versions) |
| `cut` renvoie des champs vides | Délimiteur absent, ou espaces multiples | Vérifier avec `cat -A`, normaliser par `tr -s ' '`, ou passer à `awk` |
| Une ligne vide dans le résultat | Le fichier source en contient | Filtrer par `grep .` dans le tube |
| Le tri diffère d'une machine à l'autre | `LC_COLLATE` différent | Préfixer par `LC_ALL=C sort` des deux côtés |
| `sort -u` laisse des quasi-doublons | Casse différente | Ajouter `-f` : `sort -uf` |
| `sed` ne remplace qu'une fois par ligne | Flag `g` oublié | `s/motif/remplacement/g` |
| `tr` n'affiche rien | `tr` ne lit pas un fichier passé en argument | Le nourrir par une redirection `< fichier` ou par un tube |
| `awk` : total à `0` | Mauvais séparateur, donc mauvais champ | Contrôler avec `awk -F: '{print $4}'` |
