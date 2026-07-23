# Lab — cartographier Linux : noyau, distribution, logiciel libre

## Rappel

[**Notions fondamentales Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/)

Au sens strict, Linux est un **noyau** : le programme central écrit par Linus
Torvalds en 1991, distribué sous licence GPL, qui gère le matériel, la mémoire,
les processus et les fichiers. Dans l'usage courant, « Linux » désigne le
système complet, et ce système est en réalité fourni par une **distribution**
qui assemble autour du noyau des bibliothèques, des utilitaires, un système
d'initialisation et un gestionnaire de paquets. Le guide pose ce vocabulaire,
l'architecture en couches et les sept étapes du démarrage. Ce lab en fait la
démonstration sur une machine réelle : le noyau s'y voit comme un fichier, et
les deux numéros de version que tout le monde confond s'affichent côte à côte.

C'est le premier lab du parcours, il ouvre la voie et ne traite pas tout.
Ouvrir un terminal et lire son invite est l'objet de `l1-first-terminal`, la
structure d'une commande celui de `l1-read-a-command`, la documentation celui
de `l1-get-help`, l'arborescence celui de `l1-linux-filesystem` : rien de tout
cela n'est repris ici.

## Le cours

Les commandes ci-dessous ne répondent à aucune question du challenge : elles
décrivent la machine sur laquelle ce cours a été écrit, pas la vôtre, et
**toutes les valeurs affichées seront différentes chez vous**. Ce qui compte
n'est pas le numéro, c'est de savoir quelle commande le produit et ce qu'il
signifie. Toutes sont en **lecture seule** : aucune n'écrit, aucune ne réclame
`sudo`, aucune n'installe rien. Vous pouvez les lancer sans le moindre risque.

Les sorties reproduites ici ont été relevées sur un poste de travail en
**Ubuntu 24.04.2 LTS**, noyau `6.8.0-134-generic`, en locale française, d'où
les dates de la forme `juin 26 18:36`.

### Le noyau est un fichier, et vous pouvez le regarder

On parle du noyau comme d'une abstraction. C'est pourtant un fichier ordinaire,
posé sur le disque, que le chargeur de démarrage lit et met en mémoire (étape 2
du démarrage dans le guide). Il porte un nom conventionnel, `vmlinuz`, et vit
dans `/boot` :

```bash
ls -l /boot/vmlinuz*
```

```text
lrwxrwxrwx 1 root root       25 juil. 18 06:30 /boot/vmlinuz -> vmlinuz-6.8.0-136-generic
-rw------- 1 root root 15042952 juin  26 18:36 /boot/vmlinuz-6.8.0-134-generic
-rw------- 1 root root 15063432 juil.  1 21:50 /boot/vmlinuz-6.8.0-136-generic
lrwxrwxrwx 1 root root       25 juil. 18 06:30 /boot/vmlinuz.old -> vmlinuz-6.8.0-134-generic
```

Quinze mégaoctets, une date, des droits `-rw-------` qui le réservent à
l'administrateur : vous pouvez le **lister** sans privilège, mais pas le lire,
et `file` sur ce fichier répond d'ailleurs `regular file, no read permission`.

Regardez de plus près : il y a **deux** noyaux installés, et le lien
`/boot/vmlinuz` pointe sur le plus récent, `6.8.0-136-generic`. Quel est celui
qui tourne réellement ?

```bash
uname -r
cat /proc/cmdline
```

```text
6.8.0-134-generic
BOOT_IMAGE=/vmlinuz-6.8.0-134-generic root=/dev/mapper/ubuntu--vg-ubuntu--lv ro
```

Le noyau en cours d'exécution est le `-134`, pas le `-136` : `/proc/cmdline`
donne la ligne exacte que le chargeur a passée au noyau au dernier démarrage,
et elle nomme le fichier chargé. Retenez la leçon, elle resservira toute votre
carrière : **installer un noyau ne le fait pas tourner**. Le nouveau attend sur
le disque, et seul un redémarrage bascule dessus. C'est pour cela qu'une mise à
jour de sécurité du noyau se solde par un « reboot required » qu'il ne faut pas
esquiver.

### Deux numéros de version qui n'ont rien à voir

Voici la confusion numéro un du débutant. Comparez ces deux sorties :

```bash
uname -r
cat /etc/os-release
```

```text
6.8.0-134-generic
PRETTY_NAME="Ubuntu 24.04.2 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.2 LTS (Noble Numbat)"
VERSION_CODENAME=noble
[...]
ID_LIKE=debian
[...]
```

`6.8.0` est la version du **noyau**, `24.04` celle de la **distribution** :
deux projets, deux équipes, deux rythmes, deux numérotations sans le moindre
rapport. Le tableau des versions du guide le montre bien, Ubuntu numérote par
année et mois de publication (26.04 est sorti en avril 2026), là où le noyau
suit sa propre suite. Répondre « je suis en 24.04 » à la question « quelle
version de noyau ? » est un contresens, et l'inverse aussi.

Les champs de `/etc/os-release` que vous lirez le plus souvent :

| Champ | Ce qu'il donne |
|---|---|
| `PRETTY_NAME` | le nom lisible par un humain, à afficher |
| `NAME` | le nom de la distribution, sans la version |
| `VERSION_ID` | la version, sous une forme comparable par un script |
| `VERSION_CODENAME` | le nom de code de la version (`noble` ici) |
| `ID` | l'identifiant court et normalisé, celui qu'un script teste |
| `ID_LIKE` | la famille dont la distribution dérive (`debian` ici) |

`ID_LIKE` est le plus utile en pratique : il dit qu'Ubuntu dérive de Debian,
donc que les commandes de cette famille s'y appliquent.

Une seule commande affiche les deux numéros ensemble, sur les systèmes équipés
de systemd (`dpkg -S "$(command -v hostnamectl)"` confirme que `hostnamectl`
est livrée par le paquet `systemd`) :

```bash
hostnamectl
```

```text
[...]
Operating System: Ubuntu 24.04.2 LTS
          Kernel: Linux 6.8.0-134-generic
    Architecture: x86-64
[...]
```

Le système d'exploitation d'un côté, le noyau de l'autre, l'architecture
matérielle en prime. `uname -a` donne la même chose en plus brut, sur une seule
ligne, en ajoutant la date de **construction** du noyau par la distribution,
qui n'est pas celle de son installation chez vous.

### Le noyau n'est pas le premier programme que vous voyez

Le noyau prend le contrôle du matériel, puis il lance un premier programme, et
ce programme n'est pas lui. C'est l'étape 6 du démarrage décrite dans le guide,
le fameux **PID 1** :

```bash
ps -p 1 -o pid,comm,args
ls -l /sbin/init
```

```text
    PID COMMAND         COMMAND
      1 systemd         /sbin/init
lrwxrwxrwx 1 root root 22 juin   5 17:36 /sbin/init -> ../lib/systemd/systemd
```

Le processus numéro 1 s'appelle `systemd`, il a été lancé sous le nom
`/sbin/init`, et ce chemin n'est qu'un lien symbolique vers le vrai programme.
Trois choses en découlent : le PID 1 est un **programme ordinaire** posé sur le
disque, il est **fourni par la distribution** et non par le noyau, et il est
donc **remplaçable**. Selon le guide, c'est lui qui gère tout ce qui suit.

La même logique vaut pour la moindre commande. Le guide décrit le trajet de
`ls` : le shell le lance, `ls` appelle la bibliothèque C, celle-ci traduit en
appels système, le noyau répond. Ce trajet se lit dans le binaire :
`ldd /usr/bin/ls` liste `libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6`, la
**bibliothèque C** (ici la GNU libc `2.39`, d'après `ldd --version`). C'est
elle, et non `ls`, qui parle au noyau. Le noyau, lui, n'apparaît nulle part
dans cette liste, et c'est justement le point : la frontière entre l'espace
utilisateur et le mode noyau ne se franchit que par des appels système.

### Ce qu'une distribution ajoute au noyau

Un noyau seul ne fait rien d'utile : il n'a ni shell, ni commandes, ni moyen
d'installer un logiciel. Le guide énumère ce que la distribution assemble
autour de lui. Chaque brique est identifiable sur votre machine :

| Brique | Rôle | Relevé sur la machine de rédaction | Commande |
|---|---|---|---|
| Gestionnaire de paquets | installer et mettre à jour | `apt 2.8.3` | `apt --version` |
| Système d'init (PID 1) | démarrer et superviser les services | `systemd 255` | `systemctl --version` |
| Bibliothèque C | interface entre programmes et noyau | GNU libc `2.39` | `ldd --version` |
| Outils de base | manipuler fichiers, texte, processus | GNU coreutils `9.4` | `ls --version` |
| Shell | interpréter vos commandes | GNU bash `5.2.21` | `bash --version` |

S'y ajoute une brique qui n'est pas un logiciel mais une **politique** : le
choix des versions, le rythme des publications et la durée pendant laquelle les
failles seront corrigées. L'assemblage n'est pas symbolique : sur ce poste,
`dpkg-query -f '.\n' -W | wc -l` compte **1296 paquets**, toute la distance
entre « le noyau Linux » et « un système Linux ». Le guide range les
distributions serveur en deux familles, sur des critères concrets :

| Critère | Famille Debian | Famille Red Hat |
|---|---|---|
| Distributions | Debian, Ubuntu Server | RHEL, Rocky Linux, AlmaLinux |
| Gestionnaire de paquets | `apt` (paquets `.deb`) | `dnf` (paquets `.rpm`) |
| Durée de support | Debian environ 5 ans, Ubuntu LTS 5 ans (+5 en ESM) | RHEL 10 ans |
| Coût | gratuit | RHEL payant par abonnement, Rocky et Alma gratuits |
| Terrain de prédilection | web, cloud, conteneurs, homelab | entreprise, SI critiques, certification RHCSA |
| Init | systemd | systemd |

La ligne « Init » n'est pas là par hasard : les deux familles ont **le même**
système d'init. Ce qui les sépare tient aux paquets, aux chemins de
configuration et à la politique de support, pas à l'architecture. Le guide cite
aussi Alpine, dont le gestionnaire est `apk`, ainsi qu'Arch et openSUSE, qu'il
donne pour rares en production serveur sans les détailler : ce cours n'en dira
donc pas davantage.

### Le vocabulaire qui embrouille, une ligne par piège

- **Linux**, c'est le noyau et rien d'autre : `uname -s` répond `Linux`, et ne
  parle que de lui.
- **GNU/Linux** désigne l'attelage complet, noyau de Torvalds plus outils du
  projet GNU. Ce n'est pas une posture militante : c'est ce que la machine
  répond à `uname -o`, et `ls --version` nomme au passage son auteur, Richard
  M. Stallman.
- **Noyau** et **système d'exploitation** ne sont pas synonymes : le second
  ajoute au premier une bibliothèque C, un init, des outils et un gestionnaire
  de paquets.
- **Distribution** et **version** ne sont pas au même niveau : Ubuntu est la
  distribution, `24.04` la version, `noble` le nom de code de cette version.
- **Paquet** et **logiciel** ne se confondent pas : `dpkg -S /usr/bin/ls` répond
  `coreutils`, donc `ls` n'a pas de paquet à lui, il voyage dans un colis qui en
  contient des dizaines. Ce colis porte son propre numéro, `9.4-3ubuntu6`, là où
  le logiciel s'annonce en `9.4` : le suffixe est le travail d'empaquetage de la
  distribution.
- **Dépôt** n'est pas **magasin d'applications** : c'est un serveur de paquets
  signés, déclaré dans la configuration du système, sans compte ni paiement.
  `apt-cache policy coreutils` en donne l'adresse réelle,
  `http://fr.archive.ubuntu.com/ubuntu noble/main`, et le composant final
  (`main` ici) dit quel niveau d'engagement la distribution prend sur ce paquet.
- **Libre** n'est pas **gratuit** : `ls --version` affiche `License GPLv3+` et
  `This is free software: you are free to change and redistribute it`, une
  liberté qui ne dit rien du prix. Le contre-exemple est dans le guide, RHEL est
  bâtie sur du logiciel libre et se vend par abonnement, tandis que Rocky Linux
  et AlmaLinux en sont des reconstructions gratuites.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `uname -r` ne correspond pas au fichier le plus récent de `/boot` | un noyau est installé mais pas encore démarré | `cat /proc/cmdline`, puis redémarrer |
| on vous demande « quelle version de Linux ? » et vous hésitez | la question est ambiguë, elle vise le noyau ou la distribution | `uname -r` pour le noyau, `/etc/os-release` pour la distribution |
| une commande d'un tutoriel n'existe pas sur votre machine | le tutoriel vise l'autre famille de distributions | lire `ID_LIKE` dans `/etc/os-release` |
| `hostnamectl : command not found` | la commande vient du paquet `systemd` | se rabattre sur `uname -a` et `cat /etc/os-release` |
| impossible de lire le noyau dans `/boot` | droits `-rw-------`, réservés à l'administrateur | `ls -l` suffit, il n'y a rien à lire dedans |

Aucune commande de ce cours n'a rien créé ni modifié : il n'y a rien à nettoyer.
