# Lab — récupérer un filesystem en lecture seule

## Rappel

[**Récupération filesystem en lecture seule sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/)

`findmnt <mnt>` montre les options actives d'un montage (`ro` vs `rw`).
`mount -o remount,rw <mnt>` le bascule sans démonter. Une mauvaise option dans
`/etc/fstab` fait échouer `mount -a` — et un vrai boot tomberait en mode urgence —
donc teste toujours fstab avec `mount -a` après l'avoir édité.

## Le cours

Les exemples ci-dessous travaillent sur un disque de brouillon, `/dev/vdb`,
découpé en deux : `/dev/vdb1` en ext4 monté sur `/mnt/depot`, `/dev/vdb2` en xfs
monté sur `/mnt/archive`. Le challenge, lui, vous posera un autre montage,
ailleurs, avec une autre panne. Le but est d'apprendre la méthode.

> **Ne reproduisez jamais ces manipulations sur `/`.** Un système de fichiers de
> brouillon se casse et se répare sans conséquence ; la racine, non. Vérifiez par
> `lsblk` sur quel périphérique vous êtes avant chaque commande destructrice.

### Constater : le message, les options, le journal

Trois sources, et elles ne disent pas la même chose. Commencez par le message
que reçoit l'application :

```bash
sudo touch /mnt/depot/essai
```

```text
touch: cannot touch '/mnt/depot/essai': Read-only file system
```

Puis les options réellement actives du montage :

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS /mnt/depot
```

```text
TARGET     SOURCE    FSTYPE OPTIONS
/mnt/depot /dev/vdb1 ext4   ro,relatime,seclabel
```

Pour balayer toute la machine d'un coup, `findmnt -O ro -o TARGET,SOURCE,FSTYPE`
liste les montages portant l'option `ro` (les `tmpfs` de `/run/credentials`
apparaissent toujours, ce sont des montages en lecture seule voulus).

> **Attention au `grep` sur la sortie de `mount`.** Le motif souvent cité,
> `mount | grep ' ro,'`, ne remonte rien : `mount` écrit les options entre
> parenthèses, donc la ligne est `/dev/vdb1 on /mnt/depot type ext4 (ro,relatime,seclabel)`.
> Il faut `mount | grep '(ro,'`, ou mieux `findmnt -O ro`, qui interroge la
> table de montage plutôt que du texte.

Enfin, le journal du noyau, le seul à dire **pourquoi** :

```bash
sudo dmesg | grep -iE 'EXT4-fs|XFS|read-only'
```

```text
[ 2604.689943] EXT4-fs (vdb1): mounted filesystem 5a73ff73-[...] r/w with ordered data mode.
[ 2619.711686] EXT4-fs (vdb1): re-mounted 5a73ff73-[...] ro.
```

Lisez bien cette dernière ligne : `re-mounted ... ro.` est une trace d'action
administrateur, pas d'erreur. Le noyau dit qu'on lui a demandé un remontage en
lecture seule. Retenez cette formulation, elle contraste avec la suivante.

### Voulu ou subi : deux pannes qui n'ont pas la même réparation

Le message d'erreur désigne la cause, et c'est le cœur du diagnostic :

| Message obtenu | Code | Ce que ça veut dire |
|---|---|---|
| `Read-only file system` | `EROFS` | Le montage est en lecture seule **volontairement** |
| `Input/output error` | `EIO` | Le **périphérique a lâché**, le système de fichiers s'est protégé |

Pour voir le second cas sans casser de vrai disque, on intercale une couche
device-mapper entre le système de fichiers et la partition, puis on remplace sa
table par la cible `error`, qui fait échouer toute entrée-sortie :

```bash
sudo dmsetup suspend --nolockfs --noflush depot_fragile
echo "0 2097152 error" | sudo dmsetup reload depot_fragile
sudo dmsetup resume depot_fragile
sudo touch /mnt/depot/apres-panne
```

```text
touch: cannot touch '/mnt/depot/apres-panne': Input/output error
```

Et le journal, quelques secondes plus tard :

```text
Buffer I/O error on dev dm-0, logical block 0, lost sync page write
EXT4-fs (dm-0): I/O error while writing superblock
Aborting journal on device dm-0-8.
EXT4-fs error (device dm-0) in __ext4_new_inode:1093: IO failure
EXT4-fs (dm-0): Remounting filesystem read-only
```

Cinq lignes, tout le diagnostic : erreur d'écriture, superbloc impossible à
mettre à jour, journal avorté, remontage en lecture seule décidé par le noyau.
Rien à voir avec le `re-mounted ... ro.` de la section précédente.

Une écriture juste après renvoie `Read-only file system` et non plus
`Input/output error` : une fois la bascule faite, le système de fichiers refuse
proprement au lieu d'échouer sur le disque.

### ext4 : la protection `errors=remount-ro` n'est pas toujours active

C'est l'option `errors=` qui décide de ce que fait ext4 face à une incohérence :
continuer, remonter en lecture seule, ou paniquer. Sa valeur par défaut est
inscrite **dans le superbloc** :

```bash
sudo tune2fs -l /dev/vdb1 | grep -iE 'errors behavior|filesystem state'
```

```text
Filesystem state:         clean
Errors behavior:          Continue
```

**`Continue` sur un système de fichiers fraîchement créé par `mkfs.ext4`** : la
protection n'est donc pas là par défaut sur AlmaLinux 10, contrairement à ce
qu'on lit souvent. On la pose sur le superbloc, une fois pour toutes :

```bash
sudo tune2fs -e remount-ro /dev/vdb1
sudo tune2fs -l /dev/vdb1 | grep -i 'errors behavior'
```

```text
Setting error behavior to 2
Errors behavior:          Remount read-only
```

On peut aussi la donner au montage ou dans `/etc/fstab` (`errors=remount-ro`).
Détail utile : `findmnt` n'affiche l'option que lorsqu'elle **diffère** du
superbloc. Monté avec `errors=continue` alors que le superbloc dit
`remount-ro`, on lit `rw,relatime,seclabel,errors=continue` ; sinon, rien.

### xfs ne se comporte pas comme ext4

Sur RHEL et ses dérivés, la racine est en xfs par défaut. Or **rien de ce qui
précède ne s'y applique**. D'abord l'option n'existe pas :

```bash
sudo mount -o remount,errors=remount-ro /mnt/archive
```

```text
mount: /mnt/archive: fsconfig system call failed: xfs: Unknown parameter 'errors'.
```

Ensuite les outils diffèrent. `tune2fs` est un outil ext, il refuse le
périphérique (`Bad magic number in super-block`). Et `fsck` sur du xfs ne
vérifie rien :

```bash
sudo fsck -n /dev/vda4        # la racine, en xfs
```

```text
fsck from util-linux 2.40.2
If you wish to check the consistency of an XFS filesystem or
repair a damaged filesystem, see xfs_repair(8).
```

Enfin, la panne ne se manifeste pas de la même façon. Avec la même cible
`error` sous le montage xfs :

```text
XFS (dm-1): log I/O error -5
XFS (dm-1): Filesystem has been shut down due to log error (0x2).
XFS (dm-1): Please unmount the filesystem and rectify the problem(s).
```

xfs ne remonte pas en lecture seule : il **s'arrête**. Et `findmnt -no OPTIONS
/mnt/archive` continue d'afficher `rw,relatime,seclabel,attr2,...` sans le
moindre indice, alors que lecture comme écriture renvoient
`Input/output error`. Sur ext4, le noyau ajoute au moins un marqueur
`emergency_ro` dans les options ; sur xfs, la table de montage ne dit rien.

### Réparer : démonter, vérifier, remonter

On ne répare **jamais** un système de fichiers monté. Ce n'est pas une
précaution de style, les outils le refusent :

```bash
sudo e2fsck -f /dev/vdb1      # partition montée
```

```text
e2fsck 1.47.1 (20-May-2024)
/dev/vdb1 is mounted.
e2fsck: Cannot continue, aborting.
```

```bash
sudo xfs_repair -n /dev/vdb2  # partition montée
```

```text
xfs_repair: /dev/vdb2 contains a mounted and writable filesystem
fatal error -- couldn't initialize XFS library
```

`e2fsck -n` accepte lui de tourner sur un montage actif, mais il prévient que
son verdict ne vaut rien : `Warning! /dev/vdb1 is mounted.` puis
`Warning: skipping journal recovery because doing a read-only filesystem check.`
Un journal non rejoué, c'est une image du disque qui n'est pas l'état réel.

Donc : démonter d'abord. Si `umount` répond `target is busy`, cherchez qui
tient le montage avec `lsof +f -- /mnt/depot`, arrêtez le processus, et ne
gardez `umount -l` que pour le dernier recours. Sur la racine, le démontage est
impossible : il faut redémarrer sur un système de secours.

Vérification hors ligne, puis réparation :

```bash
sudo e2fsck -n -f /dev/vdb1 ; echo "exit=$?"
```

```text
Pass 5: Checking group summary information
Inode bitmap differences:  +12
Fix? no
[...]
depot: ********** WARNING: Filesystem still has errors **********
exit=4
```

```bash
sudo e2fsck -f -y /dev/vdb1 ; echo "exit=$?"
```

```text
Inode bitmap differences:  +12
Fix? yes
depot: ***** FILE SYSTEM WAS MODIFIED *****
exit=1
```

`-f` force la vérification même si le système de fichiers se croit propre, `-y`
répond oui à tout, `-n` répond non à tout et n'écrit rien. Les codes de sortie
comptent : **0** rien à corriger, **1** des erreurs ont été **corrigées** (c'est
un succès), **4 et plus** des erreurs **non corrigées**, et c'est là qu'il faut
s'inquiéter.

Côté xfs, `xfs_repair -n` fait le même travail de constat, et `xfs_repair` sans
option répare. Un cas particulier à connaître, décrit dans `man 8 xfs_repair` :
si le journal est sale, `xfs_repair` **sort en code 2 et ne fait rien**, parce
que seul le noyau sait rejouer un journal xfs. Le manuel donne la marche à
suivre : monter puis démonter aussitôt le système de fichiers pour laisser le
noyau rejouer, et ne recourir à `xfs_repair -L`, qui efface le journal, qu'en
dernier ressort, en acceptant de perdre les métadonnées en cours d'écriture.

### Le piège : un remontage réussi n'est pas une réparation

C'est ce qui coûte le lab, et l'examen. Sur le montage xfs arrêté par le noyau :

```bash
sudo mount -o remount,rw /mnt/archive ; echo "exit=$?"
sudo touch /mnt/archive/preuve
```

```text
exit=0
touch: cannot touch '/mnt/archive/preuve': Input/output error
```

**Le remontage a réussi. Rien n'est réparé.** Et même après avoir rendu le
périphérique parfaitement sain, l'écriture échoue toujours : le système de
fichiers reste arrêté jusqu'au démontage.

Sur ext4 dans le même état, le remontage ne réussit même pas :

```text
mount: /mnt/depot: fsconfig system call failed: ext4: Unknown parameter 'emergency_ro'.
```

Deux leçons. La première : ne concluez jamais sur le code de retour d'un
`mount -o remount,rw`. La seule preuve que l'écriture est revenue, c'est
**d'écrire réellement un fichier**. La seconde : la seule preuve que le système
de fichiers est sain, c'est une vérification hors ligne, `e2fsck -n -f` ou
`xfs_repair -n`, qui ne modifie rien et vous donne un code de sortie.

Et cherchez la cause. Un montage qui repart en lecture seule après remontage a
un vrai problème : relisez `dmesg` pour les lignes `Buffer I/O error on dev`,
qui pointent le périphérique fautif. Sur du matériel physique, `smartctl -H
/dev/sdX` donne l'état de santé du disque ; sur une VM, ne comptez pas dessus,
`smartctl -H /dev/vdb` répond `Unable to detect device type` sur un disque
virtio.

### Ne jamais bloquer le démarrage : `nofail`, `mount -a`, `findmnt --verify`

Une entrée fautive dans `/etc/fstab` ne se voit pas tout de suite : elle se voit
au redémarrage, quand la machine tombe en mode urgence. Deux garde-fous.

`findmnt --verify` relit `/etc/fstab` et signale ce qui ne passera pas :

```bash
sudo findmnt --verify
```

```text
/mnt/depot
   [E] unreachable on boot required source: UUID=00000000-1111-2222-3333-444444444444
0 parse errors, 1 error, 1 warning
```

`mount -a` monte tout ce que déclare `fstab` et échoue si une entrée échoue :

```text
mount: /mnt/depot: can't find UUID=00000000-1111-2222-3333-444444444444.
exit=32
```

L'option `nofail` dit au système de continuer si le périphérique est absent.
Avec elle, sur la **même** entrée cassée, `mount -a` renvoie 0 :

```text
exit=0
```

Attention à ce que cela veut dire : `nofail` ne corrige rien, il empêche
seulement le démarrage de se bloquer. `findmnt --verify` continue d'afficher
`[E] unreachable on boot required source`. Les deux commandes sont
complémentaires, l'une teste le montage, l'autre relit la déclaration.

La séquence sûre, quand on touche à `fstab` : sauvegarder le fichier
(`cp -a /etc/fstab /root/fstab.bak`), ajouter `nofail` sur toute entrée dont on
n'est pas certain, puis vérifier avec `sudo findmnt --verify` **et**
`sudo mount -a` avant tout redémarrage.

> **Après édition de `fstab`, `findmnt --verify` rappelle de lancer
> `systemctl daemon-reload`** : systemd génère des unités de montage à partir de
> ce fichier et travaille encore sur l'ancienne version tant qu'on ne l'a pas
> rechargé.
