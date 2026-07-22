# Lab — tar, gzip, bzip2

## Rappel

[**Archives et compression sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/)

`tar` regroupe des fichiers dans une seule archive ; la compression est une
option à part : `z` pour gzip, `j` pour bzip2. Verbes courants : `c` créer, `t`
lister, `x` extraire. `-f` nomme le fichier, `-C` fixe le répertoire
d'extraction, et nommer un membre n'extrait que celui-ci.

## Le cours

Les exemples ci-dessous travaillent sur un répertoire `inventaire/` contenant
`stock.csv`, `fournisseurs.json` et `historique.log` : le challenge, lui, vous
demandera d'autres fichiers, d'autres archives et d'autres noms. Le but est
d'apprendre la méthode, pas de recopier une ligne. Toutes les sorties
reproduites ici viennent d'une AlmaLinux 10 avec GNU tar 1.35.

### Archiver n'est pas compresser

Le guide pose la distinction : **archiver** regroupe plusieurs fichiers en un
seul, **compresser** réduit la taille. Ce sont deux opérations différentes, et
`tar` seul ne fait que la première. La démonstration tient en quatre commandes :

```bash
du -sb inventaire
tar cf stock.tar inventaire
tar czf stock.tar.gz inventaire
ls -l stock.tar stock.tar.gz
```

```text
162	inventaire
-rw-r--r--. 1 ansible ansible 10240 Jul 22 14:20 stock.tar
-rw-r--r--. 1 ansible ansible   338 Jul 22 14:20 stock.tar.gz
```

162 octets de données donnent une archive `tar` de **10 240 octets**. Elle est
soixante fois plus grosse que son contenu : `tar` écrit un en-tête de 512
octets par membre, puis complète par des blocs de zéros. La taille finale
s'arrondit toujours à un multiple de 10 240 octets, ce qu'on vérifie en
archivant des répertoires de tailles croissantes :

```text
  1 fichier   -> 10240 octets
  5 fichiers  -> 10240 octets
 30 fichiers  -> 40960 octets
```

Ajoutez `z` et le fichier retombe à 338 octets : c'est la compression, pas
l'archivage, qui fait maigrir.

La même surprise se produit sur un fichier isolé :

```bash
ls -l historique.log
gzip -k historique.log
ls -l historique.log.gz
```

```text
-rw-r--r--. 1 ansible ansible 55 Jul 22 14:16 historique.log
-rw-r--r--. 1 ansible ansible 78 Jul 22 14:16 historique.log.gz
```

55 octets compressés en 78. Sur un contenu minuscule, l'en-tête du format
`gzip` coûte plus cher que ce qu'il fait gagner. La compression ne devient
rentable qu'à partir de quelques kilo-octets.

`gzip -k` conserve l'original ; **sans `-k`, `gzip` remplace le fichier** et
l'original disparaît. C'est le point que souligne le guide, et il vaut aussi
pour `bzip2`, `xz` et `zstd`. Pour revenir en arrière : `gunzip fichier.gz`, ou
`gzip -d fichier.gz`.

### Les trois verbes, et ce que l'archive contient vraiment

`c` crée, `t` liste, `x` extrait. Ces trois verbes s'excluent : une commande
`tar` en contient exactement un. `-f` nomme le fichier d'archive et doit être
suivi immédiatement de ce nom.

Lister est l'opération à faire **avant** toute extraction, parce qu'elle ne
touche rien sur le disque :

```bash
tar tf stock.tar
```

```text
inventaire/
inventaire/stock.csv
inventaire/fournisseurs.json
inventaire/historique.log
```

Avec `v`, le listing devient détaillé et ressemble à un `ls -l` :

```bash
tar tvf stock.tar.gz
```

```text
drwxr-xr-x ansible/ansible   0 2026-07-22 14:20 inventaire/
-rw-r--r-- ansible/ansible  57 2026-07-22 14:20 inventaire/stock.csv
-rw-r--r-- ansible/ansible  50 2026-07-22 14:20 inventaire/fournisseurs.json
-rw-r--r-- ansible/ansible  55 2026-07-22 14:20 inventaire/historique.log
```

Le listing part sur la sortie standard : c'est du texte ordinaire, qu'on peut
rediriger vers un fichier ou filtrer avec `grep`.

Deux comportements de GNU tar qui ne se devinent pas. D'abord, la commande
ci-dessus a lu une archive gzip **sans qu'on écrive `z`** : à la lecture,
`tar` reconnaît seul le compresseur, et `z`, `j` ou `J` y sont facultatifs. À
la création, en revanche, il ne devine rien :

```bash
tar cf archive.tar.gz inventaire && file archive.tar.gz
```

```text
archive.tar.gz: POSIX tar archive (GNU)
```

Voilà un tar **non compressé** portant un nom en `.gz`, excellent moyen de
tromper le monde entier, vous compris. Soit vous nommez le compresseur, soit
vous utilisez `-a` (`--auto-compress`), qui le déduit de l'extension :

```bash
tar caf archive.tar.gz inventaire && file archive.tar.gz
```

```text
archive.tar.gz: gzip compressed data, from Unix, original size modulo 2^32 10240
```

### Le piège des chemins absolus

C'est ce qui distingue une archive utilisable d'une archive piégeuse. `tar`
enregistre les chemins **tels qu'on les lui donne**. Donnez-lui un chemin
absolu, il vous prévient :

```bash
tar czf absolu.tar.gz /srv/inventaire
```

```text
tar: Removing leading `/' from member names
```

L'avertissement n'est pas décoratif : `tar` a retiré le `/` initial et stocké
des chemins **relatifs**.

```bash
tar tf absolu.tar.gz
```

```text
srv/inventaire/
srv/inventaire/fournisseurs.json
srv/inventaire/historique.log
srv/inventaire/stock.csv
```

Conséquence, et c'est là que les restaurations se ratent : l'extraction recrée
cette arborescence **dans le répertoire courant**, pas à l'emplacement
d'origine.

```bash
mkdir -p restauration
tar xzf absolu.tar.gz -C restauration
find restauration | sort
```

```text
restauration
restauration/srv
restauration/srv/inventaire
restauration/srv/inventaire/fournisseurs.json
restauration/srv/inventaire/historique.log
restauration/srv/inventaire/stock.csv
```

Un `srv/` parasite est apparu. Les données sont là, mais pas où on les
attendait, et l'administrateur qui croit avoir restauré `/srv/inventaire` a en
réalité rempli son répertoire de travail.

**La parade tient en une option.** `-C` sert aussi à la **création** : il place
`tar` dans le répertoire indiqué avant de lire les fichiers, ce qui permet de
n'archiver que des noms relatifs.

```bash
tar czf propre.tar.gz -C /srv inventaire
tar tf propre.tar.gz
```

```text
inventaire/
inventaire/fournisseurs.json
inventaire/historique.log
inventaire/stock.csv
```

Plus d'avertissement, et des chemins qui commencent au bon endroit. La
restauration redevient explicite : on choisit la racine avec `-C`.

```bash
sudo tar xzf propre.tar.gz -C /srv
ls -l /srv/inventaire
```

```text
-rw-r--r--. 1 root root 50 Jul 22 14:20 fournisseurs.json
-rw-r--r--. 1 root root 55 Jul 22 14:20 historique.log
-rw-r--r--. 1 root root 57 Jul 22 14:20 stock.csv
```

> **L'option `-P` existe, et c'est précisément celle qu'il ne faut pas
> prendre.** `-P` (`--absolute-names`) demande à `tar` de conserver le `/`. La
> création devient silencieuse, mais le problème se déplace : c'est désormais
> le **listing** qui avertit, parce que `tar` annonce ce qu'il fera au moment
> d'extraire.
>
> ```bash
> tar cPzf absolu-P.tar.gz /srv/inventaire   # aucun message
> tar tf absolu-P.tar.gz
> ```
>
> ```text
> tar: Removing leading `/' from member names
> /srv/inventaire/
> /srv/inventaire/fournisseurs.json
> /srv/inventaire/historique.log
> /srv/inventaire/stock.csv
> ```
>
> D'où la règle de lecture : **un avertissement `Removing leading '/'` à la
> création** signifie que l'archive sera relative ; **le même avertissement au
> listing** signifie que l'archive contient de vrais chemins absolus, et
> qu'extraire une telle archive avec `-P` écrirait directement dans le système
> de fichiers, à l'emplacement choisi par celui qui l'a fabriquée. Ne le faites
> jamais sur une archive dont vous n'êtes pas l'auteur.

### Ce que tar préserve, et ce qu'il perd

Le guide annonce que `tar` conserve « l'arborescence, les permissions et les
dates ». C'est vrai, mais incomplet : ce qui est réellement restauré dépend des
options **et de l'identité de celui qui extrait**. Vérifions plutôt que de
supposer, sur un jeu de fichiers volontairement tordu :

```bash
ls -l src
```

```text
-rwxr-x---. 1 root    root     7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-rw-rw-. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

Un fichier root en `0750`, un fichier en `0600` daté de 2020, un fichier
laxiste en `0666`, un lien symbolique et un lien physique.

**Première leçon, avant même d'extraire : une archive incomplète se crée sans
bruit.** Lancée par l'utilisateur ordinaire `ansible`, qui ne peut pas lire
`deploie.sh` :

```bash
tar cf src.tar src
```

```text
tar: src/deploie.sh: Cannot open: Permission denied
tar: Exiting with failure status due to previous errors
```

`tar` renvoie un code de retour non nul mais **écrit quand même l'archive**,
amputée du fichier illisible. Une sauvegarde lancée sans vérifier son code de
retour peut donc être inutilisable le jour où on en a besoin. D'où la règle :
une sauvegarde d'arborescence système se fait en `root`, et on teste `$?`.

Reprenons avec `sudo tar cf src.tar src`, puis lisons ce que l'archive a
retenu :

```bash
tar tvf src.tar
```

```text
drwxr-xr-x ansible/ansible   0 2026-07-22 14:17 src/
-rw------- ansible/ansible  16 2020-01-15 08:30 src/secret.conf
-rwxr-x--- root/root         7 2026-07-22 14:17 src/deploie.sh
lrwxrwxrwx ansible/ansible   0 2026-07-22 14:17 src/lien-sym -> secret.conf
hrw------- ansible/ansible   0 2020-01-15 08:30 src/lien-dur link to src/secret.conf
-rw-rw-rw- ansible/ansible   8 2026-07-22 14:17 src/partage.txt
```

Tout y est, y compris la nature des liens : `l` pour le lien symbolique avec sa
cible, `h` pour le lien physique avec la mention `link to`. Un lien physique
n'est **pas** stocké deux fois : `tar` enregistre le contenu une seule fois et
note la relation.

Restent les trois façons d'extraire cette même archive.

**Utilisateur ordinaire, sans `-p`** :

```bash
tar xf src.tar -C sans-p && ls -l sans-p/src
```

```text
-rwxr-x---. 1 ansible ansible  7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-r--r--. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

`partage.txt` est passé de `0666` à `0644` : les droits ont été filtrés par
l'`umask` de la session, `0022` ici. Et les propriétaires sont tous devenus
`ansible`.

**Utilisateur ordinaire, avec `-p`** :

```bash
tar xpf src.tar -C avec-p && ls -l avec-p/src
```

```text
-rwxr-x---. 1 ansible ansible  7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-rw-rw-. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

`0666` est bien revenu : `-p` (`--preserve-permissions`) court-circuite
l'`umask`. En revanche **les propriétaires ne sont toujours pas restaurés** :
`deploie.sh` reste `ansible:ansible` alors que l'archive dit `root/root`. Ce
n'est pas une faiblesse de `tar`, c'est le noyau : un utilisateur ordinaire ne
peut pas donner un fichier à quelqu'un d'autre.

**En root** :

```bash
sudo tar xf src.tar -C as-root && ls -l as-root/src
```

```text
-rwxr-x---. 1 root    root     7 Jul 22 14:17 deploie.sh
-rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 14:17 lien-sym -> secret.conf
-rw-rw-rw-. 1 ansible ansible  8 Jul 22 14:17 partage.txt
-rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

Sans avoir écrit `-p`, `root` obtient les droits exacts **et** les
propriétaires d'origine : pour lui, `-p` est le comportement par défaut, et la
restauration des propriétaires aussi.

Dans les trois cas, les horodatages de 2020 sont revenus et le lien symbolique
est resté un lien. Le lien physique aussi, ce qu'un `ls -li` confirme après
extraction, les deux noms partageant le même numéro d'inode :

```text
25672526 -rw-------. 2 ansible ansible 16 Jan 15  2020 lien-dur
25672526 -rw-------. 2 ansible ansible 16 Jan 15  2020 secret.conf
```

| Ce qui est restauré | utilisateur, sans `-p` | utilisateur, avec `-p` | root |
|---|---|---|---|
| Arborescence et contenu | oui | oui | oui |
| Date de modification | oui | oui | oui |
| Liens symboliques et physiques | oui | oui | oui |
| Droits exacts | non, filtrés par l'`umask` | oui | oui, par défaut |
| Propriétaire et groupe | non | non | oui, par défaut |

**Ce que le guide ne dit pas : le contexte SELinux est perdu par défaut.** Sur
cette AlmaLinux en `Enforcing`, un fichier étiqueté `etc_t` ressort du tar
étiqueté selon le répertoire de destination :

```bash
ls -Z src/secret.conf                     # unconfined_u:object_r:etc_t:s0
tar cf ctx.tar src
tar xf ctx.tar -C ctx-defaut
ls -Z ctx-defaut/src/secret.conf
```

```text
unconfined_u:object_r:user_home_t:s0 ctx-defaut/src/secret.conf
```

Pour une sauvegarde système sur une distribution avec SELinux, il faut le
demander explicitement, **des deux côtés** :

```bash
sudo tar --selinux --xattrs -cf ctx2.tar src
sudo tar --selinux --xattrs -xf ctx2.tar -C ctx-selinux
ls -Z ctx-selinux/src/secret.conf
```

```text
unconfined_u:object_r:etc_t:s0 ctx-selinux/src/secret.conf
```

### Choisir un compresseur : mesurer plutôt que recopier un tableau

`z` appelle `gzip`, `j` appelle `bzip2`, `J` (majuscule) appelle `xz`, et
`--zstd` appelle `zstd`. Premier réflexe : vérifier lesquels **existent** sur
la machine, parce que `tar` ne fait que les invoquer.

```bash
for c in gzip bzip2 xz zstd; do printf "%-6s " $c; command -v $c || echo ABSENT; done
```

```text
gzip   /usr/bin/gzip
bzip2  ABSENT
xz     /usr/bin/xz
zstd   ABSENT
```

Sur une AlmaLinux 10 installée en minimal, **`bzip2` et `zstd` ne sont pas
là**, et `zip`/`unzip` non plus. Ce qui donne, si on demande `j` quand même :

```bash
tar cjf essai.tar.bz2 inventaire ; echo "rc=$?"
```

```text
/bin/sh: line 1: bzip2: command not found
tar: essai.tar.bz2: Cannot write: Broken pipe
tar: Child returned status 127
tar: Error is not recoverable: exiting now
rc=2
```

Message obscur, et un fichier `essai.tar.bz2` de **0 octet** laissé sur le
disque. Le correctif est un `sudo dnf install bzip2` (ou `sudo apt install
bzip2` sur Debian et Ubuntu).

Une fois les quatre outils présents, la comparaison se fait en une boucle.
Voici les mesures obtenues sur un journal web de 600 000 lignes (archive `tar`
non compressée : 50 636 800 octets), options par défaut de chaque compresseur,
sur une VM à 1 vCPU :

| Option | Fichier | Taille | Part du tar | Temps |
|---|---|---|---|---|
| `-z` (gzip) | `.tar.gz` | 8 215 406 | 16,2 % | 0,92 s |
| `-j` (bzip2) | `.tar.bz2` | 4 713 638 | 9,3 % | 3,82 s |
| `-J` (xz) | `.tar.xz` | 5 979 348 | 11,8 % | 22,92 s |
| `--zstd` | `.tar.zst` | 8 878 856 | 17,5 % | 0,15 s |

Et sur un tout autre jeu de données, une copie de `/usr/share/doc` (archive
`tar` : 24 033 280 octets), donc des milliers de petits fichiers de
documentation :

| Option | Taille | Part du tar | Temps |
|---|---|---|---|
| `-z` (gzip) | 8 299 696 | 34,5 % | 0,72 s |
| `-j` (bzip2) | 7 063 641 | 29,4 % | 1,24 s |
| `-J` (xz) | 6 273 336 | 26,1 % | 8,76 s |
| `--zstd` | 8 044 571 | 33,5 % | 0,10 s |

Trois enseignements que ces chiffres établissent, et qu'aucun tableau appris
par coeur ne donne :

1. **Le classement dépend des données.** Sur le journal, `bzip2` bat `xz` de
   deux points et demi ; sur la documentation, `xz` reprend la tête. La
   hiérarchie « gzip, puis bzip2, puis xz » que l'on lit partout est une
   tendance, pas une loi.
2. **L'écart de temps est sans commune mesure avec l'écart de taille.** Sur le
   journal, `xz` met vingt-cinq fois plus longtemps que `gzip` pour gagner
   quatre points de taille. Sur une sauvegarde nocturne le calcul se défend,
   sur un transfert interactif beaucoup moins.
3. **`zstd` change les termes du problème.** Il compresse ici six fois plus
   vite que `gzip` pour une taille comparable, ce qui explique son adoption
   rapide. Les paquets de cette AlmaLinux l'utilisent déjà :
   `rpm -q --qf '%{PAYLOADCOMPRESSOR}\n' bash tar gzip` répond `zstd` trois
   fois.

La décompression suit la même logique, mesurée sur le journal : 0,17 s pour
gzip, 0,97 s pour bzip2, 0,24 s pour xz, 0,06 s pour zstd. Notez que `xz`, très
lent à compresser, décompresse presque aussi vite que `gzip`. Pour une archive
écrite une fois et lue souvent, c'est un argument.

Chaque compresseur amène ses utilitaires de lecture, qui évitent de
décompresser avant de chercher :

```bash
zgrep -c " 500 " frontal.log.gz
```

```text
100030
```

`zcat`, `zgrep` et `zless` viennent avec `gzip` ; `bzcat` avec `bzip2`,
`xzcat` avec `xz`, `zstdcat` avec `zstd` (un `rpm -qf` sur chacun le confirme).
Sur un journal compressé de 50 Mio, c'est la différence entre une commande
immédiate et un détour par le disque.

### Sortir un seul fichier d'une archive

Une restauration réelle consiste presque toujours à récupérer un fichier, pas
toute l'arborescence. Nommer un membre après le nom de l'archive limite
l'opération à celui-ci :

```bash
tar xzf propre.tar.gz -C cible inventaire/stock.csv
find cible | sort
```

```text
cible
cible/inventaire
cible/inventaire/stock.csv
```

Trois points à noter. Le membre se désigne **exactement comme `tar tf`
l'affiche**, ici `inventaire/stock.csv` et non `stock.csv`. L'arborescence
stockée est recréée sous la cible, d'où le `cible/inventaire/` intermédiaire.
Et le répertoire donné à `-C` doit exister au préalable, sinon :

```text
tar: /tmp/pas-la: Cannot open: No such file or directory
tar: Error is not recoverable: exiting now
```

Se tromper de nom de membre ne passe pas inaperçu, ce qui est une bonne
nouvelle :

```bash
tar xzf propre.tar.gz -C cible inventaire/absent.txt ; echo "rc=$?"
```

```text
tar: inventaire/absent.txt: Not found in archive
tar: Exiting with failure status due to previous errors
rc=2
```

Trois options complètent la panoplie :

```bash
tar xzf propre.tar.gz -C cible2 --wildcards "inventaire/*.json"
tar xzf propre.tar.gz -C cible3 --strip-components=1
tar cf sans-log.tar -C /srv --exclude="*.log" inventaire
```

`--wildcards` sort les seuls fichiers correspondants : le motif doit être entre
guillemets pour que ce soit `tar`, et non le shell, qui l'interprète.
`--strip-components=1` retire le premier niveau de chemin, ce qui donne les
trois fichiers directement dans `cible3/`, sans le `inventaire/` intermédiaire.
`--exclude` s'utilise à la création comme à l'extraction ; ici, à la création :

```text
inventaire/
inventaire/stock.csv
inventaire/fournisseurs.json
```

> **Une extraction écrase sans demander.** Un membre qui porte le nom d'un
> fichier existant le remplace, en silence. L'option `-k`
> (`--keep-old-files`) inverse ce comportement : `tar` refuse alors le membre
> et sort en erreur, mais le fichier local reste intact.
>
> ```text
> tar: marqueur.txt: Cannot open: File exists
> tar: Exiting with failure status due to previous errors
> ```
>
> C'est la raison pour laquelle on liste avant d'extraire, et pour laquelle on
> extrait dans un répertoire vide quand on a un doute.

### Vérifier une archive

`tar df` (`--diff`, ou `--compare`) relit l'archive et la confronte au disque.
Silence et code 0 signifient que tout concorde :

```bash
tar df propre.tar.gz -C /srv ; echo "rc=$?"
```

```text
rc=0
```

Modifions un fichier d'origine et recommençons :

```bash
sudo sh -c 'echo modif >> /srv/inventaire/stock.csv'
tar df propre.tar.gz -C /srv ; echo "rc=$?"
```

```text
inventaire/stock.csv: Mod time differs
inventaire/stock.csv: Size differs
rc=1
```

C'est le contrôle qui manque à la plupart des scripts de sauvegarde : il prouve
que l'archive est relisible et fidèle, sans rien écrire sur le disque.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `tar: Removing leading '/' from member names` à la création | un chemin absolu a été donné ; l'archive sera relative, prévoir `-C` à l'extraction, ou archiver avec `-C` |
| Le même message au **listing** | l'archive contient de vrais chemins absolus (créée avec `-P`) : extraire avec prudence, jamais avec `-P` |
| L'extraction crée un `srv/`, `home/` ou `etc/` parasite | l'archive avait été créée depuis un chemin absolu ; se placer à la bonne racine avec `-C` |
| `Cannot open: Permission denied` puis `Exiting with failure status` | archive créée sans les droits de lecture ; elle existe mais est **incomplète**, refaire en root |
| `bzip2: command not found` puis `Child returned status 127` | le compresseur n'est pas installé ; `sudo dnf install bzip2` (ou `zstd`, `xz`) |
| `gzip: stdin: not in gzip format` | mauvais compresseur demandé (`z` sur une archive bzip2) ; l'omettre, GNU tar détecte seul |
| Une archive nommée `.tar.gz` que `file` dit non compressée | `tar cf` ne devine pas d'après l'extension : écrire `tar czf` ou `tar caf` |
| Du binaire déversé dans le terminal | `-f` oublié : `tar` a écrit sur la sortie standard |
| `Not found in archive` | le membre n'est pas nommé comme `tar tf` l'affiche (chemin complet attendu) |
| `Cannot open: No such file or directory` sur la cible de `-C` | le répertoire n'existe pas, `tar` ne le crée pas |
| Un fichier local remplacé après extraction | comportement normal ; `-k` pour l'interdire |
| Les droits ne sont pas ceux de l'archive | extraction en utilisateur ordinaire sans `-p` : l'`umask` a filtré |
| Le propriétaire n'est pas restauré malgré `-p` | seul `root` peut restaurer les propriétaires |
| Le contexte SELinux a changé après restauration | `--selinux --xattrs` sont nécessaires à la création **et** à l'extraction |
| `gzip: fichier already has .gz suffix -- unchanged` | le fichier est déjà compressé |
| Le fichier d'origine a disparu après `gzip` | `gzip` remplace ; `gzip -k` pour le conserver |

Pour tout défaire et repartir de zéro :

```bash
rm -rf ~/cours
sudo rm -rf /srv/inventaire
```
