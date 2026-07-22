# Lab — l'arborescence standard (FHS)

## Rappel

[**Arborescence Linux : à quoi sert chaque répertoire**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/arborescence-fhs/)

Le **Filesystem Hierarchy Standard** (FHS) est la convention qui dit où Linux
range chaque type de fichier. Le guide le compare au plan d'un immeuble : chaque
étage a une fonction, et quand on connaît le plan on trouve du premier coup. Ce
lab ne demande pas de réciter une liste : il travaille les quelques
**distinctions** qui tranchent une vraie question d'administration, « où est-ce
que je pose ça ? » et « où est-ce que je vais le chercher ? ».

L'écriture des chemins est traitée dans `l1-paths-absolute-relative`, et la
lecture de `ls -l`, `file` et `stat` dans `l1-navigate-filesystem` : rien de tout
cela n'est repris ici.

## Le cours

Les exemples ci-dessous explorent des répertoires réels en **lecture seule** :
aucun ne recopie ce que le challenge demande, qui porte sur d'autres
emplacements. Aucune commande de ce cours n'a besoin de `sudo` et aucune n'écrit
quoi que ce soit.

Toutes les sorties reproduites ici ont été relevées sur **Ubuntu 24.04.2 LTS**,
noyau `6.8.0-134-generic`, avec `ls (GNU coreutils) 9.4`. C'est important : le
FHS est un standard, mais son application varie d'une distribution à l'autre et
d'une version à l'autre. Chez vous, les dates, les tailles et quelques entrées
différeront. Lancez les mêmes commandes sur votre machine et comparez.

### La racine, et ce qu'elle raconte

Tout part de `/`. Une seule commande donne la carte complète :

```bash
ls -l /
```

```text
lrwxrwxrwx   1 root root          7 avril 22  2024 bin -> usr/bin
drwxr-xr-x   2 root root       4096 févr. 26  2024 bin.usr-is-merged
drwxr-xr-x   5 root root       4096 juil. 18 06:31 boot
drwxr-xr-x  20 root root       4660 juil. 21 12:33 dev
drwxr-xr-x 128 root root      12288 juil. 22 06:25 etc
[...]
lrwxrwxrwx   1 root root          7 avril 22  2024 lib -> usr/lib
drwxr-xr-x   2 root root       4096 août  27  2024 media
drwxr-xr-x   6 root root       4096 juil.  2 19:19 mnt
drwxr-xr-x   8 root root       4096 juil.  2 18:34 opt
dr-xr-xr-x 975 root root          0 janv.  1  2022 proc
drwx------  13 root root       4096 juil.  6 08:15 root
drwxr-xr-x  42 root root       1380 juil. 22 18:03 run
lrwxrwxrwx   1 root root          8 avril 22  2024 sbin -> usr/sbin
drwxr-xr-x  13 root root       4096 févr.  5 18:12 snap
drwxr-xr-x   2 root root       4096 août  27  2024 srv
-rw-------   1 root root 4294967296 juil. 11  2025 swap.img
dr-xr-xr-x  13 root root          0 janv.  1  2022 sys
drwxrwxrwt 200 root root      36864 juil. 22 18:04 tmp
drwxr-xr-x  12 root root       4096 août  27  2024 usr
drwxr-xr-x  14 root root       4096 févr. 28 09:05 var
```

Trois choses sautent aux yeux, et aucune n'est un détail :

- **La racine n'est pas peuplée que de répertoires.** Pour `bin`, `lib` et
  `sbin`, la première colonne commence par `l` : ce sont des liens symboliques.
  `swap.img` commence par `-`, c'est un fichier ordinaire de 4 Gio.
- **Tout n'y est pas du FHS.** `snap` et `swap.img` sont des ajouts d'Ubuntu,
  `bin.usr-is-merged` une trace de migration. Le standard décrit le socle
  commun, pas la totalité de ce que vous verrez.
- **`proc` et `sys` affichent une taille de 0** et une date figée au 1er janvier
  2022 : ils ne sont pas sur le disque. On y revient plus bas.

Attention à un faux ami : **`/root` n'est pas `/`**. C'est le répertoire
personnel de l'administrateur, et ses droits `drwx------` le réservent à lui
seul.

### Le usr-merge : `/bin`, `/sbin` et `/lib` ne sont plus des répertoires

C'est le point où une bonne moitié des documentations encore en ligne est
périmée. Historiquement, `/bin` et `/sbin` contenaient les binaires nécessaires
au démarrage, avant que `/usr` ne soit monté ; `/usr/bin` et `/usr/sbin`
contenaient le reste. Cette séparation n'a plus lieu d'être, et les
distributions modernes l'ont supprimée. Mesurez-le :

```bash
ls -ld /bin /sbin /lib /lib64
```

```text
lrwxrwxrwx 1 root root 7 avril 22  2024 /bin -> usr/bin
lrwxrwxrwx 1 root root 7 avril 22  2024 /lib -> usr/lib
lrwxrwxrwx 1 root root 9 avril 22  2024 /lib64 -> usr/lib64
lrwxrwxrwx 1 root root 8 avril 22  2024 /sbin -> usr/sbin
```

Les quatre sont des liens : sur cette machine, `/bin` et `/usr/bin` **sont le
même répertoire**. Le guide date cette fusion, le usr-merge, de Debian 12+,
Ubuntu 22.04+, RHEL 9+, Fedora et Arch ; Alpine, elle, garde la séparation.

La distinction qui **reste** vivante n'est donc pas `/` contre `/usr`, mais
`bin` contre `sbin` : `/usr/bin` porte les commandes de tout le monde,
`/usr/sbin` celles d'administration (`fdisk`, `useradd`, `iptables` d'après le
guide). Un binaire introuvable en tant qu'utilisateur ordinaire est souvent
simplement dans `sbin`, hors de votre `PATH`.

Même histoire pour l'état d'exécution : `/var/run` a été remplacé par `/run`, et
n'en est plus qu'un lien.

```bash
ls -ld /var/run /var/lock
```

```text
lrwxrwxrwx 1 root root 9 août  27  2024 /var/lock -> /run/lock
lrwxrwxrwx 1 root root 4 août  27  2024 /var/run -> /run
```

Une documentation qui vous fait écrire un fichier PID dans `/var/run`
fonctionnera encore, par ce lien, mais l'emplacement à écrire aujourd'hui est
`/run`.

### `/usr`, `/usr/local` et `/opt` : trois façons d'installer un logiciel

`/usr` est le cœur applicatif : c'est là que le gestionnaire de paquets dépose
tout ce qu'il installe.

| Chemin | Contenu (guide) |
|---|---|
| `/usr/bin/` | commandes utilisateur |
| `/usr/sbin/` | commandes d'administration |
| `/usr/lib/` | bibliothèques partagées et fichiers de support |
| `/usr/share/` | documentation et données indépendantes de l'architecture |
| `/usr/local/` | logiciels installés **manuellement**, hors gestionnaire de paquets |

La question qu'un administrateur se pose vraiment est : *je viens de télécharger
un binaire, où le mets-je ?* La réponse tient en une règle : **pas dans
`/usr/bin`**, que le gestionnaire de paquets écrasera à la prochaine mise à
jour. Deux emplacements sont prévus pour vous, avec deux conventions
différentes :

- `/usr/local/` reproduit la structure de `/usr` (`bin`, `sbin`, `lib`, `etc`,
  `share`) et accueille les binaires isolés ;
- `/opt/<produit>/` accueille une application tierce **auto-contenue**, qui
  garde ses fichiers groupés dans son propre dossier.

Les deux se combinent souvent, et la machine d'essai en donne un exemple net :

```bash
ls -l /opt/opentofu ; ls -l /usr/local/bin/tofu
```

```text
total 110740
[...]
-rwxr-xr-x 1 student  student  113348792 janv. 21 17:10 tofu
lrwxrwxrwx 1 root root        18 janv. 31 20:10 /usr/local/bin/tofu -> /opt/opentofu/tofu
```

Le produit vit groupé dans `/opt`, et un simple lien depuis `/usr/local/bin` le
rend appelable. Pourquoi celui-là ? Parce qu'il est dans le `PATH`, et **avant**
les répertoires du système : `echo "$PATH"` contient ici, dans cet ordre,
`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`. `/usr/local/bin`
précède `/usr/bin`, donc votre version maison l'emporte sur celle du paquet.
C'est voulu, et c'est aussi un piège classique de dépannage.

### `/etc`, `/var`, `/srv` : la configuration, l'état, les données servies

Ces trois répertoires répondent à trois questions distinctes, et les confondre
est l'erreur de rangement la plus fréquente.

**`/etc` : ce que vous décidez.** Uniquement de la configuration, en fichiers
texte éditables, un sous-répertoire par service. `ls -d /etc/*/` les liste, et
`ls -d /etc/*/ | wc -l` en compte 126 sur la machine d'essai : `/etc/apache2/`,
`/etc/apt/`, `/etc/cron.d/`, `/etc/ssh/`, `/etc/systemd/` et cent vingt et une
autres.

La règle d'or du guide vaut d'être retenue mot pour mot : **ne modifiez jamais
un fichier dans `/usr/lib/` ou `/usr/share/`**, copiez-le ou surchargez-le dans
`/etc/`. Un exemple réel de ce mécanisme :

```bash
ls -l /usr/lib/systemd/system/containerd.service /etc/systemd/system/containerd.service.d/
```

```text
-rw-r--r-- 1 root root 1242 déc.  18  2025 /usr/lib/systemd/system/containerd.service

/etc/systemd/system/containerd.service.d/:
total 4
-rw-r--r-- 1 root root 78 janv. 23 10:36 override.conf
```

Le paquet fournit l'unité dans `/usr/lib`, l'administrateur la surcharge dans
`/etc`. Une mise à jour remplacera la première et laissera la seconde intacte.

**`/var` : ce que la machine produit.** Tout ce qui grossit, change, s'accumule
pendant que le système tourne.

| Chemin | Contenu (guide) |
|---|---|
| `/var/lib/` | état persistant des services (bases, paquets) |
| `/var/cache/` | caches, nettoyables pour récupérer de l'espace |
| `/var/spool/` | files d'attente (impression, mail, cron) |
| `/var/tmp/` | fichiers temporaires persistants |

`/var/lib` est la réponse à « où ce service range-t-il ses données ? ». Sur la
machine d'essai il contient une entrée par service installé : `apt`,
`containerd`, `docker`, `dpkg`, `libvirt`, `kubelet`. Le guide prévient qu'un
`/var` saturé peut bloquer le système entier quand il partage la partition
racine, d'où l'usage de le séparer en production (`df -h /var`).

**`/srv` : ce que la machine sert aux autres.** Le contenu qu'un serveur expose
(sites, dépôts, partages). C'est le seul des trois dont le remplissage est
laissé libre, et sur un poste de travail il est simplement vide : `ls -A /srv`
n'affiche aucune ligne et rend pourtant le code retour 0, la preuve que le
répertoire existe mais que rien ne l'occupe. Notez que beaucoup de distributions
servent malgré tout leurs sites depuis `/var/www`.

### `/tmp` contre `/var/tmp` : lequel survit au redémarrage

Les deux sont accessibles en écriture à tout le monde, avec le bit collant
(`t` final) qui empêche de supprimer le fichier d'autrui :

```bash
ls -ld /tmp /var/tmp
```

```text
drwxrwxrwt 200 root root 36864 juil. 22 18:04 /tmp
drwxrwxrwt  11 root root  4096 juil. 22 17:47 /var/tmp
```

La différence est **la durée de vie** : `/tmp` est vidé au redémarrage,
`/var/tmp` survit. Une idée reçue attribue cela au fait que `/tmp` serait en
RAM. C'est faux ici, et c'est vérifiable :

```bash
df -Th /tmp /var/tmp
```

```text
Filesystem                        Type  Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv ext4  914G  537G  339G  62% /
/dev/mapper/ubuntu--vg-ubuntu--lv ext4  914G  537G  339G  62% /
```

Les deux sont sur la même partition `ext4`, la racine. `/tmp` n'est donc pas un
`tmpfs` sur cette machine, et il est pourtant bien vidé : c'est `systemd` qui
s'en charge, sur la foi d'une règle déclarée :

```bash
grep -Ev '^#|^$' /usr/lib/tmpfiles.d/tmp.conf
systemctl cat systemd-tmpfiles-setup.service | grep ExecStart
```

```text
D /tmp 1777 root root 30d
ExecStart=systemd-tmpfiles --create --remove --boot --exclude-prefix=/dev
```

La ligne `D /tmp` est active, celle qui concerne `/var/tmp` est commentée dans
ce même fichier. Le service tourne au démarrage avec `--remove --boot`. **La
conclusion pratique ne change pas** : un fichier que vous voulez retrouver après
un reboot ne va pas dans `/tmp`. Et dans un script, créez-le avec `mktemp`
plutôt qu'avec un nom fixe, pour éviter les collisions et les attaques par lien
symbolique.

### `/proc`, `/sys`, `/run` : des fichiers qui ne sont pas sur le disque

Ce sont des **systèmes de fichiers virtuels**, générés à la volée par le noyau.
Leurs fichiers n'ont pas de contenu stocké, et leur taille affichée ne veut rien
dire :

```bash
ls -l /proc/uptime ; cat /proc/uptime ; wc -c /proc/uptime
```

```text
-r--r--r-- 1 root root 0 juil. 14 18:39 /proc/uptime
728281.78 10823041.61
22 /proc/uptime
```

Zéro octet annoncé, vingt-deux octets lus. Le fichier est fabriqué au moment où
vous le lisez : ces deux nombres sont les secondes écoulées depuis le démarrage
et le temps cumulé d'inactivité des cœurs. Côté `/sys`, la taille annoncée n'est
pas 0 mais 4096, la taille d'une page mémoire, ce qui ne dit rien de plus :
`ls -l /sys/class/net/lo/mtu` annonce 4096 octets, `cat` du même fichier répond
`65536` et `wc -c` en compte six.

La preuve qu'ils ne consomment aucun disque tient en une commande :

```bash
findmnt -t proc,sysfs,tmpfs -o TARGET,SOURCE,FSTYPE,SIZE
```

```text
TARGET     SOURCE  FSTYPE  SIZE
/sys       sysfs   sysfs      0
/proc      proc    proc       0
/run       tmpfs   tmpfs   4,7G
[...]
```

Leur source n'est pas un périphérique bloc mais `proc` et `sysfs` eux-mêmes,
pour une taille nulle ; `df -hT /proc /sys` le confirme avec des colonnes
`Size`, `Used` et `Avail` à 0. `/run` est un `tmpfs`, donc de la mémoire vive :
il porte
l'état d'exécution des services (fichiers PID, sockets, verrous) et repart vide
à chaque démarrage.

De là vient la règle du guide : **on ne sauvegarde jamais `/proc` ni `/sys`**.
Les inclure dans un `tar` ou un `rsync` de la racine ne copie aucune donnée
utile et provoque erreurs ou boucles ; excluez-les toujours.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| une doc distingue `/bin` de `/usr/bin` et vous n'observez aucune différence | usr-merge : ce sont les mêmes | `ls -ld /bin /sbin /lib` |
| `command not found` sur une commande d'administration | elle est dans `sbin`, hors de votre `PATH` | `echo "$PATH"` |
| une commande installée à la main est ignorée au profit de l'ancienne | ordre du `PATH`, `/usr/local/bin` d'abord | `type -a <commande>` |
| un réglage modifié n'est pas pris en compte | édité dans `/usr/lib/`, écrasé par la mise à jour | surcharger sous `/etc/` |
| un fichier a disparu après un redémarrage | il était dans `/tmp` | utiliser `/var/tmp` |
| un fichier de `/proc` affiche 0 octet | système de fichiers virtuel | `cat` puis `wc -c` |
| une sauvegarde de `/` échoue ou n'en finit pas | `/proc` et `/sys` non exclus | `findmnt -t proc,sysfs` |
| `No space left on device` alors que `df -h /` semble correct | `/var` sur une partition à part | `df -h /var` |

Aucune commande de ce cours n'a rien créé : il n'y a rien à nettoyer.
