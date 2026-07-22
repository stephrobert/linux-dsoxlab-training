# Lab — récupérer un filesystem plein

## Rappel

[**Espace disque sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/)

`df -h` liste les filesystems et leur occupation ; `du -h --max-depth=1 <dir>`
montre ce que pèse chaque sous-répertoire, pour descendre jusqu'au coupable. Si
`df` dit plein mais `du` n'est pas d'accord, `lsof +L1` trouve un fichier
supprimé mais encore ouvert, tenu par un processus.

## Le cours

Les exemples ci-dessous travaillent sur `/mnt/space-demo`, un petit conteneur de
démonstration monté en loopback : le challenge, lui, portera sur un autre point
de montage, d'autres fichiers et d'autres seuils. Le but est d'apprendre la
méthode, pas de recopier une ligne. Toutes les sorties affichées ont été
capturées sur la VM du lab (AlmaLinux 10).

### Le décor de démonstration

Saturer un vrai filesystem est risqué. On s'en fabrique donc un jetable de
64 Mio, dans un simple fichier attaché à un périphérique loop :

```bash
sudo dd if=/dev/zero of=/root/space-demo.img bs=1M count=64 status=none
sudo losetup --find --show /root/space-demo.img    # affiche le loop attribué
sudo mkfs.ext4 -q -F -L space-demo /dev/loop1
sudo mkdir -p /mnt/space-demo
sudo mount /dev/loop1 /mnt/space-demo
```

`losetup --find --show` choisit le premier `/dev/loopN` libre et l'affiche :
reprenez **la valeur qu'il vous rend**, elle n'est pas forcément `loop1`.

> **Pourquoi ext4 et pas XFS ici.** Sur cette VM, `mkfs.xfs` refuse un conteneur
> de cette taille : `Filesystem must be larger than 300MB.` XFS impose un
> plancher que 64 Mio ne franchissent pas. Les commandes de diagnostic qui
> suivent (`df`, `du`, `lsof`) sont identiques quel que soit le système de
> fichiers ; seules les commandes d'agrandissement diffèrent.

On y pose de quoi travailler : trois petits rapports, une archive, et un gros
journal applicatif.

```bash
sudo mkdir -p /mnt/space-demo/{rapports,exports/2026-07,archives}
for i in 1 2 3; do
  sudo dd if=/dev/zero of=/mnt/space-demo/rapports/rapport-$i.pdf bs=1M count=1 status=none
done
sudo dd if=/dev/zero of=/mnt/space-demo/archives/2026-06.tar bs=1M count=8 status=none
sudo dd if=/dev/zero of=/mnt/space-demo/exports/2026-07/extraction.log bs=1M count=30 status=none
sudo sync
```

### Voir l'occupation avec df

`df` (*disk free*) résume l'occupation de chaque filesystem monté. `-h` rend les
tailles lisibles, `-T` ajoute le type, et exclure `tmpfs` et `devtmpfs` retire le
bruit des filesystems virtuels :

```bash
df -hT -x tmpfs -x devtmpfs
```

```text
Filesystem     Type      Size  Used Avail Use% Mounted on
/dev/vda4      xfs        19G  1.9G   17G  10% /
efivarfs       efivarfs  256K   17K  235K   7% /sys/firmware/efi/efivars
/dev/vda3      xfs       960M  237M  724M  25% /boot
/dev/vda2      vfat      200M  9.1M  191M   5% /boot/efi
/dev/loop1     ext4       55M   42M  9.3M  82% /mnt/space-demo
```

La colonne **`Use%`** repère d'un coup d'oeil le volume proche de la saturation.
C'est la première commande à lancer quand une alerte « disque plein » tombe. Ici
`/mnt/space-demo` est à 82 %, tout le reste est tranquille.

Notez déjà deux chiffres qui ne tombent pas juste : le conteneur fait 64 Mio mais
`Size` annonce 55M, et `Used` + `Avail` (42 + 9,3 = 51,3M) ne redonne pas `Size`.
Rien d'anormal : la différence part dans les métadonnées du filesystem d'un côté,
et dans une **réserve** de l'autre. Nous y revenons plus bas, parce que cette
réserve explique des « No space left on device » déroutants.

### Le disque « plein » qui a pourtant de la place : les inodes

Un filesystem peut afficher de l'espace libre et refuser malgré tout d'écrire :
il a épuisé ses **inodes**, les structures qui décrivent chaque fichier. Sur
ext4, leur nombre est **fixé à la création** et ne bouge plus. Des millions de
petits fichiers (sessions applicatives, caches, mails) peuvent les saturer bien
avant l'espace.

Fabriquons le cas, avec un second conteneur volontairement pauvre en inodes
(`-N 512`) :

```bash
sudo dd if=/dev/zero of=/root/space-demo-inodes.img bs=1M count=64 status=none
sudo losetup --find --show /root/space-demo-inodes.img
sudo mkfs.ext4 -q -F -N 512 -L space-demo-i /dev/loop2
sudo mkdir -p /mnt/space-demo-inodes
sudo mount /dev/loop2 /mnt/space-demo-inodes
df -i /mnt/space-demo-inodes
```

```text
Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/loop2        512    11   501    3% /mnt/space-demo-inodes
```

On crée ensuite des fichiers minuscules, un octet chacun, jusqu'au refus :

```bash
sudo sh -c 'mkdir -p /mnt/space-demo-inodes/sessions
            for i in $(seq 1 2000); do echo x > /mnt/space-demo-inodes/sessions/sess-$i; done'
```

```text
sh: line 1: /mnt/space-demo-inodes/sessions/sess-501: No space left on device
```

Le message accuse le manque de place. `df -h` le dément :

```bash
df -h /mnt/space-demo-inodes
df -i /mnt/space-demo-inodes
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop2       59M  526K   54M   1% /mnt/space-demo-inodes

Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/loop2        512   512     0  100% /mnt/space-demo-inodes
```

**1 % d'espace occupé, 100 % d'inodes.** Voilà le réflexe à acquérir : devant un
« No space left on device » que `df -h` ne confirme pas, lancez `df -i`. La
sortie n'a plus rien d'ambigu, et le remède est de supprimer les petits fichiers
en cause, ou de recréer le filesystem avec davantage d'inodes.

Deux précisions utiles, vérifiées sur cette VM :

```bash
df -i /            # racine en XFS
df -i /boot/efi    # partition EFI en vfat
```

```text
Filesystem      Inodes IUsed   IFree IUse% Mounted on
/dev/vda4      9858032 34497 9823535    1% /

Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/vda2           0     0     0     - /boot/efi
```

La racine est en **XFS**, qui alloue ses inodes dynamiquement : la pénurie y est
bien plus improbable que sur ext4. Et `vfat` n'a pas de notion d'inode du tout,
d'où les zéros et le tiret dans `IUse%` : sur ce type de filesystem, `df -i` ne
vous apprendra rien.

### Localiser ce qui occupe la place avec du

`df` dit **combien**, `du` (*disk usage*) dit **où**. La forme à retenir liste un
seul niveau et trie du plus petit au plus gros :

```bash
sudo du -h --max-depth=1 /usr | sort -h
```

```text
0	/usr/games
0	/usr/src
4.0K	/usr/local
56K	/usr/include
7.0M	/usr/libexec
38M	/usr/sbin
62M	/usr/bin
171M	/usr/share
181M	/usr/lib64
312M	/usr/lib
769M	/usr
```

`sort -h` (*human-numeric*) comprend les suffixes `K`, `M` et `G` et place les
plus gros en bas, donc juste au-dessus de votre invite. La dernière ligne est le
total du répertoire interrogé. Pour ce seul total, `du -sh` suffit :

```bash
sudo du -sh /usr/share
```

```text
171M	/usr/share
```

Le `sudo` n'est pas décoratif. Sans lui, `du` se heurte aux répertoires qu'il ne
peut pas lire et **sous-estime le total**, en signalant certes les refus, mais
sur la sortie d'erreur que la plupart des gens redirigent vers `/dev/null` :

```bash
du -sh /var 2>/dev/null       # 50M
sudo du -sh /var              # 71M
du -sh /var 2>&1 | grep -c 'Permission denied'   # 31
```

Vingt et un mégaoctets manquaient, répartis dans 31 répertoires illisibles. Un
diagnostic mené sans privilèges peut donc innocenter le vrai coupable.

Appliquons la méthode au conteneur saturé. Premier niveau :

```bash
sudo du -h --max-depth=1 /mnt/space-demo | sort -h
```

```text
12K	/mnt/space-demo/lost+found
3.1M	/mnt/space-demo/rapports
8.1M	/mnt/space-demo/archives
31M	/mnt/space-demo/exports
42M	/mnt/space-demo
```

`exports` pèse 31M sur les 42M du total. On y descend :

```bash
sudo du -h --max-depth=1 /mnt/space-demo/exports | sort -h
ls -lh /mnt/space-demo/exports/2026-07/
```

```text
31M	/mnt/space-demo/exports
31M	/mnt/space-demo/exports/2026-07

total 31M
-rw-r--r--. 1 root root 31M Jul 22 13:03 extraction.log
```

Deux `du` et un `ls` ont suffi. C'est toute la méthode : **on ne fouille pas, on
descend**, en suivant à chaque étage la ligne la plus lourde.

> **`ncdu` fait la même chose en interactif.** Le guide compagnon le recommande
> pour aller plus vite : tailles triées, navigation aux flèches, suppression par
> la touche `d`. Il n'est **pas installé** sur cette VM (`command -v ncdu`
> n'affiche rien et sort en code 1) ; il s'installe par `sudo dnf install ncdu`
> sur AlmaLinux, `sudo apt install ncdu` sur Debian et Ubuntu.

### Le piège du fichier supprimé mais encore ouvert

C'est le symptôme qui déroute, et celui que les examens aiment : vous supprimez
le gros fichier trouvé par `du`, et `df` ne bouge pas d'un pouce.

Mettons un processus en train d'écrire dans ce journal. Le `exec >>` ouvre le
fichier **une seule fois**, au démarrage, et garde le descripteur :

```bash
sudo tee /root/space-demo-writer.sh >/dev/null <<'EOF'
#!/bin/sh
exec >> /mnt/space-demo/exports/2026-07/extraction.log
while true; do echo "space-demo ligne"; sleep 5; done
EOF
sudo chmod +x /root/space-demo-writer.sh
sudo setsid /root/space-demo-writer.sh </dev/null >/dev/null 2>&1 &
```

On supprime le coupable, puis on regarde :

```bash
sudo rm -f /mnt/space-demo/exports/2026-07/extraction.log
sync
df -h /mnt/space-demo
sudo du -sh /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   42M  9.3M  82% /mnt/space-demo

12M	/mnt/space-demo
```

**`df` dit 42M, `du` dit 12M.** Trente mégaoctets ont disparu du côté de `du`
sans revenir du côté de `df`. La raison tient en une phrase : `rm` ne supprime
pas un fichier, il supprime un **nom**. Les blocs ne sont rendus que lorsque plus
personne ne tient l'inode, or notre processus le tient toujours par son
descripteur ouvert. Le fichier n'a plus de nom, donc `du`, qui parcourt
l'arborescence, ne le voit plus ; le filesystem, lui, le compte encore.

`lsof +L1` liste exactement ces fichiers, ceux dont le nombre de liens est
tombé sous 1 :

```bash
sudo lsof +L1
```

```text
COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NLINK NODE NAME
space-dem 39645 root    1w   REG    7,1 31457314     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
sleep     39783 root    1w   REG    7,1 31457314     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
```

Quatre colonnes portent toute l'information : `PID` désigne le processus à
traiter, `SIZE/OFF` chiffre l'espace retenu (31 457 314 octets, soit les 30 Mio
manquants), `NLINK` vaut `0` parce que plus aucun nom ne pointe vers l'inode, et
le suffixe `(deleted)` le confirme.

Deux détails que cette sortie révèle et qu'il faut avoir vus une fois :

- **Le descripteur s'hérite.** Le `sleep` de la boucle apparaît lui aussi, avec
  le même numéro d'inode : un enfant reçoit une copie des descripteurs de son
  parent. Tuer le seul parent ne libère donc pas toujours l'espace tout de suite.
- **Passer un point de montage en argument ne filtre pas.** Sur cette VM,
  `sudo lsof +L1 /mnt/space-demo` renvoie exactement la même liste que
  `sudo lsof +L1`, entrées d'autres filesystems comprises. Pour cibler, filtrez
  la sortie : `sudo lsof +L1 | grep /mnt/space-demo`.

La solution de référence est de **relancer proprement le service** qui écrit
(`sudo systemctl restart <service>`) : il ferme son ancien descripteur et en
rouvre un sur un fichier neuf. À défaut de service, on arrête le processus, en
visant le `PID` lu dans `lsof` :

```bash
sudo kill 39645
sleep 7
df -h /mnt/space-demo
sudo du -sh /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   12M   40M  22% /mnt/space-demo

12M	/mnt/space-demo
```

L'espace est rendu et les deux commandes se réconcilient : 12M des deux côtés,
82 % retombés à 22 %.

> **Tuez par PID, pas par motif.** `pkill -f space-demo-writer` semble plus
> commode, mais le motif est comparé à la ligne de commande **complète** de tous
> les processus. Sur cette VM, il a coupé la session SSH depuis laquelle il était
> lancé, parce que cette ligne de commande contenait elle aussi le motif. Le
> `PID` affiché par `lsof` ne présente pas ce risque.

#### Libérer l'espace sans couper le service

Quand redémarrer le service coûte trop cher, il existe une porte de sortie :
vider le fichier **par son descripteur**, à travers `/proc/<PID>/fd/<FD>`. La
colonne `FD` de `lsof` donne le numéro, ici `1w`, donc le descripteur 1 :

```bash
sudo sh -c ': > /proc/39645/fd/1'
df -h /mnt/space-demo
ps -o pid,comm,etime -p 39645
sudo lsof +L1 | grep extraction.log
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   12M   40M  22% /mnt/space-demo

    PID COMMAND             ELAPSED
  39645 space-demo-writ       00:23

space-dem 39645 root    1w   REG    7,1        0     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
sleep     39961 root    1w   REG    7,1        0     0   14 /mnt/space-demo/exports/2026-07/extraction.log (deleted)
```

L'espace est libéré, le processus **tourne toujours**, et `lsof` continue de
lister le fichier supprimé mais avec `SIZE/OFF` à `0` : il ne retient plus rien.
Cette manoeuvre fait gagner du temps sur un serveur en alerte, mais elle ne
dispense pas de traiter la cause (rotation de journaux absente, service à
relancer).

### La réserve d'ext4 : plein pour l'utilisateur, pas pour root

Revenons au premier conteneur, redescendu à 22 %, et laissons un utilisateur
ordinaire le remplir :

```bash
sudo mkdir -p /mnt/space-demo/bac-a-sable
sudo chmod 0777 /mnt/space-demo/bac-a-sable
sudo -u student dd if=/dev/zero of=/mnt/space-demo/bac-a-sable/space-demo-fill bs=1M count=100
df -h /mnt/space-demo
```

```text
dd: error writing '/mnt/space-demo/bac-a-sable/space-demo-fill': No space left on device
40+0 records in

Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   51M  3.0K 100% /mnt/space-demo
```

`Use%` est à 100 %, `Avail` à 3 Ko. Et pourtant root écrit encore :

```bash
sudo dd if=/dev/zero of=/mnt/space-demo/bac-a-sable/space-demo-root.bin bs=1M count=3 status=none
df -h /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   54M     0 100% /mnt/space-demo
```

Trois mégaoctets de plus sont passés. `tune2fs` explique pourquoi :

```bash
sudo tune2fs -l /dev/loop1 | grep -Ei '^Block count|^Reserved block count|^Block size|^Reserved blocks uid'
```

```text
Block count:              65536
Reserved block count:     3276
Block size:               1024
Reserved blocks uid:      0 (user root)
```

3 276 blocs de 1 Ko, soit environ 3,2 Mio (5 % du filesystem), sont **réservés à
root**. Le but est de garder un système saturé administrable : les services
système et les journaux ont encore de quoi écrire quand les applications n'en ont
plus. Conséquence à connaître : sur un filesystem ext4 affiché à 100 %, un `sudo`
réussira parfois là où l'application échoue. Ce n'est pas de la place retrouvée,
c'est la réserve qui s'entame.

### Quand le nettoyage ne suffit plus : agrandir

Il arrive qu'il n'y ait plus rien à supprimer. Il faut alors élargir le volume,
et la démarche dépend de la couche du dessous. Sur notre conteneur loopback en
ext4, l'agrandissement se fait **à chaud**, filesystem monté :

```bash
sudo rm -f /mnt/space-demo/bac-a-sable/space-demo-root.bin
df -h /mnt/space-demo
sudo truncate -s 128M /root/space-demo.img   # on agrandit le conteneur
sudo losetup -c /dev/loop1                   # le loop relit sa capacité
sudo resize2fs /dev/loop1                    # le filesystem prend la place
df -h /mnt/space-demo
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1       55M   51M  3.0K 100% /mnt/space-demo

resize2fs 1.47.1 (20-May-2024)
Filesystem at /dev/loop1 is mounted on /mnt/space-demo; on-line resizing required
old_desc_blocks = 1, new_desc_blocks = 1
The filesystem on /dev/loop1 is now 131072 (1k) blocks long.

Filesystem      Size  Used Avail Use% Mounted on
/dev/loop1      115M   51M   58M  47% /mnt/space-demo
```

L'ordre ne se néglige pas : **d'abord le contenant, ensuite le filesystem**.
`resize2fs` sans argument de taille prend tout l'espace disponible. Selon la
couche, le geste change :

| Couche | Commande d'agrandissement |
|---|---|
| Volume logique LVM | `sudo lvextend -r -L +<taille> <vg>/<lv>` (`-r` enchaîne le redimensionnement du filesystem) |
| Partition ext4 | agrandir la partition, puis `sudo resize2fs <partition>` |
| Partition XFS | agrandir la partition, puis `sudo xfs_growfs <point-de-montage>` |

Une règle à retenir de ce tableau : **XFS ne se réduit jamais**, il ne sait que
grandir. Et pour limiter la consommation en amont plutôt que courir après, ce
sont les quotas disque qu'il faut mettre en place.

### Les journaux systemd

Ils grossissent avec le temps et sont un coupable fréquent d'un `/var` qui gonfle
sans raison apparente. Leur taille se lit directement :

```bash
journalctl --disk-usage
```

```text
Archived and active journals take up 12.7M in the file system.
```

Deux commandes les réduisent sans rien casser : `sudo journalctl
--vacuum-size=200M` garde au plus 200 Mo, `sudo journalctl --vacuum-time=2weeks`
garde au plus deux semaines.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| « No space left on device » alors que `df -h` montre de la place | inodes épuisés : vérifier avec `df -i` |
| `df` reste plein après un `rm`, mais `du` a bien baissé | fichier supprimé encore ouvert : `sudo lsof +L1`, puis relancer le service ou tuer le PID |
| `df` reste plein même après avoir tué le processus | un enfant a hérité du descripteur ; relire `lsof +L1` et traiter les PID restants |
| `du` renvoie un total plus petit que la réalité | lancé sans `sudo` : les répertoires illisibles sont ignorés |
| L'application écrit « disque plein » mais `sudo` écrit encore | réserve root d'ext4 (5 % par défaut), visible par `sudo tune2fs -l` |
| `mkfs.xfs` refuse : `Filesystem must be larger than 300MB` | conteneur trop petit pour XFS ; utiliser ext4 ou agrandir |
| `resize2fs` ne voit pas la nouvelle taille | le périphérique loop n'a pas relu sa capacité : `sudo losetup -c /dev/loopN` |
| `/var` grossit sans fichier évident | journaux systemd : `journalctl --disk-usage`, puis `--vacuum-size` |
| Une session SSH se coupe pendant le nettoyage | un `pkill -f` a matché sa propre ligne de commande ; tuer par PID |

Pour tout défaire et repartir de zéro :

```bash
sudo kill <PID-du-writer>                 # relu dans lsof +L1 au besoin
sudo umount /mnt/space-demo /mnt/space-demo-inodes
sudo losetup -d /dev/loop1 /dev/loop2
sudo rm -f /root/space-demo.img /root/space-demo-inodes.img /root/space-demo-writer.sh
sudo rmdir /mnt/space-demo /mnt/space-demo-inodes
```

Vérifiez que rien ne traîne : `losetup -a` ne doit plus mentionner vos images, et
`df -h` ne doit plus lister vos points de montage.
