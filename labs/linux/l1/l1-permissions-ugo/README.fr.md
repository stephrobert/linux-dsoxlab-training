# Lab — permissions de fichiers avec chmod

## Rappel

[**Modifier les droits sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/)

Chaque fichier porte trois triplets de permissions (propriétaire, groupe,
autres) avec lecture (4), écriture (2), exécution (1). `chmod` les pose en
octal (`chmod 664 fichier`) ou en symbolique (`chmod u+x,o-r fichier`). Un
répertoire a besoin du bit `x` pour être traversé. Moindre privilège : accorder
exactement ce dont le fichier a besoin, pas plus.

## Le cours

Les exemples ci-dessous travaillent sur `/srv/atelier-droits`, avec les
utilisateurs `theo` et `nadia` et le groupe `redaction` : le challenge, lui,
vous demandera d'autres fichiers et d'autres valeurs. Le but est d'apprendre la
méthode, pas de recopier une ligne. Toutes les sorties reproduites ici viennent
d'une AlmaLinux 10 avec SELinux en `Enforcing`.

Une précision avant de commencer. Le challenge porte sur des fichiers dont vous
êtes déjà propriétaire : `chmod` suffit, `sudo` est inutile. Le cours, lui, a
besoin d'un second compte pour **prouver** les droits au lieu de les lire, donc
d'une machine où vous êtes administrateur.

### Le décor de démonstration

```bash
sudo useradd -m theo
sudo useradd -m nadia
sudo groupadd redaction
sudo usermod -aG redaction theo
sudo mkdir -p /srv/atelier-droits
sudo chown theo:redaction /srv/atelier-droits
sudo chmod 0775 /srv/atelier-droits
sudo -u theo sh -c 'umask 002
  echo "brouillon de l article" > /srv/atelier-droits/rapport.txt
  printf "#!/usr/bin/env bash\necho inventaire\n" > /srv/atelier-droits/inventaire.sh
  mkdir /srv/atelier-droits/archives'
```

`theo` est membre de `redaction`, `nadia` ne l'est pas encore : c'est ce qui va
permettre de tester les trois niveaux de droits sur les mêmes fichiers.

Convention pour tout ce qui suit : une commande **sans préfixe** est lancée par
`theo`, propriétaire des fichiers (en pratique `sudo -u theo …`) ; `sudo -u
nadia …` teste l'accès d'un tiers ; `sudo …` seul agit en root.

```bash
id theo
id nadia
```

```text
uid=1002(theo) gid=1002(theo) groups=1002(theo),1004(redaction)
uid=1003(nadia) gid=1003(nadia) groups=1003(nadia)
```

### Lire les droits avant de les changer

```bash
ls -l /srv/atelier-droits
```

```text
total 8
drwxrwxr-x. 2 theo theo  6 Jul 22 14:02 archives
-rw-rw-r--. 1 theo theo 36 Jul 22 14:02 inventaire.sh
-rw-rw-r--. 1 theo theo 23 Jul 22 14:02 rapport.txt
```

Le premier caractère donne le type (`-` fichier, `d` répertoire), les neuf
suivants les trois triplets `u`, `g`, `o`. Remarquez le **point final** après
les neuf caractères : il apparaît sur cette machine et n'existe pas dans les
exemples du guide. Ce n'est pas un dixième droit, et `stat` ne le voit pas.

`ls -l` est fait pour l'humain ; pour vérifier une valeur exacte, demandez
l'octal directement :

```bash
stat -c '%A %a %U %G %n' /srv/atelier-droits /srv/atelier-droits/rapport.txt /srv/atelier-droits/archives
```

```text
drwxrwxr-x 775 theo redaction /srv/atelier-droits
-rw-rw-r-- 664 theo theo /srv/atelier-droits/rapport.txt
drwxrwxr-x 775 theo theo /srv/atelier-droits/archives
```

C'est la commande à réflexe : `%A` donne la forme `rwx`, `%a` l'octal, et les
deux se lisent d'un coup. Attention, `%a` supprime les zéros de tête : un
fichier sans aucun droit s'affiche `0`, pas `000`.

### La notation symbolique : qui, quelle action, quoi

Le guide résume les trois parties d'une expression symbolique.

| Qui | Signification |
|-----|---------------|
| `u` | User (propriétaire) |
| `g` | Group (groupe) |
| `o` | Others (autres) |
| `a` | All (tout le monde) |

| Action | Signification |
|--------|---------------|
| `+` | Ajouter une permission |
| `-` | Retirer une permission |
| `=` | Définir exactement ces permissions |

Sur le décor ci-dessus, chaque commande et son résultat réel :

```bash
chmod u+x /srv/atelier-droits/inventaire.sh
stat -c '%A %a %n' /srv/atelier-droits/inventaire.sh
```

```text
-rwxrw-r-- 764 /srv/atelier-droits/inventaire.sh
```

```bash
chmod go-w /srv/atelier-droits/inventaire.sh
stat -c '%A %a %n' /srv/atelier-droits/inventaire.sh
```

```text
-rwxr--r-- 744 /srv/atelier-droits/inventaire.sh
```

```bash
chmod a=r /srv/atelier-droits/rapport.txt
stat -c '%A %a %n' /srv/atelier-droits/rapport.txt
```

```text
-r--r--r-- 444 /srv/atelier-droits/rapport.txt
```

### `+` ajuste, `=` remet à plat

La différence entre `+` et `=` est le premier piège de la notation symbolique.
Partons d'un fichier ouvert à tous en lecture et écriture :

```bash
chmod 0666 /srv/atelier-droits/rapport.txt
chmod o+r  /srv/atelier-droits/rapport.txt
stat -c '%a %n' /srv/atelier-droits/rapport.txt
```

```text
666 /srv/atelier-droits/rapport.txt
```

Rien n'a bougé : `o+r` **ajoute** la lecture, qui était déjà là, et ne dit rien
de l'écriture. Avec `=`, le triplet est réécrit en entier :

```bash
chmod o=r /srv/atelier-droits/rapport.txt
stat -c '%a %n' /srv/atelier-droits/rapport.txt
```

```text
664 /srv/atelier-droits/rapport.txt
```

Retenez la règle du guide : `+` ou `-` quand vous ajustez **une** permission,
`=` ou l'octal quand vous voulez un état exact. Un énoncé qui dit « ce fichier
doit être en … » demande un état exact, donc `=` ou l'octal, jamais `+`.

### La notation octale : trois chiffres

Chaque permission a une valeur, et on additionne par triplet.

| Permission | Valeur |
|------------|--------|
| `r` (read) | **4** |
| `w` (write) | **2** |
| `x` (execute) | **1** |

| Permissions | Calcul | Octal |
|-------------|--------|-------|
| `rwx` | 4+2+1 | **7** |
| `rw-` | 4+2+0 | **6** |
| `r-x` | 4+0+1 | **5** |
| `r--` | 4+0+0 | **4** |
| `---` | 0+0+0 | **0** |

Les trois chiffres se lisent dans l'ordre propriétaire, groupe, autres.
Donnons au brouillon un mode d'équipe : le propriétaire et le groupe lisent et
écrivent, les autres n'ont rien.

```bash
chgrp redaction /srv/atelier-droits/rapport.txt
chmod 0660 /srv/atelier-droits/rapport.txt
stat -c '%A %a %U %G %n' /srv/atelier-droits/rapport.txt
```

```text
-rw-rw---- 660 theo redaction /srv/atelier-droits/rapport.txt
```

### Prouver un droit plutôt que le lire

Lire `ls -l` ne prouve rien : c'est l'accès réel qui compte. `sudo -u <compte>
<commande>` lance la commande sous une autre identité et donne la réponse du
noyau.

```bash
sudo -u theo cat /srv/atelier-droits/rapport.txt
```

```text
brouillon de l article
```

```bash
sudo -u nadia cat /srv/atelier-droits/rapport.txt
```

```text
cat: /srv/atelier-droits/rapport.txt: Permission denied
```

```bash
sudo -u nadia sh -c 'echo ligne-de-nadia >> /srv/atelier-droits/rapport.txt'
```

```text
sh: line 1: /srv/atelier-droits/rapport.txt: Permission denied
```

`nadia` tombe dans le triplet « autres », qui est à `---`. Faisons-la entrer
dans le groupe :

```bash
sudo usermod -aG redaction nadia
id nadia
```

```text
uid=1003(nadia) gid=1003(nadia) groups=1003(nadia),1004(redaction)
```

```bash
sudo -u nadia cat /srv/atelier-droits/rapport.txt
```

```text
brouillon de l article
ligne-de-theo
```

Le fichier n'a pas changé d'un bit : c'est l'appartenance de `nadia` qui a
changé de triplet. `sudo -u` démarre un processus neuf, dont la liste de
groupes est relue à cet instant ; une session déjà ouverte, elle, garde les
groupes qu'elle avait au démarrage, d'où le réflexe de se reconnecter après un
`usermod -aG`.

### Un seul niveau s'applique, et il n'est pas forcément le plus généreux

Le noyau s'arrête au **premier** niveau qui correspond : propriétaire, sinon
groupe, sinon autres. Il ne cumule pas. Un mode volontairement absurde le
montre :

```bash
chmod 0466 /srv/atelier-droits/rapport.txt
stat -c '%A %a %U %G %n' /srv/atelier-droits/rapport.txt
```

```text
-r--rw-rw- 466 theo redaction /srv/atelier-droits/rapport.txt
```

```bash
sudo -u theo sh -c 'echo essai-de-theo >> /srv/atelier-droits/rapport.txt'
```

```text
sh: line 1: /srv/atelier-droits/rapport.txt: Permission denied
```

```bash
sudo -u nadia sh -c 'echo ligne-de-nadia >> /srv/atelier-droits/rapport.txt'
```

Aucun message : l'écriture est passée. `theo`, **propriétaire** du fichier et
membre du groupe, ne peut pas écrire, alors que `nadia`, simple membre du
groupe, le peut. Le triplet `u` a gagné, et il valait `r--`. Conséquence
pratique : un mode plus restrictif pour `u` que pour `g` ou `o` n'est jamais
utile, il ne bloque que le propriétaire.

### Sur un répertoire, `r` et `x` ne servent pas à la même chose

C'est le point que tout le monde comprend de travers. Sur un répertoire, `r`
autorise à **lister les noms**, `x` à **traverser** et atteindre le contenu.
Les deux sont indépendants, donc quatre situations existent. Le décor : un
répertoire appartenant à `theo`, contenant un fichier connu, et `nadia` qui
n'est ni propriétaire ni membre du groupe (elle tombe donc sur le triplet
« autres »).

```bash
cd /srv/atelier-droits
umask 002
mkdir -p dossier-test
echo "contenu du fichier" > dossier-test/dedans.txt
```

Les quatre essais, avec la réponse réelle de la machine :

```bash
chmod o=rx /srv/atelier-droits/dossier-test     # drwxrwxr-x 775
sudo -u nadia ls  /srv/atelier-droits/dossier-test
sudo -u nadia cat /srv/atelier-droits/dossier-test/dedans.txt
sudo -u nadia sh -c 'cd /srv/atelier-droits/dossier-test && pwd'
```

```text
dedans.txt
contenu du fichier
/srv/atelier-droits/dossier-test
```

```bash
chmod o=r /srv/atelier-droits/dossier-test      # drwxrwxr-- 774
```

```text
dedans.txt
cat: /srv/atelier-droits/dossier-test/dedans.txt: Permission denied
sh: line 1: cd: /srv/atelier-droits/dossier-test: Permission denied
```

```bash
chmod o=x /srv/atelier-droits/dossier-test      # drwxrwx--x 771
```

```text
ls: cannot open directory '/srv/atelier-droits/dossier-test': Permission denied
contenu du fichier
/srv/atelier-droits/dossier-test
```

```bash
chmod o= /srv/atelier-droits/dossier-test       # drwxrwx--- 770
```

```text
ls: cannot open directory '/srv/atelier-droits/dossier-test': Permission denied
cat: /srv/atelier-droits/dossier-test/dedans.txt: Permission denied
sh: line 1: cd: /srv/atelier-droits/dossier-test: Permission denied
```

Le tableau de synthèse :

| Droits sur le répertoire | `ls` | `cat` d'un fichier connu | `cd` |
|---|---|---|---|
| `r-x` | oui | oui | oui |
| `r--` | oui, les noms seulement | non | non |
| `--x` | non | oui | oui |
| `---` | non | non | non |

Le cas `r--` mérite un coup d'œil de plus, car `ls -l` y devient bavard sans
rien savoir :

```bash
sudo -u nadia ls -l /srv/atelier-droits/dossier-test
```

```text
ls: cannot access '/srv/atelier-droits/dossier-test/dedans.txt': Permission denied
total 0
-????????? ? ? ? ?            ? dedans.txt
```

Le nom vient du répertoire (droit `r`), tout le reste vient du fichier, que
`ls` ne peut pas atteindre faute de `x` sur le répertoire. À l'inverse, le cas
`--x` est celui d'un répertoire « aveugle » : impossible de savoir ce qu'il
contient, mais tout fichier dont on connaît le nom s'ouvre normalement.

Deux conséquences à garder en tête :

- un répertoire sans `x` est inutilisable, même avec `r` : c'est presque
  toujours une erreur ;
- il faut le `x` sur **chaque** répertoire du chemin, pas seulement sur le
  dernier. Un fichier parfaitement ouvert reste inaccessible si un répertoire
  parent est fermé.

### Supprimer un fichier, c'est modifier le répertoire

Point contre-intuitif : supprimer n'écrit pas dans le fichier, cela retire son
nom du répertoire. Les droits vérifiés sont donc ceux du **répertoire** (`w` et
`x`), pas ceux du fichier.

```bash
mkdir /srv/atelier-droits/bac-a-sable
echo a > /srv/atelier-droits/bac-a-sable/blinde.txt
chmod 0777 /srv/atelier-droits/bac-a-sable          # drwxrwxrwx
chmod 0000 /srv/atelier-droits/bac-a-sable/blinde.txt   # ----------
sudo -u nadia rm /srv/atelier-droits/bac-a-sable/blinde.txt
```

Aucun message : un fichier sans le moindre droit a été supprimé par quelqu'un
qui ne pouvait ni le lire ni l'écrire. Le cas inverse :

```bash
mkdir /srv/atelier-droits/verrou
echo b > /srv/atelier-droits/verrou/ouvert.txt
chmod 0555 /srv/atelier-droits/verrou               # dr-xr-xr-x, pas de w
chmod 0777 /srv/atelier-droits/verrou/ouvert.txt    # -rwxrwxrwx
sudo -u nadia rm /srv/atelier-droits/verrou/ouvert.txt
```

```text
rm: cannot remove '/srv/atelier-droits/verrou/ouvert.txt': Permission denied
```

```bash
sudo -u nadia sh -c 'echo intrusion >> /srv/atelier-droits/verrou/ouvert.txt'
```

Aucun message : elle ne peut pas le supprimer, mais elle peut écrire dedans.
Les droits du fichier protègent son **contenu**, ceux du répertoire protègent
son **existence**. Verrouiller un fichier sensible suppose donc de regarder
aussi le répertoire qui le contient.

### `chown` et `chgrp` : propriétaire et groupe

Poser les bons bits ne sert à rien si le fichier appartient au mauvais compte.
Le décor : un fichier `planning.txt` créé par `theo`, donc `theo:theo`.

```bash
sudo -u theo chown nadia /srv/atelier-droits/planning.txt
```

```text
chown: changing ownership of '/srv/atelier-droits/planning.txt': Operation not permitted
```

Donner un fichier est réservé à root, comme le dit le guide : sinon n'importe
qui pourrait se débarrasser d'un fichier gênant en l'attribuant à un autre. Le
groupe, en revanche, obéit à une règle plus fine, que le guide ne détaille pas :
le **propriétaire** peut le changer, à condition d'être membre du groupe visé.

```bash
sudo -u theo chgrp redaction /srv/atelier-droits/planning.txt   # theo est membre : accepté
sudo -u theo chgrp nadia     /srv/atelier-droits/planning.txt   # il ne l'est pas
```

```text
chgrp: changing group of '/srv/atelier-droits/planning.txt': Operation not permitted
```

Avec les droits root, les deux formes du guide fonctionnent, `chown` sachant
faire les deux d'un coup :

```bash
sudo chown nadia:nadia /srv/atelier-droits/planning.txt   # propriétaire et groupe
sudo chown :redaction  /srv/atelier-droits/planning.txt   # le groupe seul
stat -c '%U %G %n' /srv/atelier-droits/planning.txt
```

```text
nadia redaction /srv/atelier-droits/planning.txt
```

Dernier rappel utile : `chmod` aussi exige d'être propriétaire (ou root). Une
fois le fichier passé à `nadia`, `theo` ne peut plus rien y changer.

```bash
sudo -u theo chmod 0664 /srv/atelier-droits/planning.txt
```

```text
chmod: changing permissions of '/srv/atelier-droits/planning.txt': Operation not permitted
```

### Le récursif, et pourquoi `-R` avec un octal est presque toujours faux

Le décor : une petite arborescence de répertoires en `775` et de fichiers en
`664`, sur laquelle on applique un `chmod -R` de bonne foi.

```bash
cd /srv/atelier-droits
umask 002
mkdir -p projet/config
touch projet/lisezmoi.md projet/config/app.conf
chmod -R 775 /srv/atelier-droits/projet
find /srv/atelier-droits/projet -printf '%m %M %p\n' | sort -k3
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
775 -rwxrwxr-x /srv/atelier-droits/projet/config/app.conf
775 -rwxrwxr-x /srv/atelier-droits/projet/lisezmoi.md
```

Un fichier de configuration devenu exécutable : le même chiffre n'a pas le même
sens sur un fichier et sur un répertoire, et `-R` ne fait pas la différence. La
parade du guide consiste à traiter les deux types séparément :

```bash
find /srv/atelier-droits/projet -type d -exec chmod 775 {} +
find /srv/atelier-droits/projet -type f -exec chmod 664 {} +
find /srv/atelier-droits/projet -printf '%m %M %p\n' | sort -k3
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
664 -rw-rw-r-- /srv/atelier-droits/projet/config/app.conf
664 -rw-rw-r-- /srv/atelier-droits/projet/lisezmoi.md
```

`chmod` offre une seconde parade, plus courte, en symbolique : le `X`
**majuscule** n'accorde `x` qu'aux répertoires et aux fichiers qui l'ont déjà.
Partons d'une arborescence fermée aux autres (`770` et `660`) et ouvrons-la en
lecture :

```bash
chmod -R o+rx /srv/atelier-droits/projet    # x minuscule
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
665 -rw-rw-r-x /srv/atelier-droits/projet/config/app.conf
665 -rw-rw-r-x /srv/atelier-droits/projet/lisezmoi.md
```

```bash
chmod -R o+rX /srv/atelier-droits/projet    # X majuscule
```

```text
775 drwxrwxr-x /srv/atelier-droits/projet
775 drwxrwxr-x /srv/atelier-droits/projet/config
664 -rw-rw-r-- /srv/atelier-droits/projet/config/app.conf
664 -rw-rw-r-- /srv/atelier-droits/projet/lisezmoi.md
```

Les répertoires sont traversables, les fichiers sont restés non exécutables :
c'est le résultat voulu, en une commande.

Un détail qui trompe pendant les vérifications : `find` obéit lui aussi aux
permissions. Lancé par un compte qui n'a pas le `x` sur l'arborescence, il
n'affiche que la racine et une erreur, ce qui ressemble à un répertoire vide.

```text
find: '/srv/atelier-droits/projet': Permission denied
770 drwxrwx--- /srv/atelier-droits/projet
```

### `umask` : les droits des fichiers que vous n'avez pas encore créés

Un fichier neuf ne naît jamais en `rwxrwxrwx`. Un masque, le `umask`, retire
des bits à la création.

```bash
umask
```

```text
0022
```

```bash
cd /srv/atelier-droits
umask 007
touch u007.txt && mkdir u007.d
stat -c '%a %A %n' u007.txt u007.d
```

```text
660 -rw-rw---- u007.txt
770 drwxrwx--- u007.d
```

Le point de départ est `666` pour un fichier et `777` pour un répertoire : les
fichiers ne reçoivent **jamais** le bit `x` à la création, c'est pour cela
qu'un script fraîchement écrit doit être rendu exécutable à la main.

Le `umask` est un **masque**, pas une soustraction, même si l'écart ne se voit
pas avec les valeurs courantes :

```bash
umask 013
touch u013.txt && stat -c '%a %A %n' u013.txt
```

```text
664 -rw-rw-r-- u013.txt
```

Une soustraction donnerait `666 - 013 = 653` ; le résultat réel est `664`. Le
noyau retire des **bits** : le `1` du masque vise `x`, que le fichier n'avait
déjà pas.

Enfin, `umask` ne vaut que pour le shell courant et n'affecte pas les fichiers
existants. Après la commande précédente, une nouvelle session repart à `0022`.
Pour le rendre permanent, il faut le poser dans un fichier de profil.

### Le piège des trois chiffres sur un répertoire

Un répertoire peut porter des bits supplémentaires (set-GID, sticky bit), qui
occupent un **quatrième** chiffre. Et là, `chmod` ne se comporte pas comme on
l'attend :

```bash
mkdir /srv/atelier-droits/partage
chmod 2775 /srv/atelier-droits/partage     # on pose le set-GID
chmod 775  /srv/atelier-droits/partage     # on croit revenir à un mode simple
stat -c '%a %A %n' /srv/atelier-droits/partage
```

```text
2775 drwxrwsr-x /srv/atelier-droits/partage
```

Le `s` est toujours là, et un `0` de tête (`chmod 0775`) n'y change rien non
plus. `man chmod` documente le fait : « For directories chmod preserves
set-user-ID and set-group-ID bits unless you explicitly specify otherwise ».
Trois écritures effacent réellement ces bits, toutes vérifiées :

```bash
chmod g-s   /srv/atelier-droits/partage    # symbolique
chmod 00775 /srv/atelier-droits/partage    # deux zéros de tête
chmod =775  /srv/atelier-droits/partage    # signe égal
```

```text
775 drwxrwxr-x /srv/atelier-droits/partage
```

Sur un **fichier**, la règle est différente : trois chiffres suffisent à effacer
le set-UID.

```bash
cd /srv/atelier-droits
touch bin-demo
chmod 4755 bin-demo && stat -c '%a %A' bin-demo
chmod 755  bin-demo && stat -c '%a %A' bin-demo
```

```text
4755 -rwsr-xr-x
755 -rwxr-xr-x
```

C'est exactement le genre d'écart qui fait échouer une vérification
automatique : la commande n'a rien signalé, et le mode obtenu n'est pas celui
demandé. Vérifiez toujours avec `stat -c '%a'` après coup.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `chmod: … Operation not permitted` | vous n'êtes ni propriétaire ni root |
| `chown: … Operation not permitted` | seul root peut donner un fichier |
| `chgrp: … Operation not permitted` | vous n'êtes pas membre du groupe visé |
| `Permission denied` en lisant un fichier pourtant ouvert | il manque le `x` sur un répertoire du chemin |
| `ls` marche mais `cat` échoue | `r` sans `x` sur le répertoire |
| `cat` marche mais `ls` échoue | `x` sans `r` sur le répertoire |
| `ls -l` affiche des `?` partout | `r` sans `x` : les noms sont lisibles, les métadonnées non |
| Le propriétaire est bloqué alors que le groupe passe | un seul niveau s'applique, et `u` est plus restrictif que `g` |
| Impossible de supprimer un fichier en `777` | c'est le répertoire qui décide (`w` et `x`) |
| Tous les fichiers sont devenus exécutables | `chmod -R` avec un octal ; utiliser `find -type f/-type d` ou `X` majuscule |
| Le mode obtenu commence par un chiffre en trop | set-UID ou set-GID conservé ; utiliser `g-s`, `00…` ou `=…` |
| Un fichier neuf n'a pas les droits attendus | le `umask` du shell, à vérifier avec `umask` |

### Défaire le décor

```bash
sudo rm -rf /srv/atelier-droits
sudo userdel -r theo
sudo userdel -r nadia
sudo groupdel redaction
```
