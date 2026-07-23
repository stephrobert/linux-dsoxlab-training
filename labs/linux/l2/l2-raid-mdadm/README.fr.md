# Lab — Construire un RAID 1 logiciel avec mdadm

## Rappel

[**Le RAID logiciel avec mdadm**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/)

Le RAID 1 duplique les données sur plusieurs disques : l'array survit à la perte
d'un disque. Un spare peut reconstruire automatiquement. L'array doit être
déclaré dans `mdadm.conf` (et l'initramfs) pour se réassembler au démarrage.

## Le cours

Les exemples ci-dessous construisent un miroir nommé `/dev/md10` sur les
partitions d'un disque de démonstration, monté sur `/srv/miroir-demo` : le
challenge, lui, vous demandera un autre array, sur d'autres périphériques et un
autre point de montage. Le but est d'apprendre la méthode, pas de recopier une
ligne. Toutes les sorties ci-dessous ont été produites sur une VM AlmaLinux 10.2
(`mdadm` 4.4).

### Où en est la machine

Trois questions avant de commencer : l'outil est-il là, un array existe-t-il
déjà, et quels disques sont libres.

```bash
rpm -q mdadm            # sur AlmaLinux 10, le paquet n'est pas installé par défaut
cat /proc/mdstat        # la liste des arrays du noyau
lsblk                   # quels disques ne portent aucun point de montage
```

```text
package mdadm is not installed

Personalities :
unused devices: <none>

vdb    252:16   0    2G  0 disk
```

`Personalities :` vide et `unused devices: <none>` signifient qu'aucun array
n'est assemblé, et que le noyau n'a même pas encore chargé de module RAID.
Installez l'outil avec `sudo dnf install -y mdadm` : le paquet active au passage
le service de surveillance `mdmonitor`.

> **Ne travaillez jamais à l'aveugle sur un disque.** Vérifiez avec `lsblk` que
> celui que vous visez ne porte aucun point de montage. Ici, `/dev/vda` est le
> disque système (il porte `/`, `/boot` et `/boot/efi`) : on n'y touche pas.

### Préparer les périphériques

Un array RAID a besoin d'au moins **deux périphériques de même taille**, disques
entiers ou partitions. Le disque de démonstration est découpé en quatre
partitions de 500 Mio : deux pour le miroir, une de secours (*spare*), une pour
jouer le disque de remplacement.

```bash
sudo parted -s /dev/vdb mklabel gpt
sudo parted -s /dev/vdb mkpart mir1 1MiB 500MiB
sudo parted -s /dev/vdb set 1 raid on
# … idem pour mir2 (501-1000), mir3 (1001-1500), mir4 (1501-2000)
sudo partprobe /dev/vdb
```

```text
Number  Start   End     Size   File system  Name  Flags
 1      1049kB  524MB   523MB               mir1  raid
 2      525MB   1049MB  523MB               mir2  raid
 3      1050MB  1573MB  523MB               mir3  raid
 4      1574MB  2097MB  523MB               mir4  raid
```

Le drapeau `raid` est une étiquette de table de partitions : il documente
l'usage et évite qu'un autre outil s'approprie la partition. Il ne crée aucun
array à lui seul.

### Créer le miroir et suivre la synchronisation

Le *spare* est un périphérique inactif qui prend le relais **automatiquement** à
la première panne : c'est ce qui transforme la redondance en résilience sans
intervention.

```bash
sudo mdadm --create /dev/md10 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdb2 \
  --spare-devices=1 /dev/vdb3
```

Sur AlmaLinux 10, `mdadm` 4.4 pose **deux questions** avant de créer :

```text
To optimalize recovery speed, it is recommended to enable write-indent bitmap,
do you want to enable it now? [y/N]?
mdadm: Note: this array has metadata at the start and
    may not be suitable as a boot device.  …
Continue creating array [y/N]? mdadm: Defaulting to version 1.2 metadata
mdadm: array /dev/md10 started.
```

Répondre `y` aux deux convient. Si vous scriptez, `--bitmap=internal` supprime la
première question et `--run` la seconde :

```bash
sudo mdadm --create /dev/md10 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdb2 \
  --spare-devices=1 /dev/vdb3 --bitmap=internal --run
```

La synchronisation initiale se suit dans `/proc/mdstat` :

```text
md10 : active raid1 vdb3[2](S) vdb2[1] vdb1[0]
      509952 blocks super 1.2 [2/2] [UU]
      [===============>.....]  resync = 78.5% (401280/509952) finish=0.0min speed=200640K/sec
      bitmap: 1/1 pages [4KB], 65536KB chunk
```

Trois choses à lire sur ces lignes :

- **`(S)`** marque le spare : `vdb3` est là, mais ne porte pas de données.
- **`[2/2] [UU]`** donne l'état des disques actifs, `U` pour up, `_` pour absent.
- La ligne `resync` n'est pas une panne : c'est la première recopie, l'array est
  déjà utilisable pendant ce temps.

`mdadm --detail` donne la vue complète, celle qui compte pour un contrôle :

```text
        Raid Level : raid1
      Raid Devices : 2
             State : clean
    Active Devices : 2
   Working Devices : 3
    Failed Devices : 0
     Spare Devices : 1
[...]
       0     252       17        0      active sync   /dev/vdb1
       1     252       18        1      active sync   /dev/vdb2
       2     252       19        -      spare   /dev/vdb3
```

`Working Devices : 3` pour `Raid Devices : 2` : les deux membres actifs plus le
spare.

### Formater et monter

Un array `mdadm` se comporte comme un disque ordinaire : il se formate et se
monte de la même façon.

```bash
sudo mkfs.xfs /dev/md10
sudo mkdir -p /srv/miroir-demo
sudo mount /dev/md10 /srv/miroir-demo
findmnt -n /srv/miroir-demo
```

```text
/srv/miroir-demo /dev/md10 xfs rw,relatime,seclabel,attr2,inode64,…
```

Pour un montage persistant, on passe par l'**UUID du système de fichiers**, pas
par `/dev/md10` : le nom du périphérique peut changer (la section suivante
montre pourquoi), l'UUID non.

```bash
sudo blkid /dev/md10
```

```text
/dev/md10: UUID="25cb208f-60cd-4d59-8ad0-6fa3e7756e11" BLOCK_SIZE="512" TYPE="xfs"
```

```text title="/etc/fstab"
UUID=25cb208f-60cd-4d59-8ad0-6fa3e7756e11 /srv/miroir-demo xfs defaults,nofail 0 0
```

L'option **`nofail`** évite qu'un array dégradé bloque le démarrage. Testez la
ligne sans redémarrer, avec `sudo mount -a` : si la commande passe sans erreur,
la syntaxe est bonne.

### Rendre l'array persistant : le piège qui coûte des points

Un array créé en mémoire n'est **pas réassemblé à l'identique** après un
redémarrage tant qu'il n'est pas déclaré dans la configuration et inclus dans
l'**initramfs**. Sur RHEL et AlmaLinux, `/etc/mdadm.conf` n'existe **pas par
défaut** : il faut le créer.

```bash
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf
sudo dracut --force
```

```text
ARRAY /dev/md10 metadata=1.2 spares=1 UUID=b80196f2:943633e5:33dc2b1f:19baf30b
```

La ligne identifie l'array par **UUID**, donc indépendamment de l'ordre des
disques. Sur Debian et Ubuntu, le fichier est `/etc/mdadm/mdadm.conf` et
l'initramfs se régénère avec `sudo update-initramfs -u`.

Pourquoi le `dracut` compte : avant, l'initramfs ne contenait **rien** de
`mdadm` ; après, il embarque le module `mdraid` et le binaire.

```bash
sudo lsinitrd /boot/initramfs-$(uname -r).img | grep -c mdadm    # 0 avant, non nul après
```

Le nom que reprend l'array dépend, lui, de `/etc/mdadm.conf`. La démonstration
suivante l'établit sans redémarrer, en arrêtant l'array puis en forçant une
nouvelle détection des disques :

```bash
sudo umount /srv/miroir-demo && sudo mdadm --stop /dev/md10
sudo mv /etc/mdadm.conf /root/mdadm.conf.save        # on écarte la conf
sudo udevadm trigger --subsystem-match=block --action=add && sudo udevadm settle
cat /proc/mdstat
```

```text
md127 : active (auto-read-only) raid1 vdb3[2] vdb4[3](S) vdb2[1]
      509952 blocks super 1.2 [2/2] [UU]
```

L'array est revenu, mais sous le nom **`/dev/md127`**. Rien n'est perdu, sauf que
toute ligne de `/etc/fstab` ou tout script qui parlait de `/dev/md10` vise
désormais un périphérique inexistant. Remettez la configuration en place et
refaites le même test :

```bash
sudo mdadm --stop /dev/md127 && sudo cp /root/mdadm.conf.save /etc/mdadm.conf
sudo udevadm trigger --subsystem-match=block --action=add && sudo udevadm settle
cat /proc/mdstat
```

```text
md10 : active raid1 vdb3[2] vdb4[3](S) vdb2[1]
      509952 blocks super 1.2 [2/2] [UU]
```

> **Ce qui n'est pas prouvé ici : le comportement au démarrage.** La machine
> n'a pas été redémarrée ; ce qui précède est un réassemblage à chaud. La règle
> du guide reste entière : `mdadm.conf` **plus** initramfs régénéré, sinon
> l'array peut ne pas remonter comme prévu.

### Simuler une panne et reconstruire

Le geste attendu en examen tient en trois mots : **marquer**, **retirer**,
**ajouter**. On simule la panne avec `--fail`.

```bash
sudo mdadm /dev/md10 --fail /dev/vdb1
cat /proc/mdstat
```

```text
md10 : active raid1 vdb3[2] vdb2[1] vdb1[0](F)
      509952 blocks super 1.2 [2/1] [_U]
      [>....................]  recovery =  0.8% (4096/509952) finish=2.0min speed=4096K/sec
```

`(F)` marque le disque en panne, `[2/1] [_U]` dit qu'il ne reste qu'un membre
actif sur deux, et la ligne `recovery` montre le spare en train de reconstruire.
`mdadm --detail` le dit en toutes lettres :

```text
             State : clean, degraded, recovering
    Active Devices : 1
    Failed Devices : 1
    Rebuild Status : 14% complete
[...]
       2     252       19        0      spare rebuilding   /dev/vdb3
```

Pendant toute la reconstruction, le système de fichiers reste monté et lisible :
c'est tout l'intérêt du miroir. Une fois terminé, l'array repasse en `[UU]`, le
spare étant devenu membre actif et `vdb1` restant listé comme `faulty`.

Retirez alors le disque défaillant, puis ajoutez son remplaçant, qui devient le
nouveau spare :

```bash
sudo mdadm /dev/md10 --remove /dev/vdb1
sudo mdadm /dev/md10 --add /dev/vdb4
cat /proc/mdstat
```

```text
mdadm: hot removed /dev/vdb1 from /dev/md10
mdadm: added /dev/vdb4
md10 : active raid1 vdb4[3](S) vdb3[2] vdb2[1]
      509952 blocks super 1.2 [2/2] [UU]
```

> **Sur un petit array, tout va trop vite pour être observé.** Ces 500 Mio se
> reconstruisent en quelques secondes. Suivez avec `watch -n1 cat /proc/mdstat`,
> ou bridez volontairement le débit le temps de regarder :
> `echo 2000 | sudo tee /proc/sys/dev/raid/speed_limit_max` (valeur par défaut
> `200000`, à remettre après).

Un RAID sans surveillance n'est pas résilient : une panne qui passe inaperçue
finit en perte totale au second disque. Le service `mdmonitor` est `enabled` dès
l'installation du paquet ; déclarez l'adresse de notification en tête de
`mdadm.conf` avec une ligne `MAILADDR root@localhost`. Pour un script,
`mdadm --detail --test /dev/md10` renvoie 0 quand l'array est sain.

### Démonter proprement, et dépanner

Un array qu'on abandonne sans le démonter laisse un **superbloc RAID** sur
chaque membre, qui le fera réapparaître plus tard. Le nettoyage complet, dans
l'ordre :

```bash
sudo umount /srv/miroir-demo
sudo mdadm --stop /dev/md10
sudo mdadm --zero-superblock /dev/vdb2 /dev/vdb3 /dev/vdb4
sudo wipefs -a /dev/vdb1 /dev/vdb2 /dev/vdb3 /dev/vdb4
cat /proc/mdstat        # doit revenir à "unused devices: <none>"
```

Sans le `--zero-superblock`, la trace reste visible et bloque la réutilisation :

```text
$ sudo mdadm --examine /dev/vdb1
     Array UUID : b80196f2:943633e5:33dc2b1f:19baf30b
     Raid Level : raid1

$ sudo mdadm --create /dev/md20 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdb2
mdadm: /dev/vdb1 appears to be part of a raid array:
       level=raid1 devices=2 ctime=Wed Jul 22 14:57:18 2026
```

N'oubliez pas de retirer la ligne `ARRAY` de `/etc/mdadm.conf` et de relancer
`sudo dracut --force` : une configuration qui décrit un array disparu est un
piège pour le prochain démarrage.

| Symptôme | Cause probable | Solution |
|---|---|---|
| `mdadm --create` reste bloqué sur `Continue creating array [y/N]?` | la commande attend une confirmation | répondre `y`, ou ajouter `--run` (et `--bitmap=internal` pour la première question) |
| `mkfs.xfs: appears to contain an existing filesystem` | signature laissée par un usage précédent du disque | `sudo wipefs -a /dev/mdX` avant le `mkfs` |
| L'array revient sous `/dev/md127` | aucune ligne `ARRAY` dans `/etc/mdadm.conf` | `mdadm --detail --scan >> /etc/mdadm.conf` puis `dracut --force` |
| `/proc/mdstat` affiche `[_U]` | un membre en panne, reconstruction en cours ou impossible | `mdadm --detail` puis `--remove` et `--add` |
| `appears to be part of a raid array` | superbloc RAID résiduel | `sudo mdadm --zero-superblock /dev/vdbX` |
| Array absent ou renommé après un reboot | `mdadm.conf` ou initramfs pas à jour | régénérer la conf, puis `dracut --force` (ou `update-initramfs -u`) |
