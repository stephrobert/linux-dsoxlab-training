# Lab — montage persistant par UUID

## Rappel

[**Montages persistants sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/)

`blkid` et `lsblk -f` montrent l'UUID d'un filesystem. Une ligne `/etc/fstab`
(`<quoi> <où> <type> <options> <dump> <pass>`) le monte au démarrage. Référence
le disque par `UUID=` — les noms comme `/dev/vdb` peuvent changer d'un reboot à
l'autre. `mount -a` monte tout ce que déclare fstab et valide ton entrée sans
redémarrer.

## Le cours

Les exemples ci-dessous travaillent sur `/mnt/depot`, un point de montage de
démonstration alimenté par une partition XFS : le challenge, lui, vous demandera
un autre répertoire, un autre système de fichiers et un autre disque. Le but est
d'apprendre la méthode et de la transposer, pas de recopier une ligne.

Toutes les sorties reproduites ici viennent d'une AlmaLinux 10 avec un disque
supplémentaire vierge. Les UUID changent d'une machine à l'autre : ne recopiez
jamais ceux du cours, lisez toujours les vôtres.

### Le décor de démonstration

Une partition d'un gibioctet est créée sur le disque supplémentaire, puis
formatée en XFS avec l'étiquette `depot` :

```bash
sudo parted -s /dev/vdb mklabel gpt mkpart depot xfs 1MiB 1025MiB
sudo partprobe /dev/vdb
sudo mkfs.xfs -L depot /dev/vdb1
```

```text
NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
vdb    252:16   0   2G  0 disk
└─vdb1 252:17   0   1G  0 part
```

Cette étape n'est là que pour fabriquer le décor. La vraie question commence
maintenant : comment désigner cette partition de façon durable.

### Trouver l'identifiant stable du filesystem

`blkid` interroge la signature écrite dans le système de fichiers :

```bash
sudo blkid /dev/vdb1
```

```text
/dev/vdb1: LABEL="depot" UUID="75605d28-9cd5-4ed4-aac4-a74fbbad926f" BLOCK_SIZE="512" TYPE="xfs" PARTLABEL="depot" PARTUUID="dcb8647b-a77a-4fb8-92bf-004409becd49"
```

Quatre identifiants sortent d'un coup, et ils ne désignent pas la même chose :

| Champ | Ce qu'il identifie | Posé par |
|---|---|---|
| `UUID` | le **système de fichiers** | `mkfs` |
| `LABEL` | le système de fichiers, par un nom que vous choisissez | `mkfs -L` |
| `PARTUUID` | la **partition** dans la table de partitions | `parted` |
| `PARTLABEL` | la partition, par un nom que vous choisissez | `parted` |

C'est l'`UUID` que ce lab utilise. Pour n'obtenir que lui, sans le reste :

```bash
sudo blkid -s UUID -o value /dev/vdb1
```

```text
75605d28-9cd5-4ed4-aac4-a74fbbad926f
```

`lsblk -f` donne la même information, en arborescence, et montre en plus le
point de montage courant :

```bash
lsblk -f /dev/vdb
```

```text
NAME   FSTYPE FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
vdb
└─vdb1 xfs          depot 75605d28-9cd5-4ed4-aac4-a74fbbad926f
```

La colonne `MOUNTPOINTS` est vide : le filesystem existe, mais il n'est monté
nulle part. Un disque formaté n'est pas un disque utilisable.

### Monter et démonter à la main

Le point de montage est un répertoire qui doit exister avant le montage :

```bash
sudo mkdir -p /mnt/depot
sudo mount /dev/vdb1 /mnt/depot
findmnt /mnt/depot
```

```text
TARGET     SOURCE    FSTYPE OPTIONS
/mnt/depot /dev/vdb1 xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

`findmnt` est plus lisible que `mount` sans argument : il ne montre que ce que
vous lui demandez. `SOURCE` confirme le périphérique, `FSTYPE` le type,
`OPTIONS` les options réellement actives.

`mount` accepte aussi directement l'UUID, ce qui évite de deviner le nom du
périphérique :

```bash
sudo mount UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f /mnt/depot
```

Ce montage reste **temporaire** : il disparaît au prochain démarrage tant que
rien ne l'inscrit dans `/etc/fstab`.

Pour démonter, la commande s'écrit `umount`, sans le premier `n`. Elle échoue
tant qu'un processus travaille dans le répertoire :

```bash
sudo umount /mnt/depot
```

```text
umount: /mnt/depot: target is busy.
```

Deux outils désignent le coupable. `fuser -vm` liste les processus, mais son
alignement de colonnes est trompeur, la valeur `kernel` débordant sur la ligne
d'en-tête :

```bash
sudo fuser -vm /mnt/depot
```

```text
kernel                     USER        PID ACCESS COMMAND
/mnt/depot:          root      mount /mnt/depot
                     16607 root      ..c.. sleep
```

`lsof` dit la même chose, sans ambiguïté sur le PID :

```bash
sudo lsof /mnt/depot
```

```text
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
sleep   16607 root  cwd    DIR 252,17        6  128 /mnt/depot
```

La colonne `FD` vaut ici `cwd` : le processus ne tient aucun fichier ouvert, il
a simplement son **répertoire courant** dans le point de montage. Cela suffit à
bloquer le démontage. Quittez le répertoire ou arrêtez le processus, puis
recommencez. Une fois démonté, `findmnt` n'affiche plus rien et renvoie le code
de retour `1`, ce qui en fait un test utilisable dans un script.

### Rendre le montage persistant dans /etc/fstab

`/etc/fstab` (*file systems table*) liste ce que le système monte au démarrage.
Une ligne, six champs séparés par des espaces :

```text title="/etc/fstab"
UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f  /mnt/depot  xfs  defaults,nofail  0 0
```

| Champ | Valeur ici | Rôle |
|---|---|---|
| quoi | `UUID=75605d28-...` | le filesystem à monter, par son identifiant stable |
| où | `/mnt/depot` | le point de montage, qui doit exister |
| type | `xfs` | le type du filesystem, qui doit correspondre au disque |
| options | `defaults,nofail` | options de montage, séparées par des virgules |
| dump | `0` | sauvegarde héritée, désactivée |
| passe | `0` | ordre de `fsck` au démarrage |

Sur la passe : `1` est réservé à la racine, `2` convient aux autres systèmes de
fichiers qui acceptent un `fsck` au démarrage, et `0` désactive la vérification.
XFS se vérifie au montage et non par `fsck` au boot, d'où le `0` ici.

L'option `nofail` est le garde-fou : si le disque est absent au démarrage, le
système continue de démarrer au lieu de s'arrêter en mode de dépannage. Elle est
recommandée sur tout ce qui n'est pas le disque système.

> **Sauvegardez avant d'éditer.** Une ligne fautive dans `/etc/fstab` peut
> empêcher la machine de redémarrer. Prenez le réflexe de
> `sudo cp -a /etc/fstab /etc/fstab.bak` avant la première modification : vous
> aurez de quoi revenir en arrière depuis un shell de secours.

### Vérifier sans redémarrer : le réflexe vital

Redémarrer pour savoir si une ligne est correcte est le pire des tests : si elle
est fautive, vous l'apprenez au moment où vous n'avez plus de machine. Deux
commandes répondent à chaud.

**`mount -a`** monte tout ce que déclare `fstab` et n'affiche rien quand tout va
bien :

```bash
sudo mount -a
findmnt /mnt/depot
```

```text
TARGET     SOURCE    FSTYPE OPTIONS
/mnt/depot /dev/vdb1 xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

**`findmnt --verify`** ne monte rien : il relit `/etc/fstab` et signale ce qui
clocherait au démarrage.

```bash
sudo findmnt --verify
```

```text
Success, no errors or warnings detected
```

Lancé juste après l'édition, il commence par vous rappeler une étape oubliée
neuf fois sur dix :

```text
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload

0 parse errors, 0 errors, 1 warning
```

systemd fabrique une unité `.mount` par entrée de `fstab`, au démarrage
seulement. Tant que vous n'avez pas rechargé, il travaille sur l'ancienne
version du fichier. Le commentaire en tête de `/etc/fstab`, sur AlmaLinux, le
dit déjà :

```text
# After editing this file, run 'systemctl daemon-reload' to update systemd
# units generated from this file.
```

D'où l'enchaînement à retenir après toute modification :

```bash
sudo systemctl daemon-reload
sudo findmnt --verify
sudo mount -a
```

Une fois l'entrée montée, systemd la gère comme une unité à part entière :

```bash
systemctl list-units --type=mount | grep depot
```

```text
  mnt-depot.mount               loaded active mounted /mnt/depot
```

Enfin, `findmnt --fstab` montre ce que le fichier **déclare**, à comparer avec
ce qui est **réellement** monté :

```bash
findmnt --fstab /mnt/depot
```

```text
TARGET     SOURCE                                    FSTYPE OPTIONS
/mnt/depot UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f xfs    defaults,nofail
```

### Ce que `mount -a` ne voit pas

Les deux commandes ne couvrent pas le même terrain, et c'est la raison de les
lancer toutes les deux. Trois cas où `mount -a` répond que tout va bien alors
que la ligne est fautive.

**Premier cas : le type ne correspond pas au disque.** La ligne annonce `vfat`
alors que la partition est en XFS, mais elle est déjà montée. `mount -a` ne
retouche pas un point de montage actif, donc il ne dit rien :

```bash
sudo mount -a           # code de retour 0, aucune sortie
sudo findmnt --verify
```

```text
/mnt/depot
   [W] vfat does not match with on-disk xfs

0 parse errors, 0 errors, 1 warning
```

`findmnt --verify` compare le type déclaré à la signature réellement présente
sur le disque. Au démarrage, machine froide, le montage échouera :

```bash
sudo umount /mnt/depot
sudo mount -a
```

```text
mount: /mnt/depot: wrong fs type, bad option, bad superblock on /dev/vdb1, missing codepage or helper program, or other error.
       dmesg(1) may have more information after failed mount system call.
```

**Deuxième cas : un UUID inexistant, avec `nofail`.** La ligne pointe un
identifiant qui n'existe sur aucun disque. `nofail` fait exactement son travail,
c'est-à-dire ne pas bloquer, et `mount -a` se tait :

```bash
sudo mount -a           # code de retour 0, aucune sortie
findmnt /mnt/depot      # code de retour 1, rien n'est monté
sudo findmnt --verify
```

```text
/mnt/depot
   [E] unreachable on boot required source: UUID=00000000-0000-0000-0000-000000000000

0 parse errors, 1 error, 0 warnings
```

C'est le piège le plus vicieux : le service démarre, mais le répertoire est
vide. Sans `nofail`, la même ligne se signale immédiatement :

```bash
sudo mount -a
```

```text
mount: /mnt/depot: can't find UUID=00000000-0000-0000-0000-000000000000.
```

**Troisième cas : une ligne incomplète.** Ici, l'UUID et le point de montage,
sans type ni options. Les deux outils la rejettent, mais le mot important est
`ignored` : la ligne n'a aucun effet, et le montage n'aura jamais lieu.

```text
findmnt: /etc/fstab: parse error at line 15 -- ignored

1 parse error, 0 errors, 0 warnings
```

Retenez la lecture du résumé de `findmnt --verify` : `parse errors` pour la
syntaxe, `errors` pour ce qui empêchera le montage, `warnings` pour ce qui
mérite un second regard. Seul `Success, no errors or warnings detected` autorise
un redémarrage serein.

### Pourquoi un UUID plutôt qu'un `/dev/vdX`

L'argument habituel est qu'un nom de périphérique « peut changer ». Le voici
démontré, sans redémarrer, avec deux fichiers image branchés comme des disques.
Chacun porte un marqueur qui permet de savoir lequel on a monté :

```bash
sudo truncate -s 400M /var/tmp/disque-a.img /var/tmp/disque-b.img
sudo mkfs.xfs -L ALPHA /var/tmp/disque-a.img
sudo mkfs.xfs -L BETA  /var/tmp/disque-b.img
sudo losetup -f --show /var/tmp/disque-a.img      # -> /dev/loop0
sudo losetup -f --show /var/tmp/disque-b.img      # -> /dev/loop1
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="ALPHA" UUID="a68aa8af-90a1-439c-8fe2-4d9eb0b0f312" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="BETA" UUID="00446362-527b-478c-9edd-06950d7a51bb" BLOCK_SIZE="512" TYPE="xfs"
```

Dans cet ordre, `/dev/loop0` est ALPHA. On détache tout, puis on rebranche dans
l'ordre inverse, exactement ce que fait un noyau qui énumère les disques dans un
ordre différent :

```bash
sudo losetup -d /dev/loop0 /dev/loop1
sudo losetup -f --show /var/tmp/disque-b.img      # -> /dev/loop0
sudo losetup -f --show /var/tmp/disque-a.img      # -> /dev/loop1
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="BETA" UUID="00446362-527b-478c-9edd-06950d7a51bb" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="ALPHA" UUID="a68aa8af-90a1-439c-8fe2-4d9eb0b0f312" BLOCK_SIZE="512" TYPE="xfs"
```

**`/dev/loop0` désigne maintenant l'autre filesystem.** Les UUID, eux, n'ont pas
bougé d'un caractère : ils sont attachés au contenu, pas au rang d'énumération.
Le noyau maintient d'ailleurs un répertoire d'alias qui suit les UUID :

```bash
ls -l /dev/disk/by-uuid/
```

```text
lrwxrwxrwx. 1 root root 11 Jul 22 14:43 00446362-527b-478c-9edd-06950d7a51bb -> ../../loop0
lrwxrwxrwx. 1 root root 11 Jul 22 14:43 a68aa8af-90a1-439c-8fe2-4d9eb0b0f312 -> ../../loop1
```

Les liens ont été refaits pour pointer vers les nouveaux noms. Une ligne
`/etc/fstab` écrite par UUID continue donc de trouver son filesystem, quand une
ligne écrite par nom monte le mauvais disque, en silence et sans la moindre
erreur. La démonstration tient en deux montages du même chemin, avant et après
l'inversion :

| Commande | Avant l'inversion | Après l'inversion |
|---|---|---|
| `sudo mount /dev/loop0 /mnt/essai` | `donnees du disque ALPHA` | `donnees du disque BETA` |
| `sudo mount UUID=a68aa8af-... /mnt/essai` | `donnees du disque ALPHA` | `donnees du disque ALPHA` |

Un montage par nom a changé de contenu sans prévenir. Sur une machine de
production, ce sont des sauvegardes écrites sur le disque de données, ou
l'inverse.

### L'UUID change à chaque formatage

Un UUID est stable dans le temps, mais il est **créé par `mkfs`**. Reformater
en fabrique un nouveau :

```bash
sudo blkid -s UUID -o value /dev/loop1
sudo mkfs.xfs -f -L ALPHA /dev/loop1
sudo blkid -s UUID -o value /dev/loop1
```

```text
a68aa8af-90a1-439c-8fe2-4d9eb0b0f312
02aaf5ac-e778-4d2d-a99f-27942d85c63d
```

L'étiquette `ALPHA` a survécu, parce qu'elle a été redonnée à `mkfs` ;
l'identifiant, lui, est neuf. Toute ligne `/etc/fstab` écrite avec l'ancien
UUID pointe désormais dans le vide :

```bash
sudo mount UUID=a68aa8af-90a1-439c-8fe2-4d9eb0b0f312 /mnt/essai
```

```text
mount: /mnt/essai: can't find UUID=a68aa8af-90a1-439c-8fe2-4d9eb0b0f312.
```

D'où l'ordre des opérations, qui n'est pas négociable : **formater d'abord,
relire l'UUID ensuite, écrire la ligne en dernier.** Un UUID relevé avant un
formatage est un UUID périmé.

### Vérifier que la ligne pointe bien le bon disque

Le contrôle final tient en deux commandes : ce que `fstab` déclare, et l'UUID
du filesystem réellement monté. Les deux doivent être identiques.

```bash
grep depot /etc/fstab
sudo blkid -s UUID -o value $(findmnt -no SOURCE /mnt/depot)
```

```text
UUID=75605d28-9cd5-4ed4-aac4-a74fbbad926f  /mnt/depot  xfs  defaults,nofail  0 0
75605d28-9cd5-4ed4-aac4-a74fbbad926f
```

`findmnt -no SOURCE` renvoie le périphérique effectivement monté, `blkid` en
extrait l'UUID : si la valeur diffère de celle de `fstab`, le montage courant
vient d'ailleurs et ne se reproduira pas au démarrage.

### Dépannage

| Symptôme | Cause probable | Ce qu'il faut faire |
|---|---|---|
| `umount: target is busy` | un processus a son répertoire courant ou un fichier ouvert dans le montage | `sudo lsof <point>` ou `sudo fuser -vm <point>`, quitter ou arrêter le processus |
| `mount: ... wrong fs type, bad option, bad superblock` | le type déclaré ne correspond pas au filesystem du disque | relire `TYPE=` dans `blkid` et corriger le troisième champ |
| `mount: ... can't find UUID=...` | UUID erroné, ou disque reformaté depuis l'écriture de la ligne | relire `sudo blkid -s UUID -o value <périphérique>` |
| `mount: ... mount point does not exist` | le répertoire cible n'a pas été créé | `sudo mkdir -p <point>` |
| `parse error at line N -- ignored` | ligne incomplète, un champ manque | six champs, séparés par des espaces |
| `[W] ... does not match with on-disk ...` | type déclaré faux, mais le filesystem est déjà monté donc `mount -a` se tait | corriger le type avant le prochain démarrage |
| `mount -a` ne dit rien et pourtant rien n'est monté | `nofail` sur une ligne dont la source est introuvable | `sudo findmnt --verify`, qui affiche `[E] unreachable` |
| `findmnt --verify` avertit que systemd utilise l'ancienne version | `fstab` modifié sans rechargement | `sudo systemctl daemon-reload` |
| Le montage disparaît après un redémarrage | aucune entrée dans `/etc/fstab` | ajouter la ligne, puis `daemon-reload`, `findmnt --verify`, `mount -a` |

### Tout défaire et repartir de zéro

```bash
sudo umount /mnt/depot
sudo cp -a /etc/fstab.bak /etc/fstab     # ou retirer la ligne à la main
sudo systemctl daemon-reload
sudo findmnt --verify
sudo rmdir /mnt/depot
```

Un dernier `sudo findmnt --verify` renvoyant `Success, no errors or warnings
detected` est la seule preuve acceptable qu'aucune ligne fautive ne reste
derrière vous.
