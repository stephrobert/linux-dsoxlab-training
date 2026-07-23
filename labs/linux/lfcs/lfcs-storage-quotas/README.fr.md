# Lab — quotas utilisateur XFS

## Rappel

[**Les quotas sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/)

Sur XFS, les quotas s'activent par une **option de montage**, pas par un service :
`uquota` (utilisateurs) ou `gquota` (groupes). `xfs_quota -x -c "state -u"
<montage>` montre deux choses distinctes — `Accounting` (mesurer) et
`Enforcement` (plafonner). Les limites se posent avec
`xfs_quota -x -c "limit bsoft=… bhard=… <user>" <montage>` et se relisent avec
`report -u -b`.

L'option de montage doit figurer dans `/etc/fstab`, sinon les quotas sont perdus
au prochain reboot.

## Le cours

Les exemples ci-dessous plafonnent un utilisateur `stagiaire` sur deux systèmes
de fichiers de démonstration montés dans `/mnt`, avec des seuils de quelques
mégaoctets : le challenge, lui, portera sur un autre support, un autre compte et
d'autres valeurs. Apprenez l'enchaînement, ne recopiez pas une ligne. Toutes les
sorties viennent d'une VM **Ubuntu 24.04.4**, noyau **6.8.0-134-generic**, la
même image que celle du lab.

### Où en est la machine

Trois questions avant de poser le premier quota : le noyau sait-il les gérer,
les outils sont-ils là, et pour quel système de fichiers.

```bash
sudo grep -E '^CONFIG_(QUOTA|QFMT_V2|XFS_QUOTA)=' /boot/config-$(uname -r)
```

```text
CONFIG_XFS_QUOTA=y
CONFIG_QUOTA=y
CONFIG_QFMT_V2=m
```

Lisez les suffixes, tout le cours tient dedans. **`y`** signifie compilé **dans**
le noyau, **`m`** fourni comme **module** séparé. Le support XFS est en dur ; le
format de fichier de quotas dont ext4 se sert (`QFMT_V2`) est un module, donc
quelque chose qui peut manquer. Nous verrons qu'il manque sur cette image.

Côté espace utilisateur, `xfs_quota` est déjà là (paquet `xfsprogs`), mais les
outils génériques manquent : `dpkg -l quota` répond `un  quota  <none>`, soit
état souhaité *Unknown*, état réel *Not-installed*. Un paquet unique, sans aucune
dépendance nouvelle, les apporte tous. Après `sudo apt-get install -y quota`, la
même commande répond `ii  quota  4.06-1build6  amd64  disk quota management
tools`, et vous disposez de `quotacheck`, `quotaon`, `setquota`, `edquota`,
`repquota` et `quota`.

### ext4 : la chaîne complète, et le module qui manque

Sur ext4 la mise en service demande quatre gestes : **option de montage**, puis
**fichiers de décompte**, puis **activation**, et seulement ensuite les limites.
Le support de démonstration est un fichier image monté en boucle, ce qui évite de
toucher au moindre disque :

```bash
sudo truncate -s 512M /var/tmp/coffre-ext4.img
sudo mkfs.ext4 -q -L coffre /var/tmp/coffre-ext4.img && sudo mkdir -p /mnt/coffre
sudo cp -a /etc/fstab /root/fstab.avant-quota          # toujours
echo '/var/tmp/coffre-ext4.img /mnt/coffre ext4 loop,defaults,usrquota,grpquota,nofail 0 2' \
  | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a && findmnt /mnt/coffre
```

```text
TARGET      SOURCE     FSTYPE OPTIONS
/mnt/coffre /dev/loop0 ext4   rw,relatime,quota,usrquota,grpquota
```

Deux réflexes à prendre dès maintenant : **sauvegardez `/etc/fstab` avant de
l'éditer**, et ajoutez **`nofail`** pendant vos essais, pour qu'une ligne fautive
ne bloque pas le démarrage. Vérifiez par `sudo mount -a` puis `findmnt --verify` :
si les deux passent, le reboot passera aussi.

Le montage seul ne plafonne rien. `quotacheck` parcourt le système de fichiers,
comptabilise l'existant et crée les fichiers de décompte (`-c` les crée, `-u` et
`-g` traitent utilisateurs et groupes, `-m` évite un remontage en lecture seule
pendant l'analyse) :

```bash
sudo quotacheck -cugm /mnt/coffre && ls -l /mnt/coffre
```

```text
-rw------- 1 root root  6144 Jul 22 18:08 aquota.group
-rw------- 1 root root  6144 Jul 22 18:08 aquota.user
[...]
```

Reste `quotaon`, qui demande au noyau d'appliquer. **Et c'est là que l'image
Ubuntu vous arrête** : telle qu'elle sort du cloud-init, la commande échoue.

```text
quotaon: Your kernel probably supports ext4 quota feature but you are using
external quota files. [...]
quotaon: Quota format not supported in kernel.
```

Le diagnostic tient en une commande, et il confirme le `=m` relevé plus haut :
`sudo modprobe quota_v2` répond `FATAL: Module quota_v2 not found in directory
/lib/modules/6.8.0-134-generic`. Le module existe, mais dans le paquet
`linux-modules-extra-$(uname -r)`, que l'image cloud Ubuntu n'installe pas. Une
fois ce paquet posé, la même commande passe :

```bash
sudo apt-get install -y linux-modules-extra-$(uname -r)
sudo quotaon -v /mnt/coffre && sudo quotaon -p /mnt/coffre
```

```text
/dev/loop0 [/mnt/coffre]: group quotas turned on
/dev/loop0 [/mnt/coffre]: user quotas turned on
user quota on /mnt/coffre (/dev/loop0) is on
project quota on /mnt/coffre (/dev/loop0) is off
```

Retenez la conclusion pratique : **sur cette image, XFS fait des quotas sans rien
installer d'autre que `quota`, ext4 non.** Le guide ne signale pas ce point.

Pour la persistance, `quotaon` n'a pas à être rejoué à la main : le générateur
systemd lit vos options `usrquota` dans `/etc/fstab` et branche l'unité qui va
bien, ce que `systemctl show mnt-coffre.mount -p Wants` confirme en répondant
`Wants=systemd-quotacheck.service quotaon.service`.

### Poser et lire les limites

`setquota` prend les quatre plafonds d'un coup, dans l'ordre **blocs souple,
blocs dur, inodes souple, inodes dur**, les blocs étant des blocs de 1 Kio et
`0` valant « aucune limite » :

```bash
sudo setquota -u stagiaire 8192 10240 0 0 /mnt/coffre
sudo repquota -s /mnt/coffre
```

```text
*** Report for user quotas on device /dev/loop0
Block grace time: 7days; Inode grace time: 7days
                        Space limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
root      --     20K      0K      0K              2     0     0
stagiaire --      4K   8192K  10240K              1     0     0
```

8192 blocs de 1 Kio font 8 Mio en limite souple, 10240 font 10 Mio en limite
dure. `edquota -u stagiaire` présente exactement les mêmes chiffres, mais dans un
éditeur, une ligne par système de fichiers, colonnes `blocks soft hard` puis
`inodes soft hard` :

```text
  Filesystem                   blocks       soft       hard     inodes     soft     hard
  /dev/loop0                        4       8192      10240          1        0        0
```

`setquota` pour scripter, `edquota` pour ajuster à la main : c'est le seul écart
entre les deux. Côté lecture, `repquota` donne la vue administrateur d'un montage
et `quota -us <user>` la vue d'un compte sur tous ses montages.

### Souple, dure, grâce : les trois franchissements

Écrivons 9 Mio, donc au-dessus des 8 Mio souples mais sous les 10 Mio durs :

```bash
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre/stagiaire/rapport bs=1M count=9
sudo repquota -s /mnt/coffre | sed -n '7p'      # tout de suite
sync ; sleep 2
sudo repquota -s /mnt/coffre | sed -n '7p'      # apres ecriture des donnees
```

```text
stagiaire --      4K   8192K  10240K              2     0     0
stagiaire +-   9220K   8192K  10240K  7days       2     0     0
```

Deux enseignements dans ces deux lignes. D'abord le décompte est **différé** :
tant que les données restent dans le cache d'écriture, `repquota` affiche encore
4 Kio (ext4 alloue tardivement), donc `du` et `repquota` peuvent diverger
quelques secondes. Ensuite, une fois le compte à jour, la colonne d'état passe à
**`+-`** (`+` = blocs en dépassement, `-` = inodes dans les clous) et la colonne
`grace` s'arme à `7days`. L'écriture, elle, n'a **pas** été refusée : c'est toute
la différence entre souple et dur. Poussons jusqu'à la limite dure :

```bash
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre/stagiaire/archive bs=1M count=5
```

```text
dd: error writing '/mnt/coffre/stagiaire/archive': Disk quota exceeded
1044480 bytes (1.0 MB, 1020 KiB) copied
```

`Disk quota exceeded` (`EDQUOT`) : le noyau a laissé passer l'écriture jusqu'au
plafond exact, puis a refusé. `sudo quota -us stagiaire` marque alors la valeur
d'une astérisque, `10240K*`, qui signifie « limite atteinte ».

Reste le piège : **la limite souple devient bloquante quand la grâce expire**. Le
délai se règle par montage, en secondes, avec `setquota -t` (ou `edquota -t`).
Ramené à deux minutes pour la démonstration :

```bash
sudo setquota -t 120 604800 /mnt/coffre       # 120 s pour les blocs, 7 j pour les inodes
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre/stagiaire/rapport bs=1M count=9
sudo repquota -s /mnt/coffre | sed -n '7p'    # juste apres
sleep 130
sudo repquota -s /mnt/coffre | sed -n '7p'    # apres expiration
```

```text
stagiaire +-   9220K   8192K  10240K  00:02       2     0     0
stagiaire +-   9220K   8192K  10240K   none       2     0     0
```

`none` ne veut pas dire « pas de dépassement » mais « **plus de grâce** ». À cet
instant, 9220 Kio consommés pour 10240 Kio autorisés : il reste 1 Mio en
apparence, et pourtant une écriture de 512 Kio copie **zéro octet** et retourne
`dd: error writing '/mnt/coffre/stagiaire/note': Disk quota exceeded`. C'est le
scénario qui génère les tickets : l'utilisateur est sous sa limite dure, il a
ignoré son dépassement une semaine durant, et la limite souple s'est refermée.
La sortie de secours est de faire du ménage pour repasser sous le seuil souple,
ce qui désarme le compteur.

Un mot sur l'avertissement : rien ne s'affiche dans la session de l'utilisateur
au franchissement du seuil souple. Le message existe, mais il est délivré par le
démon `quota_nld` (paquet `quota`), qui n'est pas lancé par défaut ; sans lui, le
seul signal est la colonne `grace` de `repquota`.

### Bloqué avec 452 Mio libres : les quotas d'inodes

Les deux dernières colonnes de `setquota` limitent le **nombre de fichiers**, pas
leur taille. On les oublie, et elles produisent le refus le plus déroutant qui
soit. Blocs illimités, cinq fichiers en souple, huit en dur :

```bash
sudo setquota -u stagiaire 0 0 5 8 /mnt/coffre
sudo -u stagiaire bash -c 'for i in $(seq 1 10); do touch /mnt/coffre/stagiaire/f$i; done'
sudo repquota -s /mnt/coffre | sed -n '7p' ; df -h /mnt/coffre | tail -1
```

```text
touch: cannot touch '/mnt/coffre/stagiaire/f8': Disk quota exceeded
touch: cannot touch '/mnt/coffre/stagiaire/f9': Disk quota exceeded
touch: cannot touch '/mnt/coffre/stagiaire/f10': Disk quota exceeded
stagiaire -+      4K      0K      0K              8     5     8  7days
/dev/loop0      488M   44K  452M   1% /mnt/coffre
```

Sept fichiers créés, le huitième refusé : le répertoire `stagiaire` compte
lui-même pour un inode, d'où les 8 du rapport pour 7 fichiers. Le disque est
occupé à **1 %**, il reste **452 Mio**, et pourtant plus rien ne s'écrit. Notez
l'inversion du drapeau, **`-+`** au lieu de `+-` : le dépassement est du côté des
inodes. Devant un `Disk quota exceeded` incompréhensible, `quota -us` avant tout,
et lisez la moitié droite du tableau.

### XFS : même besoin, autre mécanisme

Tout ce qui précède est propre à ext4. XFS tient son décompte **en interne** : ni
`quotacheck`, ni `quotaon`, ni fichier `aquota.*`. Les quotas s'activent
uniquement **au montage**, et c'est là qu'est le piège. Montage sans option de
quota, puis tentative d'ajout à chaud :

```bash
sudo mount -o loop /var/tmp/coffre-xfs.img /mnt/coffre-xfs
sudo xfs_quota -x -c 'state -u' /mnt/coffre-xfs ; echo "rc=$?"
sudo mount -o remount,uquota /mnt/coffre-xfs ; echo "rc=$?"
findmnt -no OPTIONS /mnt/coffre-xfs
```

```text
rc=0
rc=0
rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

Deux choses à voir. `state -u` **n'affiche rien du tout** et sort en 0 quand
aucun quota n'est actif : une sortie vide est le symptôme, pas une erreur. Et le
remontage **réussit** (`rc=0`) sans rien changer : les options restent `noquota`,
sans le moindre message. Seul un démontage complet fonctionne :

```bash
sudo umount /mnt/coffre-xfs
sudo mount -o loop,uquota /var/tmp/coffre-xfs.img /mnt/coffre-xfs
findmnt -no OPTIONS /mnt/coffre-xfs
sudo xfs_quota -x -c 'state -u' /mnt/coffre-xfs | head -3
```

```text
rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,usrquota
User quota state on /mnt/coffre-xfs (/dev/loop1)
  Accounting: ON
  Enforcement: ON
```

Détail qui compte : vous avez écrit `uquota`, `findmnt` affiche **`usrquota`** ;
le noyau normalise le nom, les deux désignent la même chose. `Accounting`
(mesurer) et `Enforcement` (plafonner) sont deux états distincts : le premier
seul compterait sans rien refuser. La gestion passe ensuite par `xfs_quota` en
mode expert (`-x`), avec des suffixes lisibles plutôt que des blocs de 1 Kio :

```bash
sudo xfs_quota -x -c 'limit -u bsoft=12m bhard=15m stagiaire' /mnt/coffre-xfs
sudo -u stagiaire dd if=/dev/zero of=/mnt/coffre-xfs/stagiaire/archive bs=1M count=13
sync ; sudo xfs_quota -x -c 'report -u -b' /mnt/coffre-xfs | tail -2
```

```text
User ID          Used       Soft       Hard    Warn/Grace
stagiaire       13312      12288      15360     00  [7 days]
```

Le compteur de grâce s'arme comme sur ext4, et `repquota -s` sait lire ce montage
aussi. En revanche `quotacheck` refuse net, avec un message qui rappelle
utilement qu'on n'est plus sur ext4 : `Cannot find filesystem to check or
filesystem not mounted with quota option.`

Enfin, l'option de quota se déclare dans `/etc/fstab` exactement comme plus haut,
en quatrième champ. Sans elle, le montage du prochain démarrage se fera en
`noquota` et vos limites, toujours enregistrées mais jamais appliquées, ne
protégeront plus rien.

### Dépannage et retour à l'état initial

| Symptôme | Cause probable | Solution |
|---|---|---|
| `quotaon: Quota format not supported in kernel` | Module `quota_v2` absent (image cloud Ubuntu) | `sudo apt-get install linux-modules-extra-$(uname -r)` |
| `quotacheck: Cannot find filesystem to check` | Options de quota absentes du montage, ou système de fichiers XFS | `findmnt <montage>` ; sur XFS, passer à `xfs_quota` |
| `xfs_quota -x -c 'state -u'` ne répond rien | Aucun quota actif sur ce montage | Démonter, remonter avec `uquota` |
| Les quotas XFS restent inactifs après `mount -o remount` | XFS ne lit ces options qu'au montage initial | `umount` puis `mount` |
| `Disk quota exceeded` avec de la place libre | Quota d'**inodes** atteint, ou grâce expirée sur le seuil souple | `quota -us <user>` et lire les colonnes de droite |
| `repquota` en désaccord avec `du` | Écriture pas encore vidée du cache | `sync`, puis relire |

Pour tout défaire, dans cet ordre : couper les quotas, démonter, restaurer
`/etc/fstab` depuis la copie prise **avant** l'édition, puis vérifier.

```bash
sudo quotaoff /mnt/coffre
sudo umount /mnt/coffre /mnt/coffre-xfs
sudo cp -a /root/fstab.avant-quota /etc/fstab && sudo systemctl daemon-reload
findmnt --verify | tail -1        # 0 parse errors, 0 errors
```

Dernier réflexe : supprimer un utilisateur ne supprime pas ses quotas, qui
restent attachés à l'UID et qu'un futur compte pourra hériter. Sur ext4, remettez
les compteurs à zéro par `sudo setquota -u <user> 0 0 0 0 <montage>` **avant** le
`userdel`.
