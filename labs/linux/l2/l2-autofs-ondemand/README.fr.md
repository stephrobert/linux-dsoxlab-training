# Lab — montages à la demande avec autofs

## Rappel

[**autofs sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/)

autofs monte un chemin seulement à l'accès et le démonte après un `--timeout`
d'inactivité. Une **carte maître** (`/etc/auto.master` ou un fichier de
`/etc/auto.master.d/`) associe un point de montage à une **carte de montage** ;
la carte de montage liste des clés et comment les monter, sous la forme
`clé  -options  source`. `systemctl restart autofs` recharge les cartes.

## Le cours

Les exemples ci-dessous travaillent sur `/mnt/autofs-demo`, une image XFS de
démonstration posée dans `/srv/autofs-demo` : le challenge, lui, vous demandera
un autre point de montage, d'autres fichiers de cartes et une autre source. Le
but est d'apprendre la méthode, pas de recopier une ligne.

Toutes les sorties ci-dessous ont été produites sur la VM de ce lab
(AlmaLinux 10, `autofs-5.1.9-13.el10.x86_64`).

### Où en est la machine

Avant d'écrire quoi que ce soit, regardez ce qui existe déjà :

```bash
rpm -q autofs                 # ou: dpkg -l autofs sur Debian/Ubuntu
systemctl is-active autofs
cat /etc/auto.master
ls -la /etc/auto.master.d/
```

Sur une AlmaLinux fraîche, `/etc/auto.master` existe et **contient déjà deux
points de montage** livrés par le paquet, `/misc` et `/net`, plus la ligne
d'inclusion `+dir:/etc/auto.master.d` qui charge tous les fichiers `*.autofs`
de ce répertoire. Ne les prenez pas pour votre configuration.

`automount -m` affiche ce qu'autofs a réellement chargé, cartes maîtresse et de
montage confondues :

```bash
sudo automount -m
```

```text
Mount point: /misc

source(s):

  instance type(s): file
  map: /etc/auto.misc

  cd | -fstype=iso9660,ro,nosuid,nodev	:/dev/cdrom
```

C'est la commande à lancer en premier quand une carte « ne prend pas » : si
votre point de montage n'y figure pas, autofs ne l'a pas lu.

### Préparer une source à monter

Pour la démonstration, une image de fichier formatée en XFS fera office de
disque. `mkfs.xfs` refuse les images de moins de 300 Mo, d'où les 512 Mio.

```bash
sudo mkdir -p /srv/autofs-demo
sudo truncate -s 512M /srv/autofs-demo/archives.img
sudo mkfs.xfs -q /srv/autofs-demo/archives.img
ls -lh /srv/autofs-demo/
```

```text
total 65M
-rw-r--r--. 1 root root 512M Jul 22 13:00 archives.img
```

Notez l'écart entre la taille annoncée (`512M`) et l'occupation réelle
(`total 65M`) : `truncate` crée un fichier creux, qui ne consomme que ce qu'on
y écrit.

On y dépose un témoin, en montant l'image une fois à la main, pour avoir de
quoi vérifier plus tard que le montage automatique sert bien ce contenu :

```bash
sudo mkdir -p /mnt/autofs-demo-seed
sudo mount -o loop /srv/autofs-demo/archives.img /mnt/autofs-demo-seed
echo "inventaire 2026" | sudo tee /mnt/autofs-demo-seed/inventaire.txt
sudo umount /mnt/autofs-demo-seed && sudo rmdir /mnt/autofs-demo-seed
```

### Les deux cartes

autofs a besoin de deux fichiers, et l'ordre logique est toujours le même.

1. La **carte maître** dit *où* : elle associe un point de montage parent à un
   fichier de carte. On ne modifie pas `/etc/auto.master` : on dépose un fichier
   `*.autofs` dans `/etc/auto.master.d/`, inclus automatiquement.

   ```text
   /point-de-montage-parent   /etc/fichier-de-carte   [options]
   ```

2. La **carte de montage** dit *quoi* : une ligne par montage, sous la forme
   `clé  -options  source`. La clé devient le sous-répertoire créé sous le
   point parent. La source est un périphérique local (`:/dev/…`), une image, ou
   un partage réseau (`serveur:/export`).

Écrivons les deux :

```bash
echo '/mnt/autofs-demo  /etc/auto.autofs-demo  --timeout=30' \
  | sudo tee /etc/auto.master.d/autofs-demo.autofs
echo 'archives  -fstype=xfs,loop  :/srv/autofs-demo/archives.img' \
  | sudo tee /etc/auto.autofs-demo
sudo systemctl restart autofs
```

L'option `loop` demande à `mount` d'attacher l'image à un périphérique loop ;
elle n'a de sens que pour une source qui est un fichier. `--timeout=30`
démonte après 30 secondes d'inactivité.

Regardez ce que le redémarrage a changé dans la table des montages :

```bash
mount | grep autofs
```

Avant :

```text
/etc/auto.misc on /misc type autofs (rw,relatime,fd=6,pgrp=38113,timeout=300,...,indirect,...)
-hosts on /net type autofs (rw,relatime,fd=9,pgrp=38113,timeout=300,...,indirect,...)
```

Après :

```text
/etc/auto.misc on /misc type autofs (...)
-hosts on /net type autofs (...)
/etc/auto.autofs-demo on /mnt/autofs-demo type autofs (rw,relatime,fd=12,pgrp=38638,timeout=30,minproto=5,maxproto=5,indirect,pipe_ino=104355)
```

Trois choses à lire dans cette ligne. Le **type est `autofs`**, pas `xfs` :
rien du contenu n'est encore monté, c'est le déclencheur qui est en place. Le
**`timeout=30`** confirme que l'option de la carte maître a bien été prise. Et
le mot **`indirect`** dit qu'autofs gère un répertoire parent sous lequel il
créera les clés.

Le répertoire `/mnt/autofs-demo` n'a jamais été créé à la main : c'est autofs
qui le pose quand il lit la carte maître.

### Le déclenchement, et le piège du répertoire vide

C'est le point qui déroute tout le monde. Après le redémarrage du service, le
parent a l'air **vide** :

```bash
ls -la /mnt/autofs-demo
```

```text
total 0
drwxr-xr-x. 2 root root  0 Jul 22 13:01 .
drwxr-xr-x. 4 root root 43 Jul 22 13:01 ..
```

Aucune trace de la clé `archives`, et pourtant la carte est bonne. Un `ls` du
parent **ne déclenche rien** : la table des montages ne bouge pas.

Il faut nommer la clé pour que le montage parte :

```bash
ls -l /mnt/autofs-demo/archives
```

```text
total 4
-rw-r--r--. 1 root root 16 Jul 22 13:00 inventaire.txt
```

Cette fois la table a changé :

```bash
mount | grep autofs-demo
```

```text
/etc/auto.autofs-demo on /mnt/autofs-demo type autofs (rw,relatime,...,timeout=30,...,indirect,...)
/srv/autofs-demo/archives.img on /mnt/autofs-demo/archives type xfs (rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota)
```

Une **deuxième ligne** est apparue, de type `xfs` cette fois : le système de
fichiers est monté. Et le parent n'est plus vide :

```text
drwxr-xr-x. 3 root root  0 Jul 22 13:01 .
drwxr-xr-x. 4 root root 43 Jul 22 13:01 ..
drwxr-xr-x. 2 root root 28 Jul 22 13:00 archives
```

`lsblk` montre le périphérique loop attaché au passage :

```text
loop2    7:2    0  512M  0 loop /mnt/autofs-demo/archives
```

> **`findmnt <chemin>` déclenche le montage qu'il est censé constater.** Sur
> cette VM, après expiration du timeout, `findmnt /mnt/autofs-demo/archives` ne
> renvoie rien (`rc=1`, donc « pas monté »), mais un
> `grep autofs-demo /proc/self/mounts` lancé **juste après** montre le montage
> XFS présent : le simple fait de nommer le chemin a réveillé autofs, et
> `findmnt` a lu la table avant que le montage n'existe. Résultat : la première
> commande dit « rien », la seconde dit « monté », et on croit à une
> incohérence. Pour observer l'état **sans** le modifier, lisez la table sans
> toucher au chemin : `mount | grep …` ou `grep … /proc/self/mounts`.

Si ce répertoire parent vide vous gêne, l'option **`--ghost`** dans la carte
maître fait apparaître les clés en répertoires vides avant tout montage :

```bash
sudo sed -i 's|--timeout=30|--timeout=30 --ghost|' /etc/auto.master.d/autofs-demo.autofs
sudo systemctl restart autofs
ls -la /mnt/autofs-demo
```

```text
total 0
drwxr-xr-x. 5 root root   0 Jul 22 13:08 .
drwxr-xr-x. 9 root root 173 Jul 22 13:08 ..
drwxr-xr-x. 2 root root   0 Jul 22 13:08 archives
drwxr-xr-x. 2 root root   0 Jul 22 13:08 casse
drwxr-xr-x. 2 root root   0 Jul 22 13:08 nouvelle
```

Cette sortie a été relevée plus tard dans la séance, quand la carte comptait
déjà trois clés : `casse` et `nouvelle` apparaissent dans les sections
suivantes. L'essentiel est ailleurs : les clés sont visibles, mais **rien n'est
monté**. `grep autofs-demo/ /proc/self/mounts` ne renvoie toujours rien tant
qu'on n'entre pas dedans. Ces répertoires sont des leurres qui rendent la carte
lisible, pas des montages.

Dernier réflexe utile : le parent d'une carte indirecte **n'est pas
inscriptible**, autofs seul y crée des entrées.

```bash
sudo mkdir /mnt/autofs-demo/essai
# mkdir: cannot create directory ‘/mnt/autofs-demo/essai’: Permission denied
```

Un `Permission denied` en `root` sur un point autofs n'est donc pas une
anomalie de droits : c'est le fonctionnement normal.

### Le démontage automatique

Laissez passer le timeout sans toucher au chemin, puis lisez la table sans le
nommer :

```bash
sleep 50
grep autofs-demo /proc/self/mounts
```

```text
/etc/auto.autofs-demo /mnt/autofs-demo autofs rw,relatime,fd=12,...,timeout=30,...,indirect,... 0 0
```

La ligne `xfs` a disparu, celle de type `autofs` reste : le contenu a été
démonté, le déclencheur est toujours armé. Un nouvel accès le remontera.

Ne comptez pas sur un démontage à la seconde près. Le démon vérifie
périodiquement, à un rythme visible dans sa sortie bavarde :

```text
mounted indirect on /mnt/autofs-demo with timeout 30, freq 8 seconds
```

Avec `--timeout=30`, la vérification passe toutes les 8 secondes : le montage
disparaît donc quelque part entre 30 et 38 secondes après le dernier accès.

### Recharger : `reload` plutôt que `restart`

Le guide recommande `systemctl restart autofs` après chaque changement. Sur
cette VM, le comportement observé est plus fin, et la nuance vaut le détour.

**Une nouvelle clé dans la carte de montage ne demande aucun rechargement.**
Ajout d'une ligne, puis accès immédiat, sans rien redémarrer :

```bash
echo 'nouvelle  -fstype=bind  :/srv/autofs-demo/coffres/2025' \
  | sudo tee -a /etc/auto.autofs-demo
ls /mnt/autofs-demo/nouvelle
# bilan.txt
```

Le démon relit le fichier de carte de lui-même. Sa sortie bavarde l'annonce :
`re-reading map for /mnt/autofs-demo`.

**Un nouveau point de montage dans la carte maître, en revanche, exige un
rechargement.** Ajoutons-en un, avec sa carte de montage, sans rien recharger :

```bash
echo '/mnt/autofs-demo-tardif  /etc/auto.autofs-demo-tardif  --timeout=30' \
  | sudo tee -a /etc/auto.master.d/autofs-demo.autofs
echo 'k  -fstype=bind  :/srv/autofs-demo/coffres/2024' \
  | sudo tee /etc/auto.autofs-demo-tardif
ls /mnt/autofs-demo-tardif/k
# ls: cannot access '/mnt/autofs-demo-tardif/k': No such file or directory
```

Et `systemctl reload autofs` suffit, ce qui est préférable à `restart` :

```bash
sudo systemctl reload autofs
ls /mnt/autofs-demo-tardif/k
# bilan.txt
```

La différence entre les deux est concrète. Avec un montage actif, `reload` le
**conserve** ; `restart` le **jette** :

```text
--- avant reload ---
/dev/loop3 /mnt/autofs-demo/archives xfs rw,seclabel,relatime,... 0 0
--- apres reload ---
/dev/loop3 /mnt/autofs-demo/archives xfs rw,seclabel,relatime,... 0 0
--- apres restart ---
(plus rien)
```

Sur une machine de production où des utilisateurs travaillent dans des montages
autofs, `reload` évite de leur couper l'accès sous les pieds.
`systemctl show -p CanReload autofs` répond `CanReload=yes` sur AlmaLinux 10.

### Carte à joker : une ligne pour toutes les clés

Déclarer une ligne par utilisateur ou par année serait ingérable. Le caractère
`*` accepte n'importe quelle clé, et `&` en reprend la valeur dans la source.
Le guide illustre ce cas avec des répertoires personnels NFS ; ici, à défaut de
serveur, la même mécanique est montrée avec des montages `bind` locaux.

```bash
sudo mkdir -p /srv/autofs-demo/coffres/2024 /srv/autofs-demo/coffres/2025
echo "bilan 2024" | sudo tee /srv/autofs-demo/coffres/2024/bilan.txt
echo "bilan 2025" | sudo tee /srv/autofs-demo/coffres/2025/bilan.txt
echo '/mnt/autofs-demo-coffres  /etc/auto.autofs-demo-coffres  --timeout=30' \
  | sudo tee -a /etc/auto.master.d/autofs-demo.autofs
echo '*  -fstype=bind  :/srv/autofs-demo/coffres/&' \
  | sudo tee /etc/auto.autofs-demo-coffres
sudo systemctl restart autofs
```

Les deux clés se montent séparément, à la demande, sans qu'aucune n'ait été
déclarée :

```bash
cat /mnt/autofs-demo-coffres/2025/bilan.txt   # bilan 2025
cat /mnt/autofs-demo-coffres/2024/bilan.txt   # bilan 2024
grep autofs-demo-coffres /proc/self/mounts
```

```text
/etc/auto.autofs-demo-coffres /mnt/autofs-demo-coffres autofs ...,indirect,... 0 0
/dev/vda4 /mnt/autofs-demo-coffres/2025 xfs rw,seclabel,relatime,... 0 0
/dev/vda4 /mnt/autofs-demo-coffres/2024 xfs rw,seclabel,relatime,... 0 0
```

Deux détails à relever. La source affichée est `/dev/vda4`, le disque qui porte
réellement les données : un `bind` ne crée pas de nouveau périphérique, il
réexpose une arborescence existante. Et une clé sans source correspondante
échoue proprement :

```bash
ls /mnt/autofs-demo-coffres/1999
# ls: cannot access '/mnt/autofs-demo-coffres/1999': No such file or directory
```

### Carte directe : un chemin absolu, sans parent commun

Quand les points de montage n'ont pas de répertoire parent commun, la carte
maître utilise le symbole `/-` et c'est la carte de montage qui porte les
chemins absolus.

```bash
echo '/-  /etc/auto.autofs-demo-direct  --timeout=30' \
  | sudo tee -a /etc/auto.master.d/autofs-demo.autofs
echo '/mnt/autofs-demo-direct  -fstype=bind  :/srv/autofs-demo/coffres/2024' \
  | sudo tee /etc/auto.autofs-demo-direct
sudo systemctl restart autofs
cat /mnt/autofs-demo-direct/bilan.txt   # bilan 2024
```

La table des montages distingue les deux familles par le dernier mot des
options :

```text
/etc/auto.autofs-demo        /mnt/autofs-demo        autofs ...,indirect,... 0 0
/etc/auto.autofs-demo-direct /mnt/autofs-demo-direct autofs ...,direct,...   0 0
```

`indirect` pour un parent qui fabrique ses clés, `direct` pour un chemin
déclaré en toutes lettres. C'est le moyen le plus rapide de savoir quel type de
carte on a réellement écrit.

### Le cas NFS

Le montage NFS à la demande est l'usage historique d'autofs, et celui attendu
en RHCSA comme en LFCS. La configuration est identique, seule la **source**
change : un chemin `serveur:/export`.

```bash
echo '/mnt/nfs  /etc/auto.documents  --timeout=120' \
  | sudo tee /etc/auto.master.d/documents.autofs
echo 'documents  -rw,soft  serveur-nfs.exemple:/srv/nfs/documents' \
  | sudo tee /etc/auto.documents
sudo systemctl restart autofs
```

L'option `soft` évite qu'un processus reste bloqué indéfiniment si le serveur
disparaît ; réservez-la aux données non critiques, et gardez le défaut `hard`
pour de l'écriture sensible. Le paquet client NFS est nécessaire (`nfs-utils`
sur RHEL et dérivés, `nfs-common` sur Debian et Ubuntu).

> **Un serveur NFS sur la machine locale ne donne pas du NFS.** Si la source
> pointe vers `localhost` ou vers le nom de la machine elle-même, autofs
> fabrique un **bind local** : `findmnt` affiche alors un type `xfs`, le disque
> local, au lieu de `nfs4`. Tester réellement un montage NFS suppose un serveur
> **distant**. Ce point vient du guide et n'a pas pu être vérifié sur cette VM,
> qui est seule.

### Dépanner un montage qui ne part pas

Quand un accès renvoie `No such file or directory` sans plus d'explication,
`journalctl -u autofs` ne vous aidera pas : sur cette VM, un montage en échec
n'y laisse **aucune trace**, le journal ne contient que le démarrage et l'arrêt
du service.

La seule méthode qui donne la cause exacte est celle du guide : arrêter le
service et lancer le démon **au premier plan, en mode bavard**, puis provoquer
l'accès **depuis un autre terminal**.

```bash
# terminal 1
sudo systemctl stop autofs
sudo automount -f -v

# terminal 2
ls /mnt/autofs-demo/archives
ls /mnt/autofs-demo/inexistante
```

Le terminal 1 raconte alors exactement ce qui se passe :

```text
mounted indirect on /mnt/autofs-demo with timeout 30, freq 8 seconds
attempting to mount entry /mnt/autofs-demo/archives
mounted /mnt/autofs-demo/archives
attempting to mount entry /mnt/autofs-demo/inexistante
key "inexistante" not found in map source(s).
failed to mount /mnt/autofs-demo/inexistante
```

Une clé absente de la carte et une source qui refuse de se monter donnent deux
messages distincts. Avec une source inexistante :

```text
attempting to mount entry /mnt/autofs-demo/casse
mount(generic): failed to mount /srv/autofs-demo/absent.img (type xfs) on /mnt/autofs-demo/casse
failed to mount /mnt/autofs-demo/casse
```

Côté utilisateur, les deux échecs se ressemblent pourtant trait pour trait :
`No such file or directory`, avec `rc=2`. D'où l'intérêt du mode bavard.

Terminez toujours par un `Ctrl+C` sur le démon et un
`sudo systemctl start autofs`, sans quoi plus aucun montage automatique ne
fonctionne sur la machine.

> **Le démon et l'accès doivent venir de deux sessions différentes.** Lancer
> `automount -f -v` en arrière-plan puis faire le `ls` dans le **même** script
> a donné, sur cette VM, un `No such file or directory` sur une clé pourtant
> valide, et pas une ligne dans le journal du démon. La même clé s'est montée
> sans broncher dès que l'accès venait d'une seconde connexion. Deux terminaux,
> comme le dit le guide.

| Symptôme | Cause probable |
|---|---|
| Le point parent est vide alors que la carte est bonne | comportement normal : seul l'accès à une **clé** déclenche le montage ; ajouter `--ghost` pour voir les clés |
| `key "…" not found in map source(s)` | la clé demandée n'existe pas dans la carte de montage (faute de frappe, ou joker absent) |
| `mount(generic): failed to mount …` | la source est fausse, ou le `-fstype=` ne correspond pas au système de fichiers réel |
| Le point de montage n'apparaît pas du tout dans `mount` | la carte maître n'a pas été relue : `systemctl reload autofs` |
| Un nouveau point de montage reste introuvable | il a été ajouté à la carte **maître** : un rechargement est obligatoire, contrairement aux clés d'une carte de montage |
| `Permission denied` sur un `mkdir` dans le parent, même en root | normal : le parent d'une carte indirecte n'est pas inscriptible |
| `findmnt` dit « pas monté » puis `mount` dit « monté » | `findmnt <chemin>` a déclenché le montage ; observer via `mount` ou `/proc/self/mounts` |
| Type `xfs` au lieu de `nfs4` sur un montage NFS | la source pointe vers la machine locale : autofs a fait un bind |
| Rien ne se monte nulle part après un dépannage | `automount -f -v` est resté au premier plan et le service est arrêté : `systemctl start autofs` |

### Tout défaire

Retirer une carte de montage ne suffit pas : tant que la carte maître déclare
le point, autofs le maintient armé. On retire donc dans l'ordre inverse de la
création, puis on recharge.

```bash
sudo rm -f /etc/auto.master.d/autofs-demo.autofs
sudo rm -f /etc/auto.autofs-demo /etc/auto.autofs-demo-coffres \
           /etc/auto.autofs-demo-direct /etc/auto.autofs-demo-tardif
sudo systemctl restart autofs
mount | grep autofs-demo          # doit ne rien renvoyer
sudo rm -rf /srv/autofs-demo
```

Le `restart` final est celui qui compte, et il fait plus qu'on ne croit. Après
lui, `/mnt` est **entièrement vide** :

```text
total 0
drwxr-xr-x.  2 root root   6 Jul 22 13:13 .
dr-xr-xr-x. 20 root root 258 Jul 22 13:13 ..
```

Aucun `rmdir` n'a été nécessaire : autofs supprime les répertoires qu'il avait
créés, puisqu'il les avait créés lui-même. Il libère aussi les périphériques
loop, ce que `losetup -a` confirme avant de supprimer les images.
