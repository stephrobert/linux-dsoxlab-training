# Lab — localiser des fichiers avec find

## Rappel

[**find sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/)

`find <chemin> <prédicats>` parcourt une arborescence à partir d'un point de
départ et ne garde que les objets qui satisfont les critères donnés : `-name`
(motif sur le nom), `-type` (nature de l'objet), `-size` (taille), `-perm`
(mode), `-mtime` (date de modification), `-user` (propriétaire). Les critères
posés à la suite se combinent par un **ET** logique. La descente est récursive
par défaut.

## Le cours

Les exemples ci-dessous travaillent sur `/srv/inventaire`, une arborescence de
démonstration que vous fabriquez vous-même, avec l'utilisateur `camille` : le
challenge, lui, vous demandera d'autres chemins, d'autres motifs et d'autres
valeurs. Le but est d'apprendre la méthode et surtout de reconnaître les pièges
de `find`, pas de recopier une ligne.

Toutes les sorties reproduites ici viennent d'un AlmaLinux 10 avec
`find (GNU findutils) 4.10.0`.

### Le décor de démonstration

Fouiller le système réel est le meilleur moyen de ne rien comprendre : les
résultats changent d'une machine à l'autre et les erreurs de permission
brouillent la sortie. On se fabrique donc une arborescence dont on connaît
exactement les tailles, les modes, les propriétaires et les dates.

```bash
sudo useradd -m camille
sudo mkdir -p /srv/inventaire/{rapports,sauvegardes/ancien,scripts,partage}

# des contenus de tailles choisies
sudo sh -c 'head -c 2500  /dev/zero | tr "\0" x > /srv/inventaire/rapports/ventes-2024.csv'
sudo sh -c 'head -c 1500  /dev/zero | tr "\0" v > /srv/inventaire/rapports/export-hebdo.csv'
sudo sh -c 'head -c 120   /dev/zero | tr "\0" y > /srv/inventaire/rapports/ventes-2025.csv'
sudo touch /srv/inventaire/rapports/brouillon.tmp
sudo sh -c 'head -c 30720 /dev/zero | tr "\0" z > /srv/inventaire/sauvegardes/base.sql.bak'
sudo sh -c 'head -c 5120  /dev/zero | tr "\0" w > /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak'
sudo sh -c 'printf "#!/bin/bash\necho collecte\n" > /srv/inventaire/scripts/collecte.sh'
sudo sh -c 'printf "#!/bin/bash\necho purge\n"    > /srv/inventaire/scripts/purge.sh'
sudo sh -c 'printf "ordre du jour\n"     > "/srv/inventaire/notes de reunion.txt"'
sudo sh -c 'printf "boite aux lettres\n" > /srv/inventaire/partage/depot.txt'
sudo ln -sfn /srv/inventaire/rapports /srv/inventaire/lien-rapports
```

Puis les propriétaires et les modes :

```bash
sudo chown -R root:root /srv/inventaire
sudo chown camille:camille /srv/inventaire/sauvegardes/base.sql.bak \
                           /srv/inventaire/scripts/purge.sh

sudo chmod 0755 /srv/inventaire /srv/inventaire/rapports /srv/inventaire/sauvegardes \
                /srv/inventaire/sauvegardes/ancien /srv/inventaire/scripts /srv/inventaire/partage
sudo chmod 0644 /srv/inventaire/rapports/ventes-2024.csv \
                /srv/inventaire/rapports/export-hebdo.csv \
                /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
sudo chmod 0640 /srv/inventaire/rapports/ventes-2025.csv
sudo chmod 0660 /srv/inventaire/rapports/brouillon.tmp
sudo chmod 0400 /srv/inventaire/sauvegardes/base.sql.bak
sudo chmod 0755 /srv/inventaire/scripts/collecte.sh
sudo chmod 0700 /srv/inventaire/scripts/purge.sh
sudo chmod 0604 "/srv/inventaire/notes de reunion.txt"
sudo chmod 0666 /srv/inventaire/partage/depot.txt
```

Enfin les dates de modification, calculées par rapport à l'instant présent pour
que les exemples de `-mtime` donnent le même résultat quel que soit le jour où
vous les jouez. `touch -d` accepte une date arbitraire, il n'y a rien à
attendre :

```bash
sudo touch -d "$(date -d '2 hours ago'  '+%F %T')" /srv/inventaire/rapports/ventes-2025.csv
sudo touch -d "$(date -d '1 day ago'    '+%F %T')" /srv/inventaire/rapports/brouillon.tmp
sudo touch -d "$(date -d '2 days ago'   '+%F %T')" /srv/inventaire/scripts/purge.sh
sudo touch -d "$(date -d '3 days ago'   '+%F %T')" "/srv/inventaire/notes de reunion.txt"
sudo touch -d "$(date -d '4 days ago'   '+%F %T')" /srv/inventaire/rapports/ventes-2024.csv
sudo touch -d "$(date -d '5 days ago'   '+%F %T')" /srv/inventaire/partage/depot.txt
sudo touch -d "$(date -d '7 days ago 12 hours ago' '+%F %T')" /srv/inventaire/rapports/export-hebdo.csv
sudo touch -d "$(date -d '12 days ago'  '+%F %T')" /srv/inventaire/scripts/collecte.sh
sudo touch -d "$(date -d '51 days ago'  '+%F %T')" /srv/inventaire/sauvegardes/base.sql.bak
sudo touch -d "$(date -d '434 days ago' '+%F %T')" /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
```

Voici l'inventaire obtenu, taille en octets, mode octal, propriétaire :

```bash
find /srv/inventaire -type f -printf '%8s  %m  %-8u  %p\n' | sort -k4
```

```text
      14  604  root      /srv/inventaire/notes de reunion.txt
      18  666  root      /srv/inventaire/partage/depot.txt
       0  660  root      /srv/inventaire/rapports/brouillon.tmp
    1500  644  root      /srv/inventaire/rapports/export-hebdo.csv
    2500  644  root      /srv/inventaire/rapports/ventes-2024.csv
     120  640  root      /srv/inventaire/rapports/ventes-2025.csv
    5120  644  root      /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
   30720  400  camille   /srv/inventaire/sauvegardes/base.sql.bak
      26  755  root      /srv/inventaire/scripts/collecte.sh
      23  700  camille   /srv/inventaire/scripts/purge.sh
```

Gardez ce tableau sous les yeux : chaque résultat qui suit se vérifie dessus.

### Un point de départ, puis des prédicats

Sans le moindre critère, `find` affiche tout ce qu'il rencontre, le point de
départ compris :

```bash
find /srv/inventaire
```

```text
/srv/inventaire
/srv/inventaire/rapports
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/sauvegardes
/srv/inventaire/sauvegardes/ancien
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/scripts
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
/srv/inventaire/lien-rapports
```

Deux enseignements dans cette seule sortie. D'abord la récursion est
automatique, `base-2023.sql.bak` est deux niveaux plus bas. Ensuite l'ordre
n'est **pas** alphabétique : c'est l'ordre de parcours du système de fichiers.
Si vous avez besoin d'une liste triée, passez explicitement par `| sort`.

### Chercher par nom : `-name`, `-iname`, `-path`

```bash
find /srv/inventaire -name '*.csv'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
```

Les quotes autour du motif ne sont pas décoratives. Sans elles, c'est le shell
qui développe le glob **avant** de lancer `find`, et la commande part en erreur
dès qu'il y a plus d'un fichier correspondant dans le répertoire courant :

```bash
cd /srv/inventaire/rapports
find . -name *.csv
```

```text
find: paths must precede expression: `ventes-2024.csv'
find: possible unquoted pattern after predicate `-name'?
```

Le message est explicite si on sait le lire : `find` a reçu trois noms de
fichiers là où il attendait un seul motif. Prenez l'habitude de quoter, toujours.

`-iname` fait la même chose sans distinguer majuscules et minuscules :

```bash
find /srv/inventaire -iname '*.CSV'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
```

Piège classique : **`-name` ne voit que le dernier composant du chemin**, jamais
les répertoires qui mènent au fichier. Un motif contenant un `/` ne correspond
donc à rien :

```bash
find /srv/inventaire -name 'rapports/*'
```

```text
```

Rien, et pourtant le code retour est `0` : `find` n'a pas échoué, il n'a
simplement rien trouvé. Pour filtrer sur le chemin complet, c'est `-path` qu'il
faut, et son motif doit couvrir tout le chemin :

```bash
find /srv/inventaire -path '*/rapports/*.csv'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
```

### Filtrer par type : `-type`

| Valeur | Signification |
|---|---|
| `f` | fichier ordinaire |
| `d` | répertoire |
| `l` | lien symbolique |

```bash
find /srv/inventaire -type d
```

```text
/srv/inventaire
/srv/inventaire/rapports
/srv/inventaire/sauvegardes
/srv/inventaire/sauvegardes/ancien
/srv/inventaire/scripts
/srv/inventaire/partage
```

```bash
find /srv/inventaire -type l
```

```text
/srv/inventaire/lien-rapports
```

Le lien symbolique n'apparaît **pas** dans `-type f` : un lien n'est pas un
fichier ordinaire, même s'il pointe vers un répertoire plein de fichiers. Par
défaut `find` ne traverse pas les liens. L'option `-L`, placée **avant** le
chemin de départ, l'y oblige, et la même arborescence est alors visitée deux
fois :

```bash
find -L /srv/inventaire -name '*.csv'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/lien-rapports/ventes-2024.csv
/srv/inventaire/lien-rapports/export-hebdo.csv
/srv/inventaire/lien-rapports/ventes-2025.csv
```

Trois fichiers, six lignes. Sur un système réel, `-L` sur un lien qui remonte
vers un parent fait tourner `find` en rond, et il finit par se plaindre d'une
boucle. Ne l'activez que quand vous savez pourquoi.

### Filtrer par taille : `-size`, et son arrondi

Le suffixe donne l'unité :

| Suffixe | Unité |
|---|---|
| `c` | octets |
| `k` | Kio (1024 octets) |
| `M` | Mio |
| `G` | Gio |

Le préfixe donne le sens de la comparaison : `+` pour « strictement plus »,
`-` pour « strictement moins », rien du tout pour « exactement ».

```bash
find /srv/inventaire -type f -size +2000c -printf '%s %p\n'
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
5120 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
30720 /srv/inventaire/sauvegardes/base.sql.bak
```

La borne est **stricte** : un fichier de 2500 octets ne satisfait pas
`-size +2500c`.

```bash
find /srv/inventaire -type f -size +2500c -printf '%s %p\n'
```

```text
5120 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
30720 /srv/inventaire/sauvegardes/base.sql.bak
```

`ventes-2024.csv` a disparu. Sans préfixe, on demande l'égalité exacte :

```bash
find /srv/inventaire -type f -size 2500c -printf '%s %p\n'
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
```

Vient maintenant le piège qui surprend tout le monde. **Avec toute unité autre
que `c`, `find` arrondit la taille au bloc supérieur avant de comparer.** Un
fichier de 1 octet compte donc pour un bloc de 1 Kio, et pour un bloc de 1 Mio.
Conséquence :

```bash
find /srv/inventaire -type f -size -1M -printf '%s %p\n'
```

```text
0 /srv/inventaire/rapports/brouillon.tmp
```

Un seul résultat, alors que neuf fichiers sur dix font moins de 1 Mio.
« Strictement moins de 1 bloc de 1 Mio » ne peut vouloir dire que « zéro bloc »,
c'est-à-dire un fichier vide. Si vous cherchez les fichiers de moins d'un Mio,
écrivez `-size -1048576c`, ou acceptez la borne au bloc près.

Le même arrondi explique ceci :

```bash
find /srv/inventaire -type f -size 3k -printf '%s %p\n'
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
```

2500 octets, c'est 2,44 Kio, arrondi à 3 blocs. Le fichier répond donc à
`-size 3k` et pas à `-size 2k`. Retenez la règle : **`c` est la seule unité qui
compare la taille réelle**, toutes les autres comparent un nombre de blocs
arrondi vers le haut.

Pour les fichiers vides, `-empty` est plus lisible que `-size 0c` et donne le
même résultat :

```bash
find /srv/inventaire -type f -empty -printf '%s %p\n'
```

```text
0 /srv/inventaire/rapports/brouillon.tmp
```

### Filtrer par date : `-mtime` et ses tranches de 24 heures

C'est le prédicat le plus souvent mal compris. `-mtime n` ne parle pas de
« jours calendaires » mais de **tranches de 24 heures**, et le calcul jette la
partie fractionnaire : `find` divise l'âge du fichier par 86400 secondes et
tronque.

- `-mtime -7` : âge tronqué **inférieur** à 7, donc modifié il y a moins de
  7 fois 24 heures ;
- `-mtime +7` : âge tronqué **supérieur** à 7, donc au moins 8 fois 24 heures ;
- `-mtime 7` : âge tronqué **égal** à 7, la tranche entre 7 et 8 fois 24 heures.

Nos fichiers, avec leurs âges :

```text
2025-05-14  base-2023.sql.bak   434 jours
2026-06-01  base.sql.bak         51 jours
2026-07-10  collecte.sh          12 jours
2026-07-15  export-hebdo.csv      7 jours et 12 heures
2026-07-17  depot.txt             5 jours
2026-07-18  ventes-2024.csv       4 jours
2026-07-19  notes de reunion.txt  3 jours
2026-07-20  purge.sh              2 jours
2026-07-21  brouillon.tmp         1 jour
2026-07-22  ventes-2025.csv       2 heures
```

```bash
find /srv/inventaire -type f -mtime -7
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
```

```bash
find /srv/inventaire -type f -mtime +7
```

```text
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/scripts/collecte.sh
```

Six fichiers d'un côté, trois de l'autre : il en manque un sur dix.
`export-hebdo.csv`, âgé de 7 jours et demi, n'est ni dans `-mtime -7` ni dans
`-mtime +7`. Il vit dans le trou entre les deux :

```bash
find /srv/inventaire -type f -mtime 7
```

```text
/srv/inventaire/rapports/export-hebdo.csv
```

> `-mtime -7` et `-mtime +7` ne sont donc **pas** complémentaires. Écrire
> `-mtime +7` en pensant « tout ce qui n'a pas été modifié cette semaine »
> laisse systématiquement passer une journée entière de fichiers. Si vous voulez
> vraiment le complémentaire de `-mtime -7`, écrivez `-not -mtime -7`.

Quand la granularité de la journée ne suffit pas, `-mmin` compte en minutes :

```bash
find /srv/inventaire -type f -mmin -180
```

```text
/srv/inventaire/rapports/ventes-2025.csv
```

Et `-newer` compare à un fichier de référence, ce qui évite tout calcul :

```bash
find /srv/inventaire -type f -newer /srv/inventaire/rapports/ventes-2024.csv
```

```text
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/scripts/purge.sh
/srv/inventaire/notes de reunion.txt
```

Le fichier de référence lui-même est exclu : la comparaison est stricte.

### Filtrer par propriétaire : `-user`, `-group`

```bash
find /srv/inventaire -user camille -printf '%u:%g  %p\n'
```

```text
camille:camille  /srv/inventaire/sauvegardes/base.sql.bak
camille:camille  /srv/inventaire/scripts/purge.sh
```

`-group` fonctionne de la même façon sur le groupe propriétaire. Les deux
acceptent aussi bien un nom qu'un UID ou un GID numérique, ce qui rend service
quand le compte vient d'être supprimé. Sur un répertoire d'essai avec un compte
`zoe` d'UID 1002 :

```bash
find /srv/verif -user 1002 -printf '%u %p\n'
```

```text
zoe /srv/verif/a.txt
```

Supprimez le compte, et le fichier devient orphelin : plus aucun nom ne
correspond à son UID. `-nouser` et `-nogroup` sont là pour les retrouver, et
c'est une recherche à faire après tout ménage de comptes.

```bash
sudo userdel -r zoe
find /srv/verif -nouser -printf '%U:%G %p\n'
```

```text
1002:1002 /srv/verif/a.txt
```

### Filtrer par permissions : les trois formes de `-perm`

C'est ici que se joue la différence entre savoir la commande et savoir s'en
servir. `-perm` a trois syntaxes qui ne veulent pas du tout dire la même chose.

| Écriture | Signification |
|---|---|
| `-perm 644` | le mode vaut **exactement** 644 |
| `-perm -644` | **tous** les bits de 644 sont présents, les autres sont libres |
| `-perm /644` | **au moins un** des bits de 644 est présent |

Sur notre arborescence, l'égalité stricte :

```bash
find /srv/inventaire -type f -perm 644 -printf '%m %p\n'
```

```text
644 /srv/inventaire/rapports/ventes-2024.csv
644 /srv/inventaire/rapports/export-hebdo.csv
644 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
```

Le tiret change tout :

```bash
find /srv/inventaire -type f -perm -644 -printf '%m %p\n'
```

```text
644 /srv/inventaire/rapports/ventes-2024.csv
644 /srv/inventaire/rapports/export-hebdo.csv
644 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
755 /srv/inventaire/scripts/collecte.sh
666 /srv/inventaire/partage/depot.txt
```

`755` et `666` arrivent, car tous deux contiennent bien `rw` pour le
propriétaire, `r` pour le groupe et `r` pour les autres, plus d'autres bits par
dessus. En revanche `604` reste dehors : il lui manque le `r` du groupe.

La barre oblique est le « ou » :

```bash
find /srv/inventaire -type f -perm /044 -printf '%m %p\n'
```

```text
644 /srv/inventaire/rapports/ventes-2024.csv
644 /srv/inventaire/rapports/export-hebdo.csv
640 /srv/inventaire/rapports/ventes-2025.csv
660 /srv/inventaire/rapports/brouillon.tmp
644 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
755 /srv/inventaire/scripts/collecte.sh
666 /srv/inventaire/partage/depot.txt
604 /srv/inventaire/notes de reunion.txt
```

`/044` demande « lisible par le groupe **ou** par les autres » : `640` passe par
le groupe, `604` par les autres. Seuls `400` et `700`, illisibles pour qui n'est
pas propriétaire, restent en dehors. La même valeur en mode exact ne renvoie
évidemment rien, aucun fichier n'ayant précisément le mode `044` :

```bash
find /srv/inventaire -type f -perm 044 -printf '%m %p\n'
```

```text
```

> Un mode exact est très rarement ce que vous voulez pour un audit : il faut que
> les neuf bits coïncident. Pour chercher un risque, c'est `-perm -` ou
> `-perm /` qu'il faut. Pour vérifier une consigne précise, c'est le mode exact.

Les deux usages d'audit qui reviennent à l'examen comme en production. Les
fichiers accessibles en écriture à tout le monde :

```bash
find /srv/inventaire -type f -perm -002 -printf '%m %p\n'
```

```text
666 /srv/inventaire/partage/depot.txt
```

Et les binaires SUID, à connaître parce que ce sont eux qui s'exécutent avec les
droits de leur propriétaire. Ici sur le système réel, en lecture seule :

```bash
find /usr/bin -type f -perm -4000
```

```text
/usr/bin/umount
/usr/bin/mount
/usr/bin/chfn
/usr/bin/chage
/usr/bin/gpasswd
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/crontab
/usr/bin/su
/usr/bin/pkexec
/usr/bin/sudo
```

`-perm` accepte aussi la notation symbolique de `chmod`, souvent plus lisible :
`-perm -u=x` trouve ce qui est exécutable par son propriétaire, `-perm -g=w` ce
qui est modifiable par le groupe.

```bash
find /srv/inventaire -type f -perm -g=w -printf '%m %p\n'
```

```text
660 /srv/inventaire/rapports/brouillon.tmp
666 /srv/inventaire/partage/depot.txt
```

### Combiner les critères

Deux prédicats à la suite sont reliés par un ET implicite :

```bash
find /srv/inventaire -type f -name '*.bak' -size +10k -printf '%s %p\n'
```

```text
30720 /srv/inventaire/sauvegardes/base.sql.bak
```

Le OU s'écrit `-o`, et il exige des parenthèses, elles-mêmes protégées du shell
par une barre oblique inverse. Sans elles, la précédence joue contre vous : le
ET est prioritaire, donc `-type f -name '*.csv' -o -name '*.sh'` se lit
« (fichier ordinaire ET nom en `.csv`) OU nom en `.sh` », et le filtre `-type f`
ne s'applique plus au second terme. Avec un répertoire nommé `archives.sh` dans
l'arborescence :

```bash
find /srv/inventaire -type f -name '*.csv' -o -name '*.sh'
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/sauvegardes/archives.sh
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
```

Le répertoire `archives.sh` s'est invité. Avec les parenthèses, il disparaît :

```bash
find /srv/inventaire -type f \( -name '*.csv' -o -name '*.sh' \)
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
```

La négation s'écrit `-not` ou `!` :

```bash
find /srv/inventaire -type f -not -name '*.csv'
```

```text
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
```

### Limiter la descente et faire taire les erreurs

`-maxdepth` borne la profondeur, `-mindepth` fixe un plancher. Profondeur 1, ce
sont les entrées directes du point de départ :

```bash
find /srv/inventaire -maxdepth 1 -type f
```

```text
/srv/inventaire/notes de reunion.txt
```

Ces deux options sont **globales** : leur place dans la ligne ne change pas leur
effet, mais `find` vous rappelle à l'ordre si vous les écrivez après un test.
Depuis un terminal interactif :

```bash
find /srv/inventaire -type f -maxdepth 1
```

```text
find: warning: you have specified the global option -maxdepth after the argument -type, but global options are not positional, i.e., -maxdepth affects tests specified before it as well as those specified after it.  Please specify global options before other arguments.
/srv/inventaire/notes de reunion.txt
```

Le résultat est correct, seul l'avertissement diffère. À noter : cet
avertissement n'apparaît que si l'entrée standard est un terminal. Dans un
script, il reste muet, ce qui n'aide pas à repérer l'erreur. Écrivez les options
globales en premier, par principe.

Pour couper une branche entière, `-prune` est le bon outil. Sa forme canonique
surprend, mais elle se lit : « si le chemin est celui-là, l'élaguer, **sinon**
afficher ce qui satisfait le reste ».

```bash
find /srv/inventaire -path /srv/inventaire/sauvegardes -prune -o -type f -print
```

```text
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
/srv/inventaire/partage/depot.txt
/srv/inventaire/notes de reunion.txt
```

Le `-print` final est obligatoire ici : dès qu'une action explicite apparaît
dans l'expression, `find` n'ajoute plus l'affichage implicite.

Dernier point, les erreurs. Lancé par un compte non privilégié sur une
arborescence système, `find` déverse des `Permission denied` sur la sortie
d'erreur, mêlés au résultat :

```bash
find /etc -name 'shadow'
```

```text
find: ‘/etc/pki/rsyslog’: Permission denied
find: ‘/etc/credstore’: Permission denied
find: ‘/etc/credstore.encrypted’: Permission denied
find: ‘/etc/audit/plugins.d’: Permission denied
/etc/shadow
```

Ces lignes partent sur le canal 2, on les écarte donc sans toucher au résultat :

```bash
find /etc -name 'shadow' 2>/dev/null
```

```text
/etc/shadow
```

### Agir sur les résultats

`-exec` exécute une commande pour chaque correspondance, `{}` étant remplacé par
le chemin trouvé. Le terminateur change tout.

Avec `\;`, une exécution par fichier :

```bash
sudo find /srv/inventaire -type f -name '*.csv' -exec wc -c {} \;
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
1500 /srv/inventaire/rapports/export-hebdo.csv
120 /srv/inventaire/rapports/ventes-2025.csv
```

Avec `+`, les chemins sont accumulés et passés en une seule fois :

```bash
sudo find /srv/inventaire -type f -name '*.csv' -exec wc -c {} +
```

```text
2500 /srv/inventaire/rapports/ventes-2024.csv
1500 /srv/inventaire/rapports/export-hebdo.csv
 120 /srv/inventaire/rapports/ventes-2025.csv
4120 total
```

La ligne `total` prouve à elle seule que `wc` n'a été lancé qu'une fois. On peut
le rendre encore plus visible en affichant le PID du processus lancé :

```bash
find /srv/inventaire -type f -name '*.csv' -exec sh -c 'echo pid=$$' \;
```

```text
pid=12334
pid=12335
pid=12336
```

```bash
find /srv/inventaire -type f -name '*.csv' -exec sh -c 'echo pid=$$' sh {} +
```

```text
pid=12338
```

Trois processus contre un. Sur trois fichiers c'est anecdotique, sur cinquante
mille c'est la différence entre quelques secondes et plusieurs minutes.
Préférez `+` chaque fois que la commande accepte plusieurs arguments ;
gardez `\;` quand elle n'en prend qu'un, ou quand `{}` doit apparaître ailleurs
qu'en fin de ligne.

Reste le problème des noms de fichiers contenant des espaces. La boucle naïve
que tout le monde écrit une fois dans sa vie découpe le nom en morceaux :

```bash
for f in $(find /srv/inventaire -maxdepth 1 -type f); do echo "[$f]"; done
```

```text
[/srv/inventaire/notes]
[de]
[reunion.txt]
```

Un fichier, trois « chemins », dont aucun n'existe. La parade est `-print0`, qui
sépare les résultats par un octet nul au lieu d'un saut de ligne, associé à
`xargs -0` qui sait les relire :

```bash
find /srv/inventaire -maxdepth 1 -type f -print0 | xargs -0 -I{} echo "[{}]"
```

```text
[/srv/inventaire/notes de reunion.txt]
```

`-exec` ne souffre pas de ce défaut : il passe les chemins directement, sans
jamais les faire relire par un shell. C'est une raison de plus de le préférer.

Deux actions d'affichage complètent le tableau. `-printf` compose une ligne sur
mesure (`%s` la taille, `%m` le mode octal, `%u` le propriétaire, `%p` le
chemin, `%TY-%Tm-%Td` la date de modification) :

```bash
find /srv/inventaire -type f -printf '%8s  %TY-%Tm-%Td  %m  %-8u  %p\n' | sort -k5
```

```text
      14  2026-07-19  604  root      /srv/inventaire/notes de reunion.txt
      18  2026-07-17  666  root      /srv/inventaire/partage/depot.txt
       0  2026-07-21  660  root      /srv/inventaire/rapports/brouillon.tmp
    1500  2026-07-15  644  root      /srv/inventaire/rapports/export-hebdo.csv
    2500  2026-07-18  644  root      /srv/inventaire/rapports/ventes-2024.csv
     120  2026-07-22  640  root      /srv/inventaire/rapports/ventes-2025.csv
    5120  2025-05-14  644  root      /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
   30720  2026-06-01  400  camille   /srv/inventaire/sauvegardes/base.sql.bak
      26  2026-07-10  755  root      /srv/inventaire/scripts/collecte.sh
      23  2026-07-20  700  camille   /srv/inventaire/scripts/purge.sh
```

Et `-ls` produit directement un affichage détaillé, sans passer par une commande
externe :

```bash
find /srv/inventaire -type f -name '*.bak' -ls
```

```text
  8590673      8 -rw-r--r--   1 root     root         5120 May 14  2025 /srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
   379150     32 -r--------   1 camille  camille     30720 Jun  1 13:40 /srv/inventaire/sauvegardes/base.sql.bak
```

Les deux premières colonnes sont le numéro d'inode et la place réellement
occupée sur le disque en blocs, deux informations que `ls -l` ne donne pas.

### Supprimer, avec les précautions qui vont avec

> Les commandes de cette section détruisent des fichiers. Ne les jouez que sur
> une arborescence jetable, jamais depuis `/` ni depuis un répertoire système.
> La règle absolue : on lance d'abord la recherche seule, on lit la liste, et
> seulement ensuite on ajoute l'action.

Un bac à sable :

```bash
mkdir -p /tmp/bac/sous
touch /tmp/bac/a.tmp /tmp/bac/facture.pdf /tmp/bac/sous/b.tmp
```

D'abord regarder :

```bash
find /tmp/bac -type f -name '*.tmp'
```

```text
/tmp/bac/sous/b.tmp
/tmp/bac/a.tmp
```

La liste est celle attendue, on ajoute `-delete` :

```bash
find /tmp/bac -type f -name '*.tmp' -delete
find /tmp/bac
```

```text
/tmp/bac
/tmp/bac/sous
/tmp/bac/facture.pdf
```

`-exec rm {} +` fait exactement la même chose et convient quand `-delete` n'est
pas disponible. Sur un second bac à sable identique :

```bash
mkdir -p /tmp/bac3/sous
touch /tmp/bac3/a.tmp /tmp/bac3/facture.pdf /tmp/bac3/sous/b.tmp
find /tmp/bac3 -type f -name '*.tmp' -exec rm {} +
find /tmp/bac3
```

```text
/tmp/bac3
/tmp/bac3/sous
/tmp/bac3/facture.pdf
```

Maintenant l'accident. `-delete` est une **action**, pas un filtre, et `find`
évalue son expression de gauche à droite. Placée avant le nom, elle s'applique à
tout ce que le parcours rencontre, c'est-à-dire à l'arborescence entière :

```bash
mkdir -p /tmp/bac2/sous
touch /tmp/bac2/a.tmp /tmp/bac2/facture.pdf /tmp/bac2/sous/b.tmp
find /tmp/bac2 -delete -name '*.tmp'
find /tmp/bac2
```

```text
find: ‘/tmp/bac2’: No such file or directory
```

Le répertoire de départ lui-même a été supprimé, avec tout son contenu, y
compris `facture.pdf` qui n'avait rien demandé. Aucune erreur n'est signalée par
la commande fautive : elle a fait ce qu'on lui a écrit. Retenez que **`-delete`
se place toujours en dernier**, après tous les filtres.

Quand le doute persiste, `-ok` se comporte comme `-exec` mais demande
confirmation pour chaque fichier avant d'agir.

### `locate` : l'index, rapide mais décalé

`find` fouille le disque à chaque appel. `locate` interroge une base de données
construite à l'avance, ce qui est incomparablement plus rapide et
incomparablement moins fiable.

```bash
sudo dnf install -y plocate
sudo updatedb
locate inventaire
```

```text
/srv/inventaire
/srv/inventaire/lien-rapports
/srv/inventaire/notes de reunion.txt
/srv/inventaire/partage
/srv/inventaire/rapports
/srv/inventaire/sauvegardes
/srv/inventaire/scripts
/srv/inventaire/partage/depot.txt
/srv/inventaire/rapports/brouillon.tmp
/srv/inventaire/rapports/export-hebdo.csv
/srv/inventaire/rapports/ventes-2024.csv
/srv/inventaire/rapports/ventes-2025.csv
/srv/inventaire/sauvegardes/ancien
/srv/inventaire/sauvegardes/base.sql.bak
/srv/inventaire/sauvegardes/ancien/base-2023.sql.bak
/srv/inventaire/scripts/collecte.sh
/srv/inventaire/scripts/purge.sh
```

`locate` liste indifféremment les fichiers et les répertoires, et son motif est
cherché n'importe où dans le chemin, pas seulement dans le nom.

Le défaut se démontre en trois lignes. On crée un fichier, puis on le cherche
avec les deux outils :

```bash
sudo touch /srv/inventaire/rapports/tout-neuf.csv
locate tout-neuf.csv          # code retour 1, aucune ligne
find /srv/inventaire -name 'tout-neuf.csv'
```

```text
/srv/inventaire/rapports/tout-neuf.csv
```

`locate` ne voit rien, `find` le trouve immédiatement. Après un `sudo updatedb`,
`locate` le trouve à son tour. L'index est reconstruit une fois par jour par un
minuteur systemd, jamais en temps réel :

```bash
systemctl cat plocate-updatedb.timer
```

```text
# /usr/lib/systemd/system/plocate-updatedb.timer
[Unit]
Description=Update the plocate database daily

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
AccuracySec=6h
Persistent=true
```

**Si la fraîcheur compte, c'est `find` et rien d'autre.** `locate -i` ignore la
casse, comme `-iname`.

> Le guide compagnon indique d'installer `mlocate` sur RHEL et dérivés. Sur
> AlmaLinux 10, ce paquet n'existe plus : `dnf info mlocate` répond `No matching
> Packages to list`, et c'est `plocate` qui est fourni dans le dépôt `baseos`.
> `dnf provides '*/bin/locate'` le confirme.

### `grep` : chercher dans le contenu, et le combiner à `find`

`find` et `locate` cherchent des **noms** de fichiers, `grep` cherche du
**texte** à l'intérieur. `-r` rend la recherche récursive, `-n` ajoute le numéro
de ligne, `-i` ignore la casse, `-l` n'affiche que les noms de fichiers
correspondants et `-v` inverse la sélection.

Les deux outils se marient très bien : `find` sélectionne sur des critères
système que `grep` ne sait pas voir (taille, âge, mode, propriétaire), `grep`
tranche ensuite sur le contenu.

```bash
sudo find /srv/inventaire -type f -name '*.sh' -exec grep -Hn 'echo' {} +
```

```text
/srv/inventaire/scripts/collecte.sh:2:echo collecte
/srv/inventaire/scripts/purge.sh:2:echo purge
```

`-H` force l'affichage du nom de fichier, utile car `grep` l'omet quand il ne
reçoit qu'un seul argument, ce qui arrive avec `-exec ... \;` et rend la sortie
ambiguë.

### Quelle commande pour quel besoin

| Besoin | Commande |
|---|---|
| Trouver par nom, résultat certain et à jour | `find /chemin -name 'motif'` |
| Trouver par nom, résultat immédiat | `locate motif` |
| Filtrer par taille, type, date, mode, propriétaire | `find` avec `-size`, `-type`, `-mtime`, `-perm`, `-user` |
| Chercher du texte dans les fichiers | `grep 'motif' fichier` |
| Chercher du texte dans toute une arborescence | `grep -r 'motif' /chemin/` |
| Croiser un critère système et un contenu | `find … -exec grep -Hn 'motif' {} +` |

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `paths must precede expression` | le glob n'était pas quoté, le shell l'a développé |
| Rien ne sort alors que le fichier existe | motif avec un `/` passé à `-name` : utiliser `-path` |
| Un fichier attendu manque avec `-size -1M` | arrondi au bloc supérieur : passer en octets avec `c` |
| Un fichier attendu manque avec `-mtime +N` | il est dans la tranche `-mtime N`, ni `+N` ni `-N` |
| `-perm` ne renvoie presque rien | mode exact demandé : essayer `-perm -mode` |
| `-perm` renvoie presque tout | `-perm /mode` suffit d'un seul bit : essayer `-perm -mode` |
| Le `-type f` semble ignoré | un `-o` sans parenthèses a coupé l'expression en deux |
| `Permission denied` en pagaille | rediriger le canal d'erreur : `2>/dev/null` |
| `warning: … global option -maxdepth after the argument` | écrire `-maxdepth` avant les tests |
| Un nom avec espace éclate en plusieurs entrées | `$(find …)` relu par le shell : utiliser `-print0` avec `xargs -0`, ou `-exec` |
| Le lien symbolique n'apparaît pas dans `-type f` | c'est normal : `-type l`, ou `-L` pour traverser |
| `find … -prune` n'affiche rien | il manque le `-print` final après le `-o` |
| `locate` ne trouve pas un fichier récent | l'index est décalé : `sudo updatedb`, ou utiliser `find` |
| Trop de résultats | resserrer le point de départ ou ajouter `-maxdepth` |

Pour tout défaire et rendre la machine à son état d'origine :

```bash
sudo rm -rf /srv/inventaire /srv/verif /tmp/bac /tmp/bac2 /tmp/bac3
sudo userdel -r camille
sudo dnf remove -y plocate      # si vous l'aviez installé pour la démonstration
```
