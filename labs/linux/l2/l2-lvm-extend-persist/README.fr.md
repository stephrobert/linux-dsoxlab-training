# Lab — Étendre un volume logique, durablement

## Rappel

[**LVM sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/)

Un volume logique peut grandir alors qu'il est monté. L'ordre compte : d'abord
`lvextend` sur le volume logique, ensuite l'agrandissement du **filesystem** par
dessus (`xfs_growfs` pour XFS, `resize2fs` pour ext4). Étendre le LV sans
agrandir le filesystem est l'erreur la plus courante : l'espace ajouté reste
invisible. La persistance vit dans `/etc/fstab`, toujours par **UUID**.

## Le cours

Les exemples ci-dessous montent une pile de démonstration : un groupe de
volumes `vgatelier`, un volume logique `lvarchives` monté sur `/srv/archives`.
Le challenge, lui, vous demandera d'autres noms, un autre point de montage et
d'autres tailles. Le but est d'apprendre la méthode, pas de recopier une ligne.

Toutes les sorties ci-dessous ont été produites sur une VM **AlmaLinux 10.2**
avec `lvm2-2.03.36`, `xfsprogs-6.16.0` et `e2fsprogs-1.47.1`. Les messages de
LVM ont changé de forme entre les versions : lisez les vôtres, ne les supposez
pas.

### Avant tout : savoir sur quel disque on travaille

C'est la précaution qui n'a l'air de rien jusqu'au jour où elle manque. Une
commande LVM ne demande pas confirmation quand elle écrase un disque système.
Regardez donc **ce qui existe** avant de nommer une cible :

```bash
lsblk
sudo pvs
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sr0     11:0    1   46K  0 rom
vda    252:0    0   10G  0 disk
├─vda1 252:1    0    1M  0 part
├─vda2 252:2    0  200M  0 part /boot/efi
├─vda3 252:3    0    1G  0 part /boot
└─vda4 252:4    0  8.8G  0 part /
vdb    252:16   0    2G  0 disk
```

`pvs` ne renvoie **rien** : aucun volume physique LVM n'existe encore sur cette
machine. `lsblk` montre que `/dev/vda` porte `/boot`, `/boot/efi` et `/`, en
partitions classiques. C'est le disque système : on n'y touche pas. Le disque
libre est `/dev/vdb`, 2 Gio, sans aucun point de montage.

Sur d'autres installations, `/` est lui-même dans un volume logique. Dans ce
cas `pvs` répond, et `lsblk` affiche des lignes de type `lvm` sous `vda`.
Raison de plus pour **toujours nommer la cible explicitement** (`/dev/vdb1`)
plutôt que de compter sur un raccourci.

### Le modèle PV / VG / LV

LVM empile trois couches, et tout le reste en découle :

| Couche | Ce que c'est | Commande de création |
|---|---|---|
| **PV** (*Physical Volume*) | un disque ou une partition initialisé pour LVM | `pvcreate` |
| **VG** (*Volume Group*) | un réservoir d'espace qui agrège un ou plusieurs PV | `vgcreate` |
| **LV** (*Logical Volume*) | une tranche découpée dans le VG, que l'on formate et monte | `lvcreate` |

L'intérêt : un LV n'est plus lié à un disque précis. Quand le LV se remplit, on
l'agrandit en puisant dans le VG ; quand le VG manque d'espace, on lui ajoute un
disque. Sans reformater, sans démonter.

Trois commandes d'inspection, une par couche, à connaître par cœur : `pvs`,
`vgs`, `lvs`. Leurs variantes `pvdisplay`, `vgdisplay`, `lvdisplay` détaillent
davantage.

### Monter la pile de démonstration

On découpe d'abord le disque libre en deux partitions marquées LVM. Deux
partitions et non une : elles serviront plus loin à montrer comment on agrandit
un groupe de volumes déjà plein.

```bash
sudo parted -s /dev/vdb mklabel gpt
sudo parted -s /dev/vdb mkpart lvm1 1MiB 1300MiB
sudo parted -s /dev/vdb mkpart lvm2 1300MiB 100%
sudo parted -s /dev/vdb set 1 lvm on
sudo parted -s /dev/vdb set 2 lvm on
sudo partprobe /dev/vdb
lsblk /dev/vdb
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
vdb    252:16   0    2G  0 disk
├─vdb1 252:17   0  1.3G  0 part
└─vdb2 252:18   0  747M  0 part
```

Puis la pile proprement dite :

```bash
sudo pvcreate /dev/vdb1
sudo vgcreate vgatelier /dev/vdb1
sudo lvcreate -L 512M -n lvarchives vgatelier
```

```text
  Physical volume "/dev/vdb1" successfully created.
  Creating devices file /etc/lvm/devices/system.devices
  Volume group "vgatelier" successfully created
  Logical volume "lvarchives" created.
```

La ligne `Creating devices file` apparaît au tout premier `pvcreate` de la
machine : LVM 2.03 tient dans `/etc/lvm/devices/system.devices` la liste des
périphériques qu'il s'autorise à utiliser. C'est une note d'information, pas une
erreur.

Le volume logique est accessible par deux chemins équivalents :
`/dev/vgatelier/lvarchives` et `/dev/mapper/vgatelier-lvarchives`. On l'inspecte
couche par couche :

```bash
sudo pvs
sudo vgs
sudo lvs
```

```text
  PV         VG        Fmt  Attr PSize  PFree
  /dev/vdb1  vgatelier lvm2 a--  <1.27g 784.00m

  VG        #PV #LV #SN Attr   VSize  VFree
  vgatelier   1   1   0 wz--n- <1.27g 784.00m

  LV         VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lvarchives vgatelier -wi-a----- 512.00m
```

`VFree` est la colonne qui décide de tout : 784 Mio encore disponibles dans le
réservoir, c'est exactement la marge d'extension.

Reste à formater et monter, comme n'importe quelle partition :

```bash
sudo mkfs.xfs /dev/vgatelier/lvarchives
sudo mkdir -p /srv/archives
sudo mount /dev/vgatelier/lvarchives /srv/archives
findmnt /srv/archives
df -h /srv/archives
```

```text
TARGET        SOURCE                           FSTYPE OPTIONS
/srv/archives /dev/mapper/vgatelier-lvarchives xfs    rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  448M   35M  414M   8% /srv/archives
```

Premier écart à ne pas prendre pour un bug : le LV fait **512 Mio**, `df`
annonce **448 Mio**. La différence est occupée par les métadonnées de XFS, dont
son journal interne (16 384 blocs de 4 Kio, soit 64 Mio, visibles dans la sortie
de `mkfs.xfs`). `lvs` mesure le contenant, `df` mesure ce qui reste pour vos
fichiers : les deux chiffres ne coïncident jamais.

### Rendre le montage persistant, par UUID

Un `mount` manuel disparaît au redémarrage. Pour qu'il revienne, il faut une
ligne dans `/etc/fstab`, et cette ligne se réfère au filesystem par son **UUID**,
jamais par un nom de périphérique.

```bash
sudo blkid /dev/vgatelier/lvarchives
```

```text
/dev/vgatelier/lvarchives: UUID="2b81f1ac-3778-4231-abe1-6c853d55ee33" BLOCK_SIZE="512" TYPE="xfs"
```

```text title="/etc/fstab"
UUID=2b81f1ac-3778-4231-abe1-6c853d55ee33  /srv/archives  xfs  defaults  0 0
```

Les six colonnes, dans l'ordre : la source (UUID), le point de montage, le type,
les options, `dump` (0, fonction héritée) et la passe de `fsck` au démarrage. La
passe vaut `0` pour XFS, qui n'utilise pas `fsck` au boot.

> **Sauvegardez avant d'éditer.** Une ligne fautive dans `/etc/fstab` peut faire
> démarrer la machine en mode de secours. `sudo cp -a /etc/fstab /root/fstab.bak`
> coûte une seconde.

La vérification se fait **sans redémarrer**, avec deux commandes
complémentaires :

```bash
sudo mount -a           # tente réellement de monter tout ce qui manque
sudo findmnt --verify   # analyse le fichier sans rien monter
```

`mount -a` qui ne dit rien, c'est le succès. `findmnt --verify`, lui, parle même
quand tout va bien :

```text

0 parse errors, 0 errors, 1 warning
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload
```

Cet avertissement mérite une explication, parce qu'il n'a rien d'anodin :
systemd construit des unités de montage **à partir** de `/etc/fstab` au
démarrage, et il travaille sur la copie qu'il a en mémoire. Tant que vous n'avez
pas rechargé, le montage est actif mais systemd ignore la nouvelle entrée. D'où
le geste, que l'en-tête du `/etc/fstab` d'AlmaLinux rappelle lui-même en
commentaire :

```bash
sudo systemctl daemon-reload
sudo findmnt --verify
```

```text
Success, no errors or warnings detected
```

Voyons maintenant ce que donne une ligne fautive. Une seule lettre change dans
l'UUID (`...ee33` devient `...ee34`), le genre de faute de frappe qu'on ne voit
pas à la relecture :

```bash
sudo umount /srv/archives
# ligne modifiée dans /etc/fstab, dernier caractère de l'UUID
sudo mount -a
```

```text
mount: /srv/archives: can't find UUID=2b81f1ac-3778-4231-abe1-6c853d55ee34.
```

`findmnt --verify` est encore plus explicite, et n'a même pas besoin de démonter
quoi que ce soit pour détecter le problème :

```text
/srv/archives
   [E] unreachable on boot required source: UUID=2b81f1ac-3778-4231-abe1-6c853d55ee34
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload

0 parse errors, 1 error, 1 warning
```

`unreachable on boot` dit exactement ce qui se passerait au redémarrage. C'est
la raison pour laquelle on ne teste **jamais** une entrée `fstab` en rebootant :
on la teste à chaud, pendant que la machine est encore réparable.

### Étendre en deux temps : ce que voit `lvs`, ce que voit `df`

Voici le cœur du sujet, et l'erreur qui coûte des points en examen. Le volume
contient déjà des données (un fichier de 50 Mio a été déposé dans
`/srv/archives`), et il n'est **pas** démonté : toute l'opération se fait en
ligne.

```bash
sudo lvextend -L 768M /dev/vgatelier/lvarchives
```

```text
  Size of logical volume vgatelier/lvarchives changed from 512.00 MiB (128 extents) to 768.00 MiB (192 extents).
  Logical volume vgatelier/lvarchives successfully resized.
```

LVM annonce un succès franc. Et pourtant :

```bash
sudo lvs vgatelier/lvarchives
df -h /srv/archives
```

```text
  LV         VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lvarchives vgatelier -wi-ao---- 768.00m

Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  448M   85M  364M  19% /srv/archives
```

C'est l'état intermédiaire qu'il faut savoir reconnaître : **`lvs` dit 768 Mio,
`df` dit toujours 448 Mio**. Le contenant a grandi, le filesystem l'ignore. Les
256 Mio ajoutés existent bel et bien, mais aucun fichier ne pourra les occuper.
Un candidat qui s'arrête là a fait la moitié du travail et croit l'avoir
terminé.

Le second geste réveille le filesystem. Pour XFS, c'est `xfs_growfs` :

```bash
sudo xfs_growfs /srv/archives
df -h /srv/archives
```

```text
data blocks changed from 131072 to 196608
```

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  704M   90M  615M  13% /srv/archives
```

Cette fois `df` suit. Notez que `xfs_growfs` n'a **pas** de taille en argument :
il prend tout l'espace que le périphérique lui offre. On lui passe le **point de
montage**, et le filesystem doit être **monté** :

```bash
sudo xfs_growfs /dev/vgatelier/lvtest    # volume non monté
```

```text
xfs_growfs: /dev/vgatelier/lvtest is not a mounted XFS filesystem
```

Sur un volume monté, en revanche, `xfs_growfs` accepte aussi bien le point de
montage que le chemin du périphérique : les deux formes ont fonctionné ici avec
`xfsprogs-6.16.0`. Prenez malgré tout l'habitude du point de montage, la forme
que le manuel documente.

### `lvextend -r` : les deux gestes en une commande

L'option `-r` (`--resizefs`) enchaîne l'extension du volume **et** celle du
filesystem. C'est le réflexe à garder, précisément parce qu'elle rend l'oubli
impossible.

```bash
sudo lvextend -r -L +128M /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  Size of logical volume vgatelier/lvarchives changed from 768.00 MiB (192 extents) to 896.00 MiB (224 extents).
  Extending file system xfs to 896.00 MiB (939524096 bytes) on vgatelier/lvarchives...
xfs_growfs /dev/vgatelier/lvarchives
[...]
data blocks changed from 196608 to 229376
xfs_growfs done
  Extended file system xfs on vgatelier/lvarchives.
  Logical volume vgatelier/lvarchives successfully resized.
```

LVM ne cache rien : il identifie le filesystem, dit où il est monté, puis
**affiche la commande qu'il lance pour vous** (`xfs_growfs /dev/vgatelier/lvarchives`)
et son résultat. `df` confirme :

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  832M   93M  740M  12% /srv/archives
```

Deux notations de taille cohabitent, et la confusion est fréquente :

| Forme | Sens | Exemple |
|---|---|---|
| `-L 768M` | taille **absolue** visée | le volume fera 768 Mio |
| `-L +128M` | **ajout** à la taille actuelle | 128 Mio de plus qu'avant |
| `-l +100%FREE` | en **extents**, tout l'espace libre du VG | voir plus bas |

`-L` (majuscule) parle en unités humaines, `-l` (minuscule) parle en
**extents**, l'unité d'allocation du groupe de volumes.

### Ce que LVM refuse de faire

Trois refus valent mieux qu'un long discours, parce que ce sont eux que vous
lirez le jour où ça coince.

**Étendre au-delà de l'espace libre.** Le volume fait 896 Mio, le VG n'a plus
que 400 Mio libres, on en demande 4 Gio :

```bash
sudo lvextend -r -L 4G /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  Insufficient free space: 800 extents needed, but only 100 available
```

Le message compte en **extents**, pas en gigaoctets, ce qui déroute la première
fois. La conversion se lit dans les sorties précédentes : `512.00 MiB (128
extents)` donne 4 Mio par extent, la taille par défaut. Donc 800 extents = 3,1
Gio manquants, et 100 extents = 400 Mio disponibles, ce que `vgs` affichait
déjà en `VFree`. Rien n'a été modifié : la commande échoue avant d'agir.

**Réduire un XFS.** Le guide l'annonce, la machine le confirme :

```bash
sudo lvreduce -r -L 512M /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  File system size (896.00 MiB) is larger than the requested size (512.00 MiB).
  File system reduce is required and not supported (xfs).
```

`not supported (xfs)` n'est pas une limite de LVM, mais de XFS lui-même : ce
filesystem ne sait pas rétrécir, ni maintenant ni ailleurs. La seule voie est de
sauvegarder, recréer plus petit, restaurer. Corollaire pratique : **une
extension XFS est un aller sans retour**, donc on ne prend pas 100 % du VG sans
y avoir réfléchi.

Notez aussi que `lvreduce` sans `-r` accepterait, lui, de rogner le volume sous
son filesystem. C'est la meilleure façon de perdre des données : sur une
réduction, l'ordre est l'inverse de l'extension (filesystem d'abord, volume
ensuite), et c'est justement ce que `-r` sait faire correctement.

**Agrandir un XFS non monté.** L'opération n'est pas impossible, mais LVM
demande la permission de monter le volume au passage :

```bash
sudo lvextend -r -L +100M /dev/vgatelier/lvtest
```

```text
  File system xfs found on vgatelier/lvtest.
  File system mount is needed for extend.
Continue with xfs file system extend steps: mount, xfs_growfs? [y/n]:[n]
  File system not extended.
```

Répondre `n` (le défaut) annule **tout** : ni le volume ni le filesystem n'ont
bougé, `lvs` le confirme. Retenez surtout que la question existe : dans un
script non interactif, cette invite bloque ou échoue silencieusement.

### Quand le groupe de volumes est plein : `vgextend`

`Insufficient free space` ne veut pas dire « il faut acheter un plus gros
disque ». Le VG est un réservoir : on lui en ajoute un second.

```bash
sudo pvcreate /dev/vdb2
sudo vgextend vgatelier /dev/vdb2
sudo pvs
sudo vgs vgatelier
```

```text
  Physical volume "/dev/vdb2" successfully created.
  Volume group "vgatelier" successfully extended
```

```text
  PV         VG        Fmt  Attr PSize   PFree
  /dev/vdb1  vgatelier lvm2 a--   <1.27g 400.00m
  /dev/vdb2  vgatelier lvm2 a--  744.00m 744.00m

  VG        #PV #LV #SN Attr   VSize VFree
  vgatelier   2   1   0 wz--n- 1.99g <1.12g
```

Le VG compte maintenant 2 volumes physiques (`#PV`) et 1,12 Gio libres. C'est
ainsi qu'on dépasse la taille d'un seul disque, sans migration et sans coupure.

### `-r` choisit l'outil selon le filesystem

`-r` n'est pas un synonyme de `xfs_growfs` : LVM détecte le type de filesystem
et appelle l'outil correspondant. Créons un second volume, en **ext4** cette
fois :

```bash
sudo lvcreate -L 200M -n lvjournal vgatelier
sudo mkfs.ext4 -q /dev/vgatelier/lvjournal
sudo mkdir -p /srv/journal
sudo mount /dev/vgatelier/lvjournal /srv/journal
sudo lvextend -r -L +200M /dev/vgatelier/lvjournal
```

```text
  File system ext4 found on vgatelier/lvjournal mounted at /srv/journal.
  Size of logical volume vgatelier/lvjournal changed from 200.00 MiB (50 extents) to 400.00 MiB (100 extents).
  Extending file system ext4 to 400.00 MiB (419430400 bytes) on vgatelier/lvjournal...
resize2fs /dev/vgatelier/lvjournal
resize2fs 1.47.1 (20-May-2024)
Filesystem at /dev/vgatelier/lvjournal is mounted on /srv/journal; on-line resizing required
old_desc_blocks = 2, new_desc_blocks = 4
The filesystem on /dev/vgatelier/lvjournal is now 409600 (1k) blocks long.

resize2fs done
  Extended file system ext4 on vgatelier/lvjournal.
  Logical volume vgatelier/lvjournal successfully resized.
```

Comparez la première ligne avec celle du volume XFS : `File system ext4 found`
au lieu de `File system xfs found`, et `resize2fs` au lieu de `xfs_growfs`. La
commande tapée est rigoureusement la même. C'est tout l'intérêt de `-r` : elle
vous dispense de connaître l'outil du filesystem que vous avez en face.

Et ext4, contrairement à XFS, se **réduit** :

```bash
sudo lvreduce -r -L 250M /dev/vgatelier/lvjournal
```

```text
  Rounding size to boundary between physical extents: 252.00 MiB.
  File system ext4 found on vgatelier/lvjournal mounted at /srv/journal.
  File system size (400.00 MiB) is larger than the requested size (252.00 MiB).
  File system reduce is required using resize2fs.
  File system unmount is needed for reduce.
  File system fsck will be run before reduce.
  Reducing file system ext4 to 252.00 MiB (264241152 bytes) on vgatelier/lvjournal...
unmount /srv/journal
unmount done
e2fsck /dev/vgatelier/lvjournal
/dev/vgatelier/lvjournal: 11/102400 files (0.0% non-contiguous), 32142/409600 blocks
e2fsck done
resize2fs /dev/vgatelier/lvjournal 258048k
[...]
remount /dev/vgatelier/lvjournal /srv/journal
remount done
  Reduced file system ext4 on vgatelier/lvjournal.
  Size of logical volume vgatelier/lvjournal changed from 400.00 MiB (100 extents) to 252.00 MiB (63 extents).
```

Trois enseignements dans cette seule sortie. D'abord, `250M` est devenu
`252.00 MiB` : une taille est toujours arrondie au multiple d'extent supérieur
(4 Mio ici), et LVM le dit. Ensuite, la réduction n'est **pas** une opération en
ligne : LVM démonte, vérifie avec `e2fsck`, réduit, puis remonte. Enfin, l'ordre
est bien l'inverse de l'extension, le filesystem rétrécissant avant le volume.

### Tout prendre : `-l +100%FREE`

Quand on veut simplement que le volume avale tout ce qui reste, `-l +100%FREE`
évite de calculer :

```bash
sudo lvextend -r -l +100%FREE /dev/vgatelier/lvarchives
```

```text
  File system xfs found on vgatelier/lvarchives mounted at /srv/archives.
  Size of logical volume vgatelier/lvarchives changed from 896.00 MiB (224 extents) to <1.75 GiB (447 extents).
  Extending file system xfs to <1.75 GiB (1874853888 bytes) on vgatelier/lvarchives...
xfs_growfs /dev/vgatelier/lvarchives
data blocks changed from 229376 to 457728
xfs_growfs done
  Extended file system xfs on vgatelier/lvarchives.
  Logical volume vgatelier/lvarchives successfully resized.
```

```bash
sudo vgs -o vg_name,vg_extent_size,vg_extent_count,vg_free_count vgatelier
df -h /srv/archives
```

```text
  VG        Ext   #Ext Free
  vgatelier 4.00m  510    0
```

```text
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/vgatelier-lvarchives  1.7G  116M  1.6G   7% /srv/archives
```

`Free` tombe à zéro : il ne reste plus un extent. Cette sortie confirme au
passage la taille d'extent, 4 Mio, et le total de 510 extents pour les deux
volumes physiques.

Le `<` devant `1.75 GiB` signale un arrondi vers le bas à l'affichage : la
taille réelle est légèrement inférieure à 1,75 Gio. On le retrouve dans `pvs`
(`<1.27g`) et dans `vgs`.

Un dernier détail montre pourquoi LVM vaut mieux qu'une partition : le volume
s'étend désormais **sur les deux disques**, sans que rien ne le laisse
paraître côté filesystem.

```bash
sudo lvs -o lv_name,seg_pe_ranges vgatelier/lvarchives
```

```text
  LV         PE Ranges
  lvarchives /dev/vdb1:0-223
  lvarchives /dev/vdb1:287-323
  lvarchives /dev/vdb2:0-185
```

Trois segments, deux volumes physiques, un seul point de montage. Le trou entre
les extents 224 et 286 de `vdb1` correspond à l'emplacement occupé par l'autre
volume logique.

### Ce qui ne change pas quand le volume grandit

Point qui rassure au moment de vérifier la persistance : **l'UUID du filesystem
n'est pas modifié** par `lvextend` ni par `xfs_growfs`. Après les trois
extensions successives, `blkid` renvoie toujours la même valeur qu'au
formatage :

```text
2b81f1ac-3778-4231-abe1-6c853d55ee33
```

La ligne `/etc/fstab` écrite au départ reste donc valide, et les données écrites
avant les extensions sont toujours là. Autrement dit, agrandir un volume ne
demande **aucune** retouche de `fstab` : la persistance se règle une fois, à la
création.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `df` n'a pas bougé après `lvextend` | l'oubli classique : `-r` manquant, ou `xfs_growfs` / `resize2fs` non lancé |
| `Insufficient free space: N extents needed, but only M available` | le VG est plein : `vgs` pour lire `VFree`, puis `vgextend` avec un nouveau PV |
| `File system reduce is required and not supported (xfs)` | XFS ne se réduit pas : sauvegarder, recréer, restaurer |
| `xfs_growfs: … is not a mounted XFS filesystem` | XFS s'agrandit en ligne uniquement, montez d'abord |
| `Continue with xfs file system extend steps: mount, xfs_growfs? [y/n]` | `lvextend -r` sur un volume non monté ; en script, monter avant |
| `mount: … can't find UUID=…` au `mount -a` | UUID erroné dans `/etc/fstab` ; le relire avec `blkid` |
| `[W] your fstab has been modified, but systemd still uses the old version` | `sudo systemctl daemon-reload` après édition de `/etc/fstab` |
| `Rounding size to boundary between physical extents` | la taille demandée n'est pas un multiple de la taille d'extent ; simple information |
| `lvs` introuvable, `command not found` | paquet `lvm2` absent (`sudo dnf install lvm2`) |

Pour tout défaire et repartir de zéro, on démonte puis on retire dans l'ordre
inverse de la création : LV, VG, PV.

```bash
sudo umount /srv/archives /srv/journal
# retirer la ligne ajoutée dans /etc/fstab, puis :
sudo systemctl daemon-reload
sudo lvremove -y vgatelier/lvarchives vgatelier/lvjournal
sudo vgremove vgatelier
sudo pvremove /dev/vdb1 /dev/vdb2
sudo wipefs -a /dev/vdb
sudo rmdir /srv/archives /srv/journal
```

Deux gestes qu'on oublie dans ce ménage : retirer la ligne de `/etc/fstab` (la
laisser, c'est se garantir une erreur au prochain démarrage) et relancer
`systemctl daemon-reload` pour que systemd oublie l'unité de montage
correspondante.
