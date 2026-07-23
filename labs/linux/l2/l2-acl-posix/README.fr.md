# Lab — ACL POSIX

## Rappel

[**ACL sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/)

`setfacl -m u:<user>:<droits> <chemin>` ajoute une entrée utilisateur nommé,
`g:<groupe>:` une entrée groupe nommé. Sur un répertoire, `d:` (ou `-d`) pose une
ACL **par défaut** dont les nouveaux fichiers héritent. `getfacl <chemin>`
affiche toutes les entrées ; `setfacl -b` les retire ; `ls -l` montre un `+`
final sur les fichiers porteurs d'ACL.

## Le cours

Les exemples ci-dessous travaillent sur `/srv/atelier`, un répertoire de
démonstration, avec l'utilisateur `bruno` et le groupe `relecteurs` : le
challenge, lui, vous demandera d'autres chemins, d'autres comptes et d'autres
droits. Le but est d'apprendre la méthode, pas de recopier une ligne.

### Vérifier que les ACL sont disponibles

Deux conditions : les outils, et un système de fichiers qui sait les stocker.

```bash
command -v setfacl getfacl      # rien ne s'affiche si le paquet manque
sudo dnf -y install acl         # sur une image AlmaLinux minimale, il manque
findmnt -no FSTYPE,OPTIONS /
```

Sur la VM de ce lab, `findmnt` répond :

```text
xfs rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota
```

Notez qu'**aucune option `acl` n'apparaît**, et pourtant tout ce qui suit
fonctionne : sur **XFS** les ACL sont toujours actives, il n'y a rien à monter
en plus. Ne cherchez donc pas une option `acl` dans `/etc/fstab` : son absence
ne prouve rien. La VM de ce lab n'a que du XFS (`lsblk -f` le confirme), la
question ne se pose donc pas ici ; sur les vieux **ext3**, en revanche,
l'option de montage `acl` était nécessaire.

### Le décor de démonstration

```bash
sudo useradd -m bruno
sudo groupadd relecteurs
sudo mkdir -p /srv/atelier
echo "compte rendu de la reunion" | sudo tee /srv/atelier/notes.md
sudo chown -R root:root /srv/atelier
sudo chmod 0750 /srv/atelier
sudo chmod 0640 /srv/atelier/notes.md
```

Le fichier appartient à `root:root`, le répertoire est en `0750` : `bruno`
n'a strictement aucun accès. C'est le point de départ typique d'un besoin
d'ACL : on veut ouvrir un accès **sans** changer le propriétaire, ni le
groupe, ni les droits ugo.

### Poser une ACL utilisateur, et la première surprise

```bash
sudo setfacl -m u:bruno:r /srv/atelier/notes.md
sudo getfacl -p /srv/atelier/notes.md
```

`-m` veut dire *modify* : il ajoute l'entrée si elle n'existe pas, la remplace
sinon. `-p` demande à `getfacl` de garder le `/` initial du chemin, ce qui
évite une ambiguïté sur laquelle nous reviendrons. Sortie :

```text
# file: /srv/atelier/notes.md
# owner: root
# group: root
user::rw-
user:bruno:r--
group::r--
mask::r--
other::---
```

`ls -l` signale la présence d'une ACL par un `+` final :

```text
-rw-r-----+ 1 root root 27 Jul 22 12:01 /srv/atelier/notes.md
```

Et pourtant, `bruno` ne lit toujours rien :

```bash
sudo -u bruno cat /srv/atelier/notes.md
# cat: /srv/atelier/notes.md: Permission denied
```

C'est le piège que la théorie oublie : une ACL sur un fichier ne donne aucun
droit sur le **chemin** qui y mène. Pour ouvrir un fichier, il faut le droit
`x` (traversée) sur **chaque** répertoire du chemin. Ici `/srv/atelier` est en
`0750 root:root` : `bruno` ne peut même pas entrer.

### Ouvrir le chemin avec une ACL de groupe sur le répertoire

```bash
sudo usermod -aG relecteurs bruno
sudo setfacl -m g:relecteurs:rwx /srv/atelier
sudo getfacl -p /srv/atelier
```

```text
# file: /srv/atelier
# owner: root
# group: root
user::rwx
group::r-x
group:relecteurs:rwx
mask::rwx
other::---
```

Cette fois la lecture passe :

```bash
sudo -u bruno cat /srv/atelier/notes.md
# compte rendu de la reunion
id bruno
# uid=1003(bruno) gid=1004(bruno) groups=1004(bruno),1005(relecteurs)
```

`sudo -u bruno` démarre un nouveau processus, dont la liste de groupes est
relue à ce moment-là : l'ajout est donc pris en compte tout de suite. Un
processus déjà lancé, lui, garde les groupes qu'il avait à son démarrage, d'où
le réflexe de se reconnecter après un `usermod -aG` quand le test se fait
depuis une session ouverte.

### Le mask : un plafond qu'un simple `chmod` déplace

Passons `bruno` en écriture, et vérifions qu'il écrit vraiment :

```bash
sudo setfacl -m u:bruno:rw /srv/atelier/notes.md
sudo -u bruno sh -c 'echo ligne-ajoutee >> /srv/atelier/notes.md'   # OK
```

Maintenant, l'accident classique : quelqu'un « range » les droits du fichier.

```bash
sudo chmod g=r /srv/atelier/notes.md
sudo getfacl -p /srv/atelier/notes.md
```

```text
user::rw-
user:bruno:rw-	#effective:r--
group::r--
mask::r--
other::---
```

```bash
sudo -u bruno sh -c 'echo deuxieme-ligne >> /srv/atelier/notes.md'
# sh: line 1: /srv/atelier/notes.md: Permission denied
```

L'entrée de `bruno` n'a pas bougé, elle affiche toujours `rw-`. C'est le
**mask** qui est tombé à `r--`, et le mask est un **plafond** appliqué à toutes
les entrées nommées (`user:<nom>:`, `group:<nom>:`) ainsi qu'au groupe
propriétaire. La colonne `#effective:` donne le droit réellement obtenu. Sur
un fichier porteur d'ACL, `chmod g=…` ne touche pas le groupe propriétaire :
il réécrit le mask.

On le relève explicitement :

```bash
sudo setfacl -m m::rw /srv/atelier/notes.md
```

Corollaire à connaître : **`ls -l` affiche le mask, pas `group::`**. Après
réparation, `getfacl` dit `group::r--` alors que `ls -l` affiche :

```text
-rw-rw----+ 1 root root 57 Jul 22 12:01 /srv/atelier/notes.md
```

Le `rw` du milieu est le mask. Dès qu'il y a un `+`, ne lisez plus les droits
de groupe dans `ls -l` : lisez `getfacl`.

### L'ACL par défaut, pour que les nouveaux fichiers héritent

Une ACL par défaut ne donne aucun droit sur le répertoire lui-même : elle est
un **modèle** recopié dans tout ce qui sera créé dedans ensuite.

```bash
sudo setfacl -d -m g:relecteurs:rw /srv/atelier
sudo getfacl -p /srv/atelier
```

```text
user::rwx
group::r-x
group:relecteurs:rwx
mask::rwx
other::---
default:user::rwx
default:group::r-x
default:group:relecteurs:rw-
default:mask::rwx
default:other::---
```

Une seule entrée demandée, cinq lignes `default:` créées : un jeu d'ACL par
défaut doit être complet, le noyau comble les entrées obligatoires à partir des
droits ugo du répertoire. `-d -m g:…` et `-m d:g:…` sont deux écritures de la
même chose.

Vérifions l'héritage sur un fichier neuf, puis sur un sous-répertoire :

```bash
sudo touch /srv/atelier/herite.txt
sudo getfacl -p /srv/atelier/herite.txt
```

```text
user::rw-
group::r-x	#effective:r--
group:relecteurs:rw-
mask::rw-
other::---
```

L'entrée `relecteurs` est bien là. Notez au passage un `#effective:` sur une
entrée que personne n'a posée à la main : `group::` a hérité de `r-x`, plafonné
par un mask `rw-` calculé à la création. Un `#effective:` n'est donc pas
toujours le signe d'une erreur.

```bash
sudo mkdir /srv/atelier/sous-dossier
sudo getfacl -p /srv/atelier/sous-dossier
```

Un sous-répertoire hérite des deux jeux à la fois : l'ACL d'accès **et** l'ACL
par défaut, qui se propage donc de proche en proche.

Deux limites à retenir :

```bash
sudo setfacl -d -m g:relecteurs:r /srv/atelier/notes.md
# setfacl: /srv/atelier/notes.md: Only directories can have default ACLs
```

Et surtout : une ACL par défaut ne s'applique **qu'au futur**. Les fichiers
déjà présents ne bougent pas. Pour rattraper l'existant, il faut un passage
récursif :

```bash
sudo setfacl -R -m u:bruno:rX /srv/atelier
```

Le `X` **majuscule** n'accorde `x` que sur les répertoires et sur les fichiers
qui l'ont déjà. Sur l'arborescence de démonstration, la même commande donne
`user:bruno:r-x` au répertoire, `user:bruno:r--` à `notes.md` et
`user:bruno:r-x` au sous-répertoire. Avec un `x` minuscule, tous les fichiers
seraient devenus exécutables.

### Retirer, auditer, sauvegarder

```bash
sudo setfacl -x u:bruno /srv/atelier/notes.md   # une entrée nommée
sudo setfacl -k /srv/atelier                    # les ACL par défaut seulement
sudo setfacl -b /srv/atelier                    # tout, retour aux droits ugo
```

Après `setfacl -b`, `getfacl` ne montre plus que `user::`, `group::` et
`other::`, et le `+` disparaît de `ls -l`. Attention : retirer une entrée avec
`-x` recalcule le mask, qui redescend souvent. Vérifiez les entrées restantes.

Pour l'audit, listez les seules entrées nommées de toute une arborescence,
entrées par défaut comprises :

```bash
sudo getfacl -pR /srv/atelier 2>/dev/null | grep -E '^(default:)?(user|group):[^:]+:'
```

Le motif écarte `user::`, `group::`, `mask::` et `other::`, qui ne sont que la
traduction des droits ugo, et ne garde que ce qui a été accordé nommément.

Pour la sauvegarde, `-p` n'est pas un détail :

```bash
sudo sh -c 'getfacl -pR /srv/atelier > /root/acl-atelier.bak'
sudo setfacl --restore=/root/acl-atelier.bak
```

Sans `-p`, `getfacl` prévient (`Removing leading '/' from absolute path
names`) et écrit `# file: srv/atelier`. La restauration devient alors relative
au répertoire courant, et depuis n'importe où ailleurs que `/` elle échoue :

```text
setfacl: srv/atelier: No such file or directory
```

Dernier point de vigilance, la copie : `cp` sans option perd les ACL en
silence (plus de `+` sur la copie), `cp -a` les conserve. Même logique avec
`rsync`, qui a besoin de `-A`.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `command -v setfacl` ne renvoie rien | le paquet `acl` n'est pas installé |
| `setfacl: Option -m: Invalid argument near character 3` | l'utilisateur ou le groupe nommé n'existe pas |
| `Only directories can have default ACLs` | `-d` (ou `d:`) appliqué à un fichier |
| `Permission denied` alors que l'ACL du fichier est bonne | il manque le droit `x` sur un répertoire du chemin |
| `Permission denied` et une entrée marquée `#effective:` | le mask plafonne ; le relever avec `setfacl -m m::rw <chemin>` |
| Les droits ont changé sans qu'on touche à l'ACL | un `chmod` est passé et a réécrit le mask |
| Les nouveaux fichiers n'ont pas l'ACL attendue | pas d'ACL par défaut sur le répertoire parent |
| Les fichiers déjà présents n'ont pas l'ACL attendue | l'ACL par défaut ne vaut que pour le futur, passer `setfacl -R -m` |
| `setfacl: srv/…: No such file or directory` au `--restore` | sauvegarde faite sans `-p` ; se placer dans `/` ou refaire avec `-p` |
| `Permission denied` avec ACL et mask corrects | vérifier la couche MAC : `sudo ausearch -m AVC -ts recent` (SELinux est en `Enforcing` sur cette VM) |

Pour tout défaire et repartir de zéro :

```bash
sudo rm -rf /srv/atelier
sudo userdel -r bruno
sudo groupdel relecteurs
```
