# Lab — créer un filesystem XFS

## Rappel

[**XFS sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/)

`mkfs.xfs <device>` crée un filesystem XFS ; `-L <label>` y appose un label
(`-f` force par-dessus une signature existante). `blkid` et `lsblk -f` montrent
le type, le label et l'UUID. Un filesystem doit être **monté** sur un répertoire
pour être utilisé.

## Le cours

Les exemples ci-dessous travaillent sur une partition d'essai `/dev/vdb2`,
labellisée `archives` puis `depot`, montée sur `/mnt/labo-xfs` : le challenge,
lui, vous demandera une autre partition, un autre label et un autre point de
montage. Le but est d'apprendre la méthode, pas de recopier une ligne. Toutes
les sorties ci-dessous ont été capturées sur AlmaLinux 10, avec
`xfsprogs-6.16.0` et le noyau `6.12.0`.

### Repérer la cible avant toute commande destructrice

`mkfs.xfs` ne pose pas de question de confirmation : il écrit. Une erreur de
lettre et c'est le disque système qui y passe. Le premier geste est donc
toujours de savoir où se trouve la racine, et de regarder l'arborescence des
disques :

```bash
findmnt -no SOURCE /
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

```text
/dev/vda4
NAME    SIZE TYPE FSTYPE  MOUNTPOINTS
sr0      46K rom  iso9660
vda      10G disk
├─vda1    1M part
├─vda2  200M part vfat    /boot/efi
├─vda3    1G part xfs     /boot
└─vda4  8.8G part xfs     /
vdb       2G disk
├─vdb1  200M part
└─vdb2  1.6G part xfs     /mnt/labo-xfs
```

Trois choses se lisent d'un coup d'œil : `/` vit sur `/dev/vda4`, donc **tout
ce qui commence par `vda` est interdit** ; la colonne `FSTYPE` vide signale une
partition qui ne porte encore aucun filesystem ; la colonne `MOUNTPOINTS`
montre ce qui est déjà monté.

Prenez l'habitude de **nommer la cible en toutes lettres** dans la commande,
plutôt que de la reprendre d'une variable ou d'un historique : c'est la seule
protection contre le mauvais disque.

### Créer le filesystem avec mkfs.xfs

La commande formate et, avec `-L`, pose le label dans le même geste :

```bash
sudo mkfs.xfs -L archives /dev/vdb2
```

```text
meta-data=/dev/vdb2              isize=512    agcount=4, agsize=65536 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=1, rmapbt=1
         =                       reflink=1    bigtime=1 inobtcount=1 nrext64=1
         =                       exchange=0   metadir=0
data     =                       bsize=4096   blocks=262144, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1, parent=0
log      =internal log           bsize=4096   blocks=16384, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
         =                       rgcount=0    rgsize=0 extents
         =                       zoned=0      start=0 reserved=0
Discarding blocks...Done.
```

Ce bloc résume la géométrie : **4 groupes d'allocation** (`agcount=4`, ce qui
permet à XFS d'écrire en parallèle), des **sommes de contrôle** sur les
métadonnées (`crc=1`), une **taille de bloc** de 4096 octets et un **journal
interne** de 16384 blocs.

Deux options utiles avant de lancer pour de bon :

- **`-N`** simule et n'écrit rien : la géométrie s'affiche, le disque n'est pas
  touché. Vérifié sur une partition démontée dont le label était `depot` :
  après un `mkfs.xfs -N -f -L essai /dev/vdb2`,
  `blkid -s LABEL -o value /dev/vdb2` renvoyait toujours `depot`.
- **`-d su=<stripe>,sw=<disques>`** aligne le filesystem sur un RAID, pour que
  les écritures tombent bien sur les bandes.

### Les trois refus de mkfs.xfs

Ce sont trois messages qu'il vaut mieux avoir déjà vus.

**Trop petit.** `mkfs.xfs` refuse en dessous de 300 Mo. Sur une partition de
200 Mio :

```bash
sudo mkfs.xfs -L essai /dev/vdb1
```

```text
Filesystem must be larger than 300MB.
Usage: mkfs.xfs
[...]
```

**Signature existante.** Reformater une partition qui porte déjà un filesystem
demande un accord explicite :

```bash
sudo mkfs.xfs -L archives /dev/vdb2
```

```text
mkfs.xfs: /dev/vdb2 appears to contain an existing filesystem (xfs).
mkfs.xfs: Use the -f option to force overwrite.
```

**Filesystem monté.** Et là, `-f` ne sert à rien, c'est le seul garde-fou que
`mkfs.xfs` n'accepte pas de lever :

```bash
sudo mkfs.xfs -f -L autre /dev/loop0     # /dev/loop0 était monté
```

```text
mkfs.xfs: /dev/loop0 contains a mounted filesystem
Usage: mkfs.xfs
```

Le label du filesystem était toujours `beta` après cette tentative : rien n'a
été écrit. Retenez la portée exacte de cette protection : elle couvre ce qui
est **monté**, donc une partition démontée, elle, se laisse écraser sans autre
question que le `-f`.

Le label a aussi une limite de longueur, que l'aide de la commande donne
(`-L label (maximum 12 characters)`) et qu'un essai confirme :

```bash
sudo mkfs.xfs -f -L archives-projet /dev/vdb2
```

```text
Invalid value archives-projet for -L option
```

### Lire le résultat

Trois commandes, trois points de vue.

```bash
sudo blkid /dev/vdb2
```

```text
/dev/vdb2: LABEL="archives" UUID="5fa995a5-90a2-4743-870b-7c48e31aeb18" BLOCK_SIZE="512" TYPE="xfs" PARTLABEL="essai-xfs" PARTUUID="4362f33c-8837-4458-862b-0803f020b0ba"
```

`blkid` lit la signature **sur le disque** : type, label, UUID. Ne confondez
pas `LABEL`/`UUID` (le filesystem) avec `PARTLABEL`/`PARTUUID` (l'entrée dans
la table de partitions GPT) : ce sont deux couches différentes, et c'est le
premier couple qui sert au montage.

```bash
lsblk -f /dev/vdb
```

```text
NAME   FSTYPE FSVER LABEL    UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
vdb
├─vdb1
└─vdb2 xfs          archives 5fa995a5-90a2-4743-870b-7c48e31aeb18
```

`lsblk -f` donne la même information dans l'arborescence des disques, ce qui
permet de voir d'un coup ce qui est formaté et ce qui ne l'est pas.

`xfs_info` enfin, propre à XFS, relit la géométrie d'un volume **monté** : même
sortie que `mkfs.xfs`, mais à la demande.

```bash
sudo xfs_info /mnt/labo-xfs | head -2
```

```text
meta-data=/dev/vdb2              isize=512    agcount=7, agsize=65536 blks
         =                       sectsz=512   attr=2, projid32bit=1
```

### Le label : le poser, le lire, le changer

`-L` au formatage pose le label. Ensuite, `xfs_admin` le lit et le change, sans
démonter :

```bash
sudo xfs_admin -l /dev/vdb2          # lire
sudo xfs_admin -L depot /dev/vdb2    # changer
```

```text
label = "archives"
label = "depot"
```

> **Après un changement de label à chaud, `lsblk -f` ment un moment.**
> Immédiatement après le `xfs_admin -L`, `blkid` renvoyait bien `depot`, mais
> `lsblk -f` affichait encore `archives` : `lsblk` lit la base udev, qui n'a pas
> été re-sondée. `sudo udevadm info --query=property --name=/dev/vdb2`
> confirmait `ID_FS_LABEL=archives`, et le lien `/dev/disk/by-label/archives`
> pointait toujours vers la partition. Un `sudo udevadm trigger --settle
> /dev/vdb2` remet tout d'aplomb, et `lsblk -f` affiche alors `depot`.

### Monter et démonter

Un filesystem n'existe pour l'utilisateur qu'une fois **monté** sur un
répertoire, qui doit exister au préalable :

```bash
sudo mkdir -p /mnt/labo-xfs
sudo mount /dev/vdb2 /mnt/labo-xfs
findmnt /mnt/labo-xfs
```

```text
TARGET        SOURCE    FSTYPE OPTIONS
/mnt/labo-xfs /dev/vdb2 xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

`findmnt` est plus lisible que `mount` : la colonne `SOURCE` confirme le bon
périphérique, `FSTYPE` le type réellement monté, `OPTIONS` ce qui est actif.

Le montage peut aussi désigner le filesystem par son label ou son UUID, ce qui
évite de dépendre du nom de périphérique :

```bash
sudo mount LABEL=depot /mnt/labo-xfs
sudo mount UUID=c58910f2-1557-466f-9ee7-6e75299d7e3f /mnt/labo-xfs
```

Un XFS neuf n'est jamais tout à fait vide : sur cette partition de 1,6 Gio,
`df` annonce déjà 62 Mo occupés, essentiellement le journal interne et les
métadonnées.

```bash
df -h /mnt/labo-xfs
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb2       1.5G   62M  1.5G   5% /mnt/labo-xfs
```

Démonter détache le filesystem : les données restent sur le disque, mais le
répertoire redevient un répertoire vide de la racine.

```bash
echo bonjour | sudo tee /mnt/labo-xfs/preuve.txt
sudo umount /mnt/labo-xfs
ls -A /mnt/labo-xfs                  # ne renvoie rien
sudo mount LABEL=depot /mnt/labo-xfs
cat /mnt/labo-xfs/preuve.txt         # bonjour
```

Si `umount` répond `target is busy`, un processus travaille dans le point de
montage : `sudo fuser -vm /mnt/labo-xfs` (ou `lsof`) le désigne.

### Nom de périphérique ou UUID

L'UUID n'est pas une coquetterie : un nom comme `/dev/vdb2` est **attribué par
le noyau dans l'ordre où il découvre les disques**, alors que l'UUID est écrit
**dans le superbloc du filesystem** et voyage avec les données.

Voici la démonstration, faite avec deux fichiers-disques attachés à des
périphériques loop, ce qui permet de rejouer une énumération dans un autre
ordre sans redémarrer. Deux XFS, l'un labellisé `alpha`, l'autre `beta` :

```bash
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="alpha" UUID="d0299cfa-2791-459c-81db-72d952012490" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="beta" UUID="4de82a27-4521-422f-b891-6e047e7acd6c" BLOCK_SIZE="512" TYPE="xfs"
```

On les détache, puis on les rattache dans l'ordre inverse, exactement ce que
fait un serveur dont on a permuté deux disques ou changé un contrôleur :

```bash
sudo losetup -d /dev/loop0 ; sudo losetup -d /dev/loop1
sudo losetup -f --show /var/tmp/demo-uuid/disque-b.img    # prend loop0
sudo losetup -f --show /var/tmp/demo-uuid/disque-a.img    # prend loop1
sudo blkid /dev/loop0 /dev/loop1
```

```text
/dev/loop0: LABEL="beta" UUID="4de82a27-4521-422f-b891-6e047e7acd6c" BLOCK_SIZE="512" TYPE="xfs"
/dev/loop1: LABEL="alpha" UUID="d0299cfa-2791-459c-81db-72d952012490" BLOCK_SIZE="512" TYPE="xfs"
```

`/dev/loop0` désigne maintenant **un autre filesystem**. Les UUID, eux, n'ont
pas bougé d'un caractère : ils ont simplement suivi leurs données, et les liens
que le noyau maintient le montrent.

```bash
ls -l /dev/disk/by-uuid/ | grep loop
```

```text
4de82a27-4521-422f-b891-6e047e7acd6c -> ../../loop0
d0299cfa-2791-459c-81db-72d952012490 -> ../../loop1
```

Une ligne `/etc/fstab` écrite avec `/dev/loop0` aurait monté le mauvais volume ;
la même écrite avec `UUID=` aurait monté le bon.

> **L'UUID change à chaque formatage.** Il appartient au filesystem, pas à la
> partition : `mkfs.xfs -f` en fabrique un nouveau. Constaté sur la même
> partition, avant puis après un reformatage :
> `5fa995a5-90a2-4743-870b-7c48e31aeb18` est devenu
> `c58910f2-1557-466f-9ee7-6e75299d7e3f`. D'où l'ordre des opérations : on
> formate d'abord, on relit l'UUID par `blkid`, **puis** on écrit la ligne
> `fstab`. L'inverse laisse une ligne qui pointe vers un UUID disparu.

### Rendre le montage persistant sans risquer le démarrage

`mount` ne survit pas au redémarrage. Pour que le filesystem revienne, il faut
une ligne dans `/etc/fstab`. Sauvegardez le fichier avant d'y toucher :

```bash
sudo cp -a /etc/fstab /root/fstab.orig
sudo blkid -s UUID -o value /dev/vdb2
```

La ligne compte six champs : source, point de montage, type, options, dump,
passe de vérification.

```text title="/etc/fstab"
UUID=c58910f2-1557-466f-9ee7-6e75299d7e3f  /mnt/labo-xfs  xfs  defaults,nofail  0 0
```

- **Source** : `UUID=`, pour la raison démontrée plus haut. `LABEL=` est
  acceptable aussi, à condition que le label soit unique sur la machine.
- **Type** : `xfs`.
- **Options** : `defaults`, plus `nofail` sur tout volume qui n'est pas
  indispensable au démarrage, pour que son absence ne bloque pas le boot.
- **Passe** : `0` pour XFS, qui ne se vérifie pas au démarrage. Les trois lignes
  d'origine du `/etc/fstab` de cette machine, toutes en XFS, portent bien `0`.

**Ne testez jamais par un redémarrage.** Deux commandes disent la même chose
sans risque, et elles se complètent.

```bash
sudo systemctl daemon-reload   # sinon findmnt --verify le réclame
sudo mount -a
sudo findmnt --verify
```

Sur la ligne correcte, `mount -a` ne dit rien du tout et rend 0, et la
vérification est nette :

```text
Success, no errors or warnings detected
```

Voici maintenant la même ligne avec **un seul caractère faux dans l'UUID** :

```text title="/etc/fstab (fautif)"
UUID=c58910f2-1557-466f-9ee7-6e75299d7e39  /mnt/labo-xfs  ext4  defaults  0 0
```

```bash
sudo findmnt --verify
```

```text
/mnt/labo-xfs
   [E] unreachable on boot required source: UUID=c58910f2-1557-466f-9ee7-6e75299d7e39

0 parse errors, 1 error, 0 warnings
```

```bash
sudo mount -a
```

```text
mount: /mnt/labo-xfs: can't find UUID=c58910f2-1557-466f-9ee7-6e75299d7e39.
```

C'est exactement le message qui, au démarrage, envoie la machine en *emergency
mode*. `findmnt --verify` le dit à froid, avec le code retour 1 et la mention
`required source` : sans `nofail`, cette ligne est **bloquante**.

Troisième cas, plus sournois, parce que le montage est possible mais mal
déclaré : le bon UUID, mais le type `ext4` sur un filesystem XFS.

```text
/mnt/labo-xfs
   [W] ext4 does not match with on-disk xfs

0 parse errors, 0 errors, 1 warning
```

```bash
sudo mount -a
```

```text
mount: /mnt/labo-xfs: wrong fs type, bad option, bad superblock on /dev/vdb2, missing codepage or helper program, or other error.
       dmesg(1) may have more information after failed mount system call.
```

Retenez le partage des rôles : `findmnt --verify` **relit le fichier** et
signale ce qui ne pourra pas marcher, y compris ce que `mount -a` ne
distinguerait pas d'une erreur générique ; `mount -a` **tente réellement** les
montages et prouve que la ligne fonctionne. Faites les deux avant de fermer le
fichier.

### Agrandir à chaud, et pourquoi on ne réduit pas

C'est la grande force de XFS en production. L'opération se fait toujours en
deux temps, **conteneur d'abord, filesystem ensuite** : agrandir le conteneur
(la partition avec `parted`, le volume logique avec `lvextend`), puis étendre le
filesystem. Tant que le second temps n'a pas eu lieu, rien ne change :

```bash
sudo parted /dev/vdb resizepart 2 1801MiB     # 1 Gio -> 1,6 Gio
sudo partprobe /dev/vdb
lsblk /dev/vdb ; df -h /mnt/labo-xfs
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
vdb    252:16   0    2G  0 disk
├─vdb1 252:17   0  200M  0 part
└─vdb2 252:18   0  1.6G  0 part /mnt/labo-xfs
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb2       960M   51M  910M   6% /mnt/labo-xfs
```

La partition fait bien 1,6 Gio, le filesystem est resté à 960 Mo. C'est
`xfs_growfs` qui comble l'écart, **sans démonter**, et sans qu'on ait à
préciser une taille : XFS prend toute la place de son conteneur.

```bash
sudo xfs_growfs /mnt/labo-xfs
```

```text
[...]
data blocks changed from 262144 to 409600
```

```bash
df -h /mnt/labo-xfs
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb2       1.5G   62M  1.5G   5% /mnt/labo-xfs
```

Au passage, `xfs_info` montrait ensuite `agcount=7` là où le formatage avait
créé 4 groupes d'allocation : l'agrandissement en ajoute, il ne redimensionne
pas les existants.

> **Attention à `parted -s` sur une partition montée.** En mode script, la
> commande a affiché `Warning: Partition /dev/vdb2 is being used. Are you sure
> you want to continue?` et **n'a rien fait** : la table est restée inchangée.
> Il faut répondre explicitement `Yes` pour que le redimensionnement ait lieu.
> Un script qui ne vérifie pas le résultat croira avoir agrandi la partition.

Dans l'autre sens, il n'y a rien. Aucun `xfs_shrink` n'existe :

```bash
ls /usr/sbin/xfs_* | tr '\n' ' '
```

```text
/usr/sbin/xfs_admin /usr/sbin/xfs_bmap /usr/sbin/xfs_copy /usr/sbin/xfs_db /usr/sbin/xfs_estimate /usr/sbin/xfs_freeze /usr/sbin/xfs_fsr /usr/sbin/xfs_growfs /usr/sbin/xfs_info /usr/sbin/xfs_io /usr/sbin/xfs_logprint /usr/sbin/xfs_mdrestore /usr/sbin/xfs_mkfile /usr/sbin/xfs_ncheck /usr/sbin/xfs_property /usr/sbin/xfs_protofile /usr/sbin/xfs_quota /usr/sbin/xfs_repair /usr/sbin/xfs_rtcp /usr/sbin/xfs_spaceman
```

Et demander à `xfs_growfs` une taille plus petite que l'actuelle échoue :

```bash
sudo xfs_growfs -D 262144 /mnt/labo-xfs
```

```text
[EXPERIMENTAL] try to shrink unused space 262144, old size is 409600
xfs_growfs: XFS_IOC_FSGROWFSDATA xfsctl failed: Invalid argument
```

Le mot `[EXPERIMENTAL]` montre qu'un chemin de réduction existe dans le code,
mais il a échoué ici : **ne comptez pas dessus**. En pratique, réduire un XFS
signifie sauvegarder, recréer plus petit, restaurer. Prévoyez donc la marge à
la création, ou posez le filesystem sur un volume logique LVM, où `lvextend -r`
enchaîne l'extension du volume et `xfs_growfs` en une commande.

### Vérifier et réparer

XFS ne se vérifie pas au démarrage (d'où le `0` en dernière colonne de
`fstab`). L'outil dédié est `xfs_repair`, et il exige un filesystem
**démonté** :

```bash
sudo xfs_repair -n /dev/vdb2      # -n : diagnostic seul, n'écrit rien
```

```text
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
[...]
No modify flag set, skipping phase 5
Phase 6 - check inode connectivity...
[...]
No modify flag set, skipping filesystem flush and exiting.
```

Sur un filesystem monté, il refuse net :

```text
xfs_repair: /dev/vdb2 contains a mounted and writable filesystem

fatal error -- couldn't initialize XFS library
```

Et attention à l'argument : `xfs_repair` attend un **périphérique**, pas un
point de montage. Passé `/mnt/labo-xfs`, il répond `xfs_repair: can't determine
device size`, message qui n'aide guère à comprendre l'erreur.

Sans `-n`, `xfs_repair` corrige. L'option `-L` efface le journal quand il est
corrompu au point d'empêcher le montage : c'est un **dernier recours**, il peut
perdre les écritures récentes.

### Options de montage utiles

| Option | Effet | Pour |
|---|---|---|
| `noatime` | n'écrit pas la date d'accès | volumes très sollicités |
| `nodev,nosuid,noexec` | durcit le montage | `/tmp`, disques externes |
| `nofail` | l'absence du volume ne bloque pas le boot | tout volume non essentiel |
| `uquota` / `gquota` / `pquota` | active les quotas XFS | volumes partagés |

Les quotas XFS sont natifs : une fois le volume monté avec `uquota`, ils se
pilotent avec `xfs_quota` (`xfs_quota -x -c 'report -h' <point de montage>`
pour l'état, `-c 'limit bsoft=... bhard=... <utilisateur>'` pour poser une
limite).

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `Filesystem must be larger than 300MB.` | volume trop petit pour XFS |
| `appears to contain an existing filesystem` | signature présente ; vérifier la cible, puis `-f` si certain |
| `contains a mounted filesystem` | démonter d'abord ; `-f` ne lève pas cette protection |
| `Invalid value ... for -L option` | label de plus de 12 caractères |
| `lsblk -f` affiche l'ancien label | base udev non re-sondée : `sudo udevadm trigger --settle <dev>` |
| `mount: can't find UUID=...` | UUID faux, ou filesystem reformaté depuis l'écriture de `fstab` |
| `wrong fs type, bad option, bad superblock` | type déclaré dans `fstab` différent du type réel |
| `umount: target is busy` | un processus occupe le point de montage : `fuser -vm <pt>` |
| `xfs_repair: contains a mounted ... filesystem` | démonter avant de réparer |
| Impossible de réduire le volume | XFS ne rétrécit pas : sauvegarder, recréer, restaurer |

### Tout défaire

```bash
sudo umount /mnt/labo-xfs
sudo cp -a /root/fstab.orig /etc/fstab     # restaurer la sauvegarde
sudo systemctl daemon-reload
sudo findmnt --verify                      # doit repasser au vert
sudo rmdir /mnt/labo-xfs
```

Le `daemon-reload` n'est pas décoratif : sans lui, systemd continue d'utiliser
l'ancienne version du fichier, et `findmnt --verify` le signale par
`[W] your fstab has been modified, but systemd still uses the old version`.
