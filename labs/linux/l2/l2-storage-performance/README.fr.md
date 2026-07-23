# Lab — optimiser un montage avec noatime

## Rappel

[**Performances disques sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/)

Les options de montage changent le comportement d'un filesystem. `noatime`
désactive les mises à jour de date d'accès, un gain courant pour les charges
très lues ou avec beaucoup de petits fichiers. Mets-le dans `/etc/fstab` (4ᵉ
champ) pour la persistance, et `mount -o remount <mnt>` pour l'appliquer à chaud.
`findmnt <mnt>` montre les options actives.

## Le cours

Les exemples ci-dessous portent sur un filesystem XFS de démonstration monté sur
`/mnt/perf` (disque `/dev/vdb` de 2 Gio), avec ses propres options. Le challenge
vous demandera autre chose, ailleurs : ce qui compte ici est la méthode, pas la
ligne à recopier.

Toutes les sorties de ce cours ont été relevées sur une machine AlmaLinux 10
(noyau 6.12, 948 Mio de RAM, disques virtio), elle-même **invitée d'un
hyperviseur partagé**. Les chiffres sont réels mais **ne sont pas
transposables** : la section « Mesurer dans une machine virtuelle » dit pourquoi.

### Trois grandeurs, jamais une « vitesse »

Parler de la « vitesse » d'un disque comme d'un nombre unique est la première
erreur. Trois grandeurs différentes décrivent un stockage, et un service lent ne
souffre presque jamais des trois à la fois.

| Métrique | Ce qu'elle mesure | Quand elle compte |
|---|---|---|
| **Débit** (Mo/s) | volume transféré par seconde | gros fichiers, sauvegardes, vidéo |
| **IOPS** | opérations par seconde | bases de données, nombreux petits fichiers |
| **Latence** (`await`, ms) | temps de réponse d'une opération | ressenti utilisateur, applications interactives |

Une base de données lente est presque toujours un problème d'IOPS ou de latence,
pas de débit. Le type de disque change les ordres de grandeur : un disque dur
plafonne vers 100 à 200 IOPS, un SSD SATA atteint des dizaines de milliers, un
NVMe dépasse le million.

### Le piège du cache : la même lecture, deux résultats

Linux garde en mémoire les blocs lus et écrits (le cache de pages). Une lecture
juste après une écriture mesure donc la **RAM**, pas le disque. La preuve, sur un
fichier de 200 Mio :

```bash
sudo dd if=/dev/urandom of=/mnt/perf/demo.bin bs=1M count=200 status=none
sync
sudo dd if=/mnt/perf/demo.bin of=/dev/null bs=1M          # 1re lecture
sudo dd if=/mnt/perf/demo.bin of=/dev/null bs=1M          # 2e lecture
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'      # on vide le cache
sudo dd if=/mnt/perf/demo.bin of=/dev/null bs=1M          # 3e lecture
```

Ne vous fiez pas au seul débit affiché : comptez ce que le périphérique a
réellement servi. Le noyau tient ces compteurs dans `/sys/block/<dev>/stat`,
dont le 3ᵉ champ est le nombre de **secteurs lus** (512 octets) depuis le boot :

```bash
awk '{print $3}' /sys/block/vdb/stat
```

En encadrant chaque `dd` par cette lecture, on obtient :

| Lecture | Débit affiché | Servi par `vdb` |
|---|---|---|
| 1re, cache chaud | 11,3 Go/s | 0 Mio |
| 2e, cache chaud | 12,5 Go/s | 0 Mio |
| 3e, après `drop_caches` | 6,2 Go/s | 200 Mio |

Les deux premières mesures **n'ont pas touché le disque une seule fois**. Le
débit qu'elles affichent est celui d'une recopie mémoire.

`drop_caches` est le levier qui rend une lecture honnête. Il ne détruit rien (il
ne libère que des données propres, déjà écrites), mais faites précéder d'un
`sync`, et n'en faites pas une habitude sur un serveur en production : vous lui
retirez son cache.

Côté écriture, trois formulations mesurent trois choses différentes. Trois
répétitions chacune, fichier de 512 Mio :

```bash
F=/mnt/perf/testfile
dd if=/dev/zero of=$F bs=1M count=512               # aucune option
dd if=/dev/zero of=$F bs=1M count=512 conv=fsync    # fsync final
dd if=/dev/zero of=$F bs=1M count=512 oflag=direct  # sans cache
```

```text
sans rien    : 2,8 Go/s | 752 Mo/s | 1,1 Go/s
conv=fsync   : 758 Mo/s | 1,0 Go/s | 901 Mo/s
oflag=direct : 1,2 Go/s | 1,4 Go/s | 980 Mo/s
```

- **Sans rien**, `dd` rend la main dès que les données sont dans le cache : le
  premier essai à 2,8 Go/s mesure la vitesse à laquelle le noyau accepte de la
  donnée, rien d'autre. C'est le chiffre qu'il ne faut jamais citer.
- **`conv=fsync`** ajoute un `fsync()` à la fin : le temps inclut la vidange du
  cache. C'est la mesure la plus proche de ce que ressent une application qui
  écrit puis attend.
- **`oflag=direct`** contourne le cache à chaque bloc (`O_DIRECT`). C'est ce que
  `fio` fait avec `--direct=1`.

### Mesurer dans une machine virtuelle : ce que `direct` ne contourne pas

`oflag=direct` contourne le cache **de cette machine**. Il ne contourne pas celui
de l'hyperviseur, qui garde lui aussi le fichier disque en mémoire. `fio` en
lecture aléatoire de 4 ko le montre sans ambiguïté :

```bash
sudo fio --name=randread --directory=/mnt/perf --rw=randread --bs=4k \
    --size=256M --runtime=15 --time_based --ioengine=libaio \
    --direct=1 --group_reporting
```

```text
read: IOPS=51.1k, BW=200MiB/s (209MB/s)(2995MiB/15001msec)
  lat (usec): min=12, max=3473, avg=19.28, stdev=14.48
```

51 100 IOPS avec une latence moyenne de **19 µs** et une file d'attente de 1
(`iodepth=1` par défaut) : aucun support physique ne répond en 19 µs à cette
cadence. Ces chiffres décrivent la mémoire de l'hôte, pas un disque.

Trois exécutions ont donné 51,1k, 54,1k et 54,2k IOPS (latences 19,3 / 18,2 /
18,2 µs), soit environ 6 % d'écart entre les extrêmes. **Un chiffre isolé ne
prouve rien.** Répétez au moins trois fois, annoncez l'ordre de grandeur et la
dispersion, et donnez le contexte. Ici l'hôte est partagé avec d'autres machines
virtuelles : la même commande relancée demain donnera autre chose.

Ce qu'une mesure faite dans une VM autorise à affirmer : le **rapport** entre
deux configurations mesurées dans la même session (avec cache contre sans cache,
`atime` contre `noatime`). Ce qu'elle n'autorise pas : une caractéristique du
matériel.

> `fio` n'est pas installé par défaut. Sur AlmaLinux 10, il vient du dépôt
> **appstream** (`sudo dnf install fio`) et non d'EPEL : vérifiez par
> `dnf info fio` avant de conclure. `dd` suffit pour tout ce qui précède.

### Observer la charge réelle avec iostat

`fio` **provoque** une charge, `iostat` (paquet `sysstat`) **observe** celle qui
existe. Deux pièges tiennent en une phrase : le premier échantillon est une
moyenne **depuis le démarrage** (à ignorer), et `-z` masque les périphériques
inactifs.

```bash
sudo dnf install sysstat
iostat -xz 3 2          # seul le 2e bloc est significatif
```

Relevé pendant une écriture soutenue en blocs de 64 kio sur `/mnt/perf` :

```text
Device      w/s      wkB/s  w_await  wareq-sz   f/s  f_await  aqu-sz  %util
vdb    10270.00  657135.33     0.08     63.99  4.67    95.00    1.28  83.20
```

Les colonnes de lecture, à zéro pendant ce test, sont omises ici. Ce que cette
ligne dit :

- **`w/s` = 10 270** : les IOPS réelles en écriture.
- **`wkB/s` = 657 135**, soit environ 640 Mio/s, cohérent avec `wareq-sz` = 64
  kio, la taille de bloc demandée à `dd`.
- **`w_await` = 0,08 ms** : la latence, l'indicateur le plus parlant d'un goulot.
- **`aqu-sz` = 1,28** : la file d'attente moyenne. Un seul `dd` séquentiel ne
  peut guère faire mieux que 1.
- **`f/s`** et **`f_await`** : les demandes de vidange (flush), bien plus lentes
  (95 ms) que les écritures elles-mêmes.

**`%util` = 83 % ne veut pas dire « saturé ».** Cette colonne mesure la fraction
de temps pendant laquelle au moins une requête est en cours. Sur un périphérique
capable d'en traiter plusieurs en parallèle (SSD, NVMe, disque virtio), elle
peut atteindre 100 % alors que le disque en accepterait dix fois plus. Ici, une
latence de 0,08 ms et une file de 1,28 disent l'inverse de la saturation.
Fiez-vous à `await` et `aqu-sz`. La colonne `svctm`, que citent encore de vieux
guides, a disparu de sysstat 12 parce qu'elle était trompeuse (l'atelier tourne
en 12.7.6).

Pour savoir **quel processus** génère les E/S, le guide propose `iotop -oP`.
Attention : `iotop` n'est pas dans les dépôts de base d'AlmaLinux 10
(`dnf info iotop` ne renvoie rien). `pidstat`, livré avec `sysstat`, fait
l'essentiel et exige les droits root :

```bash
sudo pidstat -d 3 1
```

```text
15:14:38  UID   PID   kB_rd/s   kB_wr/s  kB_ccwr/s  iodelay  Command
15:14:38    0  37288      0.00  261273.09     0.00        0  sh
```

### Connaître le périphérique avant de l'accuser

```bash
lsblk -t -o NAME,PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,RA /dev/vdb
cat /sys/block/vdb/queue/scheduler
```

```text
NAME PHY-SEC LOG-SEC ROTA SCHED       RQ-SIZE   RA
vdb      512     512    1 mq-deadline     256 4096

none [mq-deadline] kyber bfq
```

- **`PHY-SEC` / `LOG-SEC`** : tailles de secteur physique et logique, 512 octets
  toutes les deux ici. `RA` donne la lecture anticipée (readahead) en kio.
- **`SCHED`** : l'ordonnanceur actif, entre crochets dans `/sys`. Ici
  `mq-deadline`. `none` signifie qu'on ne réordonne rien et qu'on transmet les
  requêtes telles quelles : c'est le réglage courant quand le tri se fait plus
  bas, dans l'hyperviseur ou dans le contrôleur NVMe, car réordonner deux fois
  n'ajoute que de la latence.
- **`ROTA` = 1** annonce un disque rotatif. C'est faux ici : virtio ne sait pas
  ce qu'il y a derrière. **Ne déduisez jamais la nature du support depuis une
  VM.**

`hdparm` donne un ordre de grandeur en lecture brute, sans passer par le
filesystem :

```bash
sudo hdparm -tT /dev/vdb
```

```text
 Timing cached reads:   31420 MB in  2.00 seconds = 15744.18 MB/sec
 Timing buffered disk reads: 2048 MB in  0.45 seconds =  4531.27 MB/sec
```

La première ligne mesure la **mémoire**, c'est explicitement son rôle. Seule la
seconde parle du périphérique, et encore, avec les réserves de la section
précédente. Trois exécutions ont donné 4531, 4605 et 4566 Mo/s.

### Optimiser après avoir mesuré : `atime`, `relatime`, `noatime`

Chaque lecture de fichier met à jour sa **date d'accès** (atime), donc transforme
une lecture en écriture. Depuis longtemps, Linux monte par défaut en
**`relatime`**, qui n'écrit l'atime que s'il est plus ancien que la date de
modification, ou vieux de plus de 24 h. Vérifiez-le, ne le supposez pas :

```bash
findmnt -no OPTIONS /mnt/perf
```

```text
rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

La sémantique se voit en trois gestes, avec `stat -c %x` qui affiche l'atime :

```text
après écriture   : 15:14:56.228
après 1 lecture  : 15:14:57.242   <- mis à jour, car atime valait mtime
après 2 lectures : 15:14:57.242   <- inchangé
```

`relatime` limite donc les dégâts sans les supprimer : chaque premier accès coûte
une écriture. Ce coût se mesure, toujours avec les compteurs du noyau (7ᵉ champ
de `/sys/block/vdb/stat` : secteurs **écrits**). Protocole : 3 000 petits
fichiers neufs, `sync`, `drop_caches`, puis une lecture complète.

```bash
sudo sh -c 'for i in $(seq 1 3000); do echo x > /mnt/perf/many/f$i; done'
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
awk '{print $7}' /sys/block/vdb/stat
sudo sh -c 'cat /mnt/perf/many/* > /dev/null'; sync
awk '{print $7}' /sys/block/vdb/stat
```

| Option de montage | Secteurs écrits pendant une lecture pure |
|---|---|
| `relatime` (défaut) | 4 533, soit environ 2,2 Mio |
| `noatime` | 0 |

Voilà le gain, mesuré : sur une charge de lecture, `noatime` supprime
**totalement** les écritures parasites. Sur 3 000 fichiers c'est anecdotique ;
sur un serveur qui en lit des millions par heure, c'est un flux d'écritures
continu qui disparaît.

L'appliquer à chaud, sans démonter :

```bash
sudo mount -o remount,noatime /mnt/perf
findmnt -no OPTIONS /mnt/perf
```

```text
rw,noatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

Ce réglage vit en mémoire : il disparaît au redémarrage. Pour qu'il tienne, il
faut une ligne dans `/etc/fstab`, dont le **4ᵉ champ** porte les options :

```text title="/etc/fstab"
UUID=12b52e83-a599-4e61-8cad-9de570f2a33c /mnt/perf xfs rw,noatime,nofail 0 0
```

L'UUID s'obtient par `sudo blkid -s UUID -o value /dev/vdb` et vaut mieux qu'un
nom de périphérique, dont l'ordre peut changer au démarrage. Une erreur dans
`/etc/fstab` pouvant bloquer le boot, sauvegardez et vérifiez :

```bash
sudo cp -a /etc/fstab /etc/fstab.bak   # avant d'éditer
sudo findmnt --verify                  # 0 parse errors, 0 errors attendus
sudo systemctl daemon-reload           # systemd relit le nouveau fstab
```

Un `mount -o remount` **sans autre option** relit les options de `/etc/fstab` :
c'est le geste qui remet d'accord le montage actif et le fichier.

```bash
sudo mount -o remount /mnt/perf
findmnt -no SOURCE,TARGET,OPTIONS /mnt/perf
```

```text
/dev/vdb /mnt/perf rw,noatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

Après un vrai redémarrage de la machine, `findmnt` affiche toujours `noatime` :
la persistance est acquise, ce qu'aucun `remount` ne prouve à lui seul.

> **Retirer `noatime` n'est pas symétrique.** Vérifié sur util-linux 2.40.2 :
> `mount -o remount,relatime /mnt/perf` laisse `noatime` en place, tandis que
> `mount -o remount,atime /mnt/perf` le retire et rend `relatime`. C'est
> l'option `atime` qui annule `noatime` ; `relatime` seul n'y suffit pas.
> Contrôlez toujours par `findmnt`, ne supposez pas.

### Dépannage

| Symptôme | Cause probable | Piste |
|---|---|---|
| Débit `dd` irréaliste (plusieurs Go/s) | cache non contourné | `oflag=direct` ou `conv=fsync`, et `drop_caches` avant une lecture |
| Deux mesures identiques donnent des chiffres très différents | mesure unique, hôte partagé, test trop court | répéter au moins 3 fois, allonger la durée (`--runtime=30 --time_based`) |
| `%util` à 100 % mais application fluide | faux positif sur périphérique parallèle | regarder `r_await` / `w_await` et `aqu-sz`, pas `%util` |
| `iostat` affiche des valeurs curieusement stables | premier échantillon, moyenne depuis le boot | ignorer le premier bloc, lire à partir du second |
| `findmnt` ne montre pas l'option ajoutée dans `/etc/fstab` | fstab modifié, montage inchangé | `sudo mount -o remount <point-de-montage>` |
| L'option est active mais disparaît au redémarrage | posée seulement par `mount -o remount,<option>` | l'écrire dans le 4ᵉ champ de `/etc/fstab` |
| `iotop` introuvable | absent des dépôts de base d'AlmaLinux 10 | `sudo pidstat -d 3 1` |
