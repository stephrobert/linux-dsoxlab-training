# Lab — partitionnement GPT avec parted

## Rappel

[**Partitions sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/)

Un disque neuf n'a aucune table de partitions : il faut commencer par en poser
une. `parted -s <disque> mklabel gpt` écrit une table GPT, `mkpart` y découpe
une partition entre deux offsets. GPT lève les limites du vieux MBR. Après
édition, le noyau doit relire la table (`partprobe <disque>`) pour que les
périphériques `<disque>1`, `<disque>2` apparaissent ; `lsblk` les montre.

## Le cours

Les exemples ci-dessous découpent des partitions de démonstration nommées
`demo1` et `demo2` : le challenge vous en demandera d'autres, d'autres tailles,
à d'autres offsets. Apprenez la méthode, elle se transpose ; ne recopiez pas les
chiffres.

Toutes les sorties de cette page ont été produites sur une VM **AlmaLinux 10**
(`parted` 3.6, `util-linux` 2.40.2), sur un disque de réserve de 2 Gio.

### Repérer le disque, et ne pas se tromper de lettre

C'est le seul geste de ce lab qui ne pardonne pas. Avant toute commande
destructrice, regardez qui porte le système :

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS
```

```text
NAME    SIZE TYPE MOUNTPOINTS
vda      10G disk
├─vda1    1M part
├─vda2  200M part /boot/efi
├─vda3    1G part /boot
└─vda4  8.8G part /
vdb       2G disk
```

`vda` porte `/`, `/boot` et `/boot/efi` : on n'y touche pas. `vdb` n'a aucune
partition et aucun point de montage, c'est le disque de réserve. Sur votre VM la
lettre peut différer : **vérifiez, ne supposez pas**, et nommez la cible
explicitement dans chaque commande.

Un disque vierge se reconnaît à deux sorties. `blkid` ne renvoie rien et sort en
erreur, `parted` annonce qu'il ne reconnaît pas d'étiquette :

```bash
sudo blkid /dev/vdb          # aucune sortie, code retour 2
sudo parted -s /dev/vdb print
```

```text
Error: /dev/vdb: unrecognised disk label
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 2147MB
Sector size (logical/physical): 512B/512B
Partition Table: unknown
```

La ligne **`Partition Table:`** est celle à surveiller tout au long du lab :
`unknown`, puis `msdos` ou `gpt`.

### MBR ou GPT : les deux limites, démontrées

Le guide résume le choix ainsi :

| Caractéristique | MBR (`msdos`) | GPT |
|---|---|---|
| Partitions primaires | **4** maximum | **128** en usage courant |
| Taille de disque gérée | **2 Tio** | très au-delà |
| Firmware | BIOS hérité | **UEFI** (et BIOS) |
| Table de secours | non | **oui** |

Ces deux limites ne sont pas théoriques, on les touche du doigt. En `msdos`, la
cinquième partition primaire est refusée :

```bash
sudo parted -s /dev/vdb mklabel msdos
sudo parted -s /dev/vdb mkpart primary 1MiB   101MiB
sudo parted -s /dev/vdb mkpart primary 101MiB 201MiB
sudo parted -s /dev/vdb mkpart primary 201MiB 301MiB
sudo parted -s /dev/vdb mkpart primary 301MiB 401MiB
sudo parted -s /dev/vdb mkpart primary 401MiB 501MiB    # la cinquième
```

```text
Error: Can't create any more partitions.
```

La limite des 2 Tio se montre sur un fichier creux de 3 Tio (il n'occupe rien
sur le disque tant qu'on n'y écrit pas) exposé en périphérique bloc :

```bash
sudo truncate -s 3T /var/tmp/gros.img     # « du » renvoie 0 : rien d'alloué
LOOP=$(sudo losetup --find --show /var/tmp/gros.img)
sudo parted -s $LOOP mklabel msdos
sudo parted -s $LOOP mkpart primary 1MiB 100%
```

```text
Error: partition length of 6442448896 sectors exceeds the
msdos-partition-table-imposed maximum of 4294967295
```

Le message donne le chiffre exact : 4 294 967 295 secteurs de 512 octets, soit
2 Tio pile. Le même disque en GPT accepte la partition entière :

```bash
sudo parted -s $LOOP mklabel gpt
sudo parted -s $LOOP mkpart data 1MiB 100%
sudo parted -s $LOOP print
```

```text
Partition Table: gpt

Number  Start   End     Size    File system  Name  Flags
 1      1049kB  3299GB  3299GB               data
```

Ne laissez pas traîner le montage de test : `sudo losetup -d $LOOP` puis
`sudo rm -f /var/tmp/gros.img`.

### Poser la table : `mklabel` efface tout, sans un mot

Retour sur le disque de réserve, qui portait à ce stade quatre partitions
`msdos`. Une seule commande, aucun avertissement, aucune question :

```bash
sudo parted -s /dev/vdb mklabel gpt      # code retour 0
sudo parted -s /dev/vdb print
```

```text
Partition Table: gpt

Number  Start  End  Size  File system  Name  Flags
```

Les quatre partitions ont disparu. `mklabel` ne convertit pas une table, il en
écrit une neuve par-dessus : **tout ce qui était décrit dedans est perdu**.

> Le mode `-s` (script) supprime les confirmations, c'est ce qui le rend
> utilisable dans un playbook. Il ne dit pas « oui » à tout pour autant : sur
> une opération jugée dangereuse par `parted`, il répond « non » et abandonne
> (voir le dépannage plus bas). Sur `mklabel`, il n'y a simplement aucune
> question posée.

### Découper avec `mkpart`

`mkpart` prend un nom, éventuellement un type de système de fichiers
(simple indication, aucun formatage n'a lieu), puis les bornes de début et de
fin :

```bash
sudo parted -s /dev/vdb mkpart demo1 1MiB 257MiB     # 256 Mio
sudo parted -s /dev/vdb mkpart demo2 257MiB 897MiB   # 640 Mio
```

La taille d'une partition est la **différence** entre les deux bornes, pas la
seconde borne : `1MiB 257MiB` donne 256 Mio, et la suivante repart exactement où
la précédente s'arrête pour ne pas laisser de trou. Le premier offset est `1MiB`
et non `0` : cet alignement sur 1 Mio est la convention qui garantit de bonnes
performances, `parted` l'applique automatiquement.

`parted print` affiche en méga-octets décimaux, `lsblk` en unités binaires
arrondies : 268 Mo et 256 Mio désignent la même chose.

```bash
sudo parted -s /dev/vdb print
```

```text
Number  Start   End    Size   File system  Name   Flags
 1      1049kB  269MB  268MB               demo1
 2      269MB   941MB  671MB               demo2
```

La colonne **File system** vide est normale : les partitions existent, elles ne
sont pas formatées. C'est l'étape suivante, avec `mkfs.ext4` ou `mkfs.xfs`.

### Le noyau, `/dev`, `partprobe` et `udevadm settle`

Trois vues coexistent, et elles ne se mettent pas à jour ensemble. Juste après
les deux `mkpart` ci-dessus :

```bash
ls -l /dev/vdb*                 # brw-rw----. 1 root disk 252, 16 /dev/vdb
grep vdb /proc/partitions
```

```text
 252       16    2097152 vdb
 252       17     262144 vdb1
 252       18     655360 vdb2
```

Le noyau connaît déjà les partitions (`/proc/partitions`, et `lsblk` qui lit
sysfs), mais les fichiers `/dev/vdb1` et `/dev/vdb2` n'existent pas encore :
c'est **udev** qui les crée, de façon asynchrone. Toute commande qui vise ce
chemin (`mkfs`, `pvcreate`, `mount`) échoue tant qu'il n'existe pas.

La fenêtre est courte et irrégulière. Le même `mkpart` suivi immédiatement d'un
`test -e`, joué trois fois de suite, a donné :

```text
run 1: node ABSENT immediatement
run 2: node present immediatement
run 3: node present immediatement
```

D'où le réflexe, dans un script comme à la main, avant d'enchaîner sur un
`mkfs` ou un `pvcreate` :

```bash
sudo partprobe /dev/vdb        # demande au noyau de relire la table
sudo udevadm settle            # attend que udev ait fini de peupler /dev
```

Les deux ne font pas la même chose : `partprobe` s'adresse au **noyau**,
`udevadm settle` attend **udev**. C'est le second qui règle le problème
ci-dessus ; le premier sert quand le noyau, lui, n'a pas pris la nouvelle table.

### Le type de partition : flag `parted` ou code `sgdisk`

Le type dit à quoi la partition est destinée (LVM, RAID, swap, EFI). Il ne
change rien au contenu, mais `pvcreate`, `mdadm` et les installateurs s'y fient.
Deux chemins mènent au même octet sur le disque. Par `parted`, c'est un flag :

```bash
sudo parted -s /dev/vdb set 1 lvm on
```

Par `sgdisk`, c'est un code à quatre chiffres hexadécimaux (`8300` Linux
filesystem, `8e00` LVM, `fd00` RAID, `ef00` EFI) :

```bash
sudo sgdisk -t 2:8e00 /dev/vdb
```

`sgdisk -p` montre le résultat des deux, dans la colonne `Code` :

```text
Number  Start (sector)    End (sector)  Size       Code  Name
   1            2048          526335   256.0 MiB   8E00  demo1
   2          526336         1837055   640.0 MiB   8E00  demo2
```

Et `parted print` affiche le même état sous forme de flag `lvm` sur les deux
partitions. Le code à quatre chiffres est un raccourci de `sgdisk` ; ce qui est
réellement écrit dans la table est un GUID de 128 bits, que `sgdisk -i` révèle :

```bash
sudo sgdisk -i 1 /dev/vdb
```

```text
Partition GUID code: E6D6D379-F507-44C2-A23C-238F2A3DF928 (Linux LVM)
Partition unique GUID: 8679E621-F137-4C28-87D7-31EB3BC8B89B
First sector: 2048 (at 1024.0 KiB)
Partition size: 524288 sectors (256.0 MiB)
Partition name: 'demo1'
```

Deux GUID différents : celui du **type** est le même sur toutes les partitions
LVM du monde, celui de la partition est unique et sert de `PARTUUID` dans
`/etc/fstab`.

> `sgdisk` et `gdisk` ne sont **pas installés** sur AlmaLinux 10, et le paquet
> `gdisk` n'est pas dans les dépôts de base : il vient d'EPEL
> (`sudo dnf install epel-release && sudo dnf install gdisk`). `parted` et
> `fdisk`, eux, sont là par défaut. Ne comptez pas sur `sgdisk` sur une machine
> que vous ne maîtrisez pas.

### Sauvegarder la table, dépanner, rendre le disque nu

Une table GPT tient dans quelques dizaines de kilo-octets et se sauvegarde en
une commande. C'est plus utile qu'un long discours sur la prudence :

```bash
sudo sgdisk --backup=/root/vdb-gpt.bak /dev/vdb   # 17920 octets ici
sudo sgdisk --zap-all /dev/vdb                    # tout est détruit
sudo sgdisk --load-backup=/root/vdb-gpt.bak /dev/vdb
sudo partprobe /dev/vdb && sudo udevadm settle
```

Après restauration, `parted print` retrouve les partitions, leurs noms et leurs
flags à l'identique. Attention : c'est la **table** qui est sauvegardée, pas les
données ; en revanche, restaurer la table suffit à retrouver des données
devenues invisibles après un mauvais `mklabel`.

GPT porte de plus une **copie de secours** en fin de disque. En écrasant
l'en-tête primaire (secteurs 1 à 33) et en relisant, `sgdisk` bascule seul :

```text
Caution: invalid main GPT header, but valid backup; regenerating main header
from backup!
Main header: ERROR
Backup header: OK
```

C'est la redondance annoncée dans le tableau MBR/GPT, vue en vrai. `sgdisk
--verify /dev/vdb` diagnostique, et un `--load-backup` répare (« No problems
found »).

| Symptôme | Cause probable |
|---|---|
| `Error: unrecognised disk label` | aucune table sur le disque : commencez par `mklabel` |
| `Error: Can't create any more partitions.` | table `msdos` et 4 partitions primaires : refaites la table en `gpt` |
| `/dev/<disque>N` introuvable juste après `mkpart` | udev n'a pas fini de peupler `/dev` : `sudo udevadm settle` |
| `Warning: Partition /dev/... is being used.` et code retour 1 | une partition du disque est montée ; `parted -s` refuse et abandonne. Démontez d'abord |
| Une partition neuve affiche un `FSTYPE` que vous n'avez pas créé | signature d'un ancien système de fichiers, restée en place ; `wipefs -a` sur la partition |

Ce dernier cas mérite un mot : `wipefs -a` sur le **disque** n'efface que les
signatures situées au début du disque. Une signature XFS ou ext4 enfouie plus
loin survit, et refait surface dès qu'une nouvelle partition recouvre sa
position. Pour rendre un disque réellement nu, il faut donc les deux passes,
partitions d'abord :

```bash
for p in /dev/vdb[0-9]*; do sudo wipefs -a "$p"; done
sudo wipefs -a /dev/vdb
```

```text
/dev/vdb2: 4 bytes were erased at offset 0x00000000 (xfs): 58 46 53 42
/dev/vdb: 8 bytes were erased at offset 0x00000200 (gpt): 45 46 49 20 50 41 52 54
/dev/vdb: 8 bytes were erased at offset 0x7ffffe00 (gpt): 45 46 49 20 50 41 52 54
/dev/vdb: 2 bytes were erased at offset 0x000001fe (PMBR): 55 aa
/dev/vdb: calling ioctl to re-read partition table: Success
```

`wipefs` retire bien les **deux** copies GPT (début et fin de disque) ainsi que
le MBR de protection. La preuve du retour à zéro :

```bash
sudo lsblk -f /dev/vdb
```

```text
NAME FSTYPE FSVER LABEL UUID FSAVAIL FSUSE% MOUNTPOINTS
vdb
```

Plus aucune partition, plus aucune signature : le disque est prêt à être
repartitionné.
