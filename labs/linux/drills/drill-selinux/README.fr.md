# Drill — SELinux

**4 tâches, 100 points, 20 minutes. Aucun indice.** RHCSA uniquement
(Debian → `drill-apparmor`). Les contextes sont vérifiés **après une relabellisation**.

## Rappel

[**SELinux : comprendre, dépanner et désactiver**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

SELinux ajoute au contrôle d'accès classique (DAC, les droits `rwx`) un contrôle
**obligatoire** (MAC) : chaque processus et chaque ressource porte une étiquette,
et la politique croise ces étiquettes pour autoriser ou refuser. Le travail
quotidien porte sur quatre objets : le **mode** (`enforcing`, `permissive`,
`disabled`), les **contextes de fichiers**, les **booléens** et les **types de
ports**. Pour chacun de ces quatre objets, il existe un réglage **à chaud** et un
réglage **dans la politique** : c'est cette distinction que le drill mesure.

## Le cours

Les exemples ci-dessous travaillent sur `/opt/partage-demo`, un répertoire de
démonstration destiné à un partage de fichiers, avec le type `samba_share_t`, le
booléen `samba_export_all_ro` et le port `2222/tcp`. Le challenge, lui, vous
demandera d'autres chemins, d'autres types, un autre booléen et un autre port.
Le but est d'apprendre la méthode, pas de recopier une ligne.

Toutes les sorties reproduites ici viennent d'une AlmaLinux 10 en mode
`enforcing`, avec `policycoreutils-python-utils` installé (c'est le paquet qui
fournit `semanage`, absent d'une installation minimale).

### La seule idée à retenir : runtime contre policy

SELinux a deux mémoires. La première est celle du **noyau en cours
d'exécution** : elle se modifie instantanément, et elle est perdue au
redémarrage. La seconde est le **magasin de politique local**, sur disque : il
faut une commande explicite pour y écrire, et c'est ce qui est rejoué au boot.

| Objet | Réglage à chaud (perdu au reboot) | Réglage dans la policy (persistant) |
|---|---|---|
| Mode | `setenforce 1` / `setenforce 0` | ligne `SELINUX=` de `/etc/selinux/config` |
| Contexte d'un fichier | `chcon -t <type> <chemin>` | `semanage fcontext -a` puis `restorecon` |
| Booléen | `setsebool <nom> on` | `setsebool -P <nom> on` |
| Type d'un port | *(rien : il n'y a pas de réglage à chaud)* | `semanage port -a -t <type> -p tcp <port>` |

Chaque ligne de gauche donne un système qui marche tout de suite et qui casse
plus tard. C'est exactement le piège de l'examen.

### Lire le mode, et voir les deux mémoires d'un coup

`getenforce` répond en un mot :

```bash
getenforce
```

```text
Enforcing
```

`sestatus` est plus utile, parce qu'il affiche **les deux** valeurs :

```bash
sestatus
```

```text
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Memory protection checking:     actual (secure)
Max kernel policy version:      33
```

`Current mode` est le noyau, `Mode from config file` est le disque. Basculez à
chaud et l'écart saute aux yeux :

```bash
sudo setenforce 0
sestatus | grep -E "Current mode|Mode from config file"
```

```text
Current mode:                   permissive
Mode from config file:          enforcing
```

```bash
grep "^SELINUX=" /etc/selinux/config
```

```text
SELINUX=enforcing
```

`setenforce` **n'a pas touché** au fichier de configuration : vérifié par le
`md5sum` du fichier avant et après, identique. Retour au mode strict :

```bash
sudo setenforce 1
getenforce
```

```text
Enforcing
```

Deux détails utiles, vérifiés sur la machine :

- `setenforce` accepte aussi les mots : `setenforce Permissive` et
  `setenforce Enforcing` fonctionnent comme `0` et `1` ;
- sans privilège, la commande échoue explicitement :
  `setenforce: security_setenforce() failed: Permission denied`. `getenforce`,
  lui, se lit sans `sudo`.

Pour la persistance, on édite la ligne `SELINUX=` de `/etc/selinux/config`.
Le guide insiste : **pas d'espace autour du `=`**, sinon la ligne est ignorée.

> **Ne mettez jamais `SELINUX=disabled` sur RHEL 9 / AlmaLinux 9 et au-delà.**
> Cette valeur n'y est plus supportée par ce fichier : le noyau démarre avec
> SELinux puis bascule tardivement. Pour désactiver réellement, on passe par la
> ligne de commande noyau (`grubby --update-kernel ALL --args selinux=0`), et
> **revenir de `disabled` à `enforcing` exige une relabellisation complète**
> (`touch /.autorelabel` puis reboot), parce que les fichiers créés sans SELinux
> n'ont aucune étiquette. C'est long, et c'est la raison pour laquelle on ne
> désactive pas SELinux « juste pour voir ».

### Lire un contexte

Un contexte est une étiquette à quatre champs, `utilisateur:rôle:type:niveau`.
Le champ qui compte au quotidien est le **type**, le troisième.

```bash
sudo mkdir -p /opt/partage-demo
echo "notes de service" | sudo tee /opt/partage-demo/memo.txt
ls -Zd /opt/partage-demo
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:usr_t:s0 /opt/partage-demo
unconfined_u:object_r:usr_t:s0 /opt/partage-demo/memo.txt
```

`-Z` marche partout : sur un processus avec `ps -eZ`, sur votre propre session
avec `id -Z`.

```bash
ps -eZ | grep sshd
```

```text
system_u:system_r:sshd_t:s0-s0:c0.c1023 1082 ?   00:00:00 sshd
system_u:system_r:sshd_session_t:s0-s0:c0.c1023 11315 ? 00:00:00 sshd-session
```

> **Un répertoire neuf n'hérite pas d'un type neutre, il hérite de son parent.**
> Le guide annonce `default_t` pour un répertoire créé de toutes pièces. C'est
> vrai seulement quand **aucune** règle de la politique ne couvre le chemin.
> Ici `/opt` est déclaré `usr_t` dans la politique, donc tout ce qu'on y crée
> naît `usr_t`. La commande qui répond sans supposer est `matchpathcon`, qui
> donne le type **attendu** par la politique pour un chemin :
>
> ```bash
> matchpathcon /opt/partage-demo
> matchpathcon /data/html
> ```
>
> ```text
> /opt/partage-demo	system_u:object_r:usr_t:s0
> /data/html	system_u:object_r:default_t:s0
> ```
>
> `/data` n'existe pas sur cette machine et n'est couvert par aucune règle :
> c'est lui qui donne `default_t`, pas `/opt`.

### `chcon` : ça marche, et ça ne tient pas

`chcon` écrit l'étiquette directement sur l'inode. Le résultat est immédiat :

```bash
sudo chcon -t samba_share_t /opt/partage-demo/memo.txt
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:samba_share_t:s0 /opt/partage-demo/memo.txt
```

Le service accède au fichier, tout va bien. Puis quelqu'un relabellise :

```bash
sudo restorecon -v /opt/partage-demo/memo.txt
ls -Z /opt/partage-demo/memo.txt
```

```text
Relabeled /opt/partage-demo/memo.txt from unconfined_u:object_r:samba_share_t:s0 to unconfined_u:object_r:usr_t:s0
unconfined_u:object_r:usr_t:s0 /opt/partage-demo/memo.txt
```

Le travail est effacé. `restorecon` ne « restaure » pas ce que vous aviez posé :
il repose ce que **la politique** prescrit, et la politique n'a jamais entendu
parler de votre `chcon`. Réservez `chcon` aux essais de quelques minutes.

### `semanage fcontext` + `restorecon` : le réglage qui tient

Deux commandes, et l'ordre a un sens : on **déclare** d'abord la règle, on
**applique** ensuite.

```bash
sudo semanage fcontext -a -t samba_share_t "/opt/partage-demo(/.*)?"
sudo semanage fcontext -l -C
```

```text
SELinux fcontext                                   type               Context

/opt/partage-demo(/.*)?                            all files          system_u:object_r:samba_share_t:s0
```

L'option `-C` limite la liste aux règles **locales**, celles que vous avez
ajoutées. Sans elle, `semanage fcontext -l` déroule les règles de la politique
de base : 5927 lignes sur cette machine (`semanage fcontext -l | wc -l`).

Attention : déclarer ne change rien sur le disque. Juste après le `semanage`, le
fichier porte toujours son ancien type :

```bash
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:usr_t:s0 /opt/partage-demo/memo.txt
```

C'est `restorecon` qui applique la règle, `-R` pour descendre récursivement et
`-v` pour dire ce qu'il fait :

```bash
sudo restorecon -Rv /opt/partage-demo
```

```text
Relabeled /opt/partage-demo from unconfined_u:object_r:usr_t:s0 to unconfined_u:object_r:samba_share_t:s0
Relabeled /opt/partage-demo/memo.txt from unconfined_u:object_r:usr_t:s0 to unconfined_u:object_r:samba_share_t:s0
```

Et maintenant la preuve qui manquait à `chcon` : on relabellise une seconde
fois, et **rien ne bouge** (`restorecon -Rv` n'affiche plus une seule ligne,
parce qu'il n'a plus rien à corriger).

```bash
sudo restorecon -Rv /opt/partage-demo
ls -Z /opt/partage-demo/memo.txt
```

```text
unconfined_u:object_r:samba_share_t:s0 /opt/partage-demo/memo.txt
```

Sur l'expression de chemin : `"/opt/partage-demo(/.*)?"` est une **expression
régulière**, à mettre entre guillemets pour que le shell n'y touche pas. Elle se
lit « ce répertoire, et éventuellement tout ce qu'il contient ». Sans le
`(/.*)?`, seul le répertoire lui-même serait couvert et les fichiers dedans
garderaient leur type.

La règle est écrite dans le magasin local, qu'on peut lire :

```bash
sudo cat /var/lib/selinux/targeted/active/file_contexts.local
```

```text
# This file is auto-generated by libsemanage
# Do not edit directly.

/opt/partage-demo(/.*)?    system_u:object_r:samba_share_t:s0
```

> **Le fichier existe à deux endroits, et les deux sont à jour.** Mesuré sur
> AlmaLinux 10 : `semanage` écrit à la fois
> `/var/lib/selinux/targeted/active/file_contexts.local` (le magasin actif, en
> `0600`) et `/etc/selinux/targeted/contexts/files/file_contexts.local` (en
> `0644`), avec le même contenu et le même horodatage. On ne les édite jamais à
> la main, mais savoir où ils sont permet de vérifier d'un coup d'œil ce qui a
> été rendu persistant.

Notez que la règle déclare `system_u` alors que le fichier reste `unconfined_u`
après `restorecon` : par défaut, `restorecon` ne corrige que le **type**.
L'option `-F` force le contexte entier, champ utilisateur compris.

```bash
sudo restorecon -FRv /opt/partage-demo
```

```text
Relabeled /opt/partage-demo from unconfined_u:object_r:samba_share_t:s0 to system_u:object_r:samba_share_t:s0
Relabeled /opt/partage-demo/memo.txt from unconfined_u:object_r:samba_share_t:s0 to system_u:object_r:samba_share_t:s0
```

Pour les règles qui vous intéressent, seul le type compte : ne vous alarmez pas
d'un `unconfined_u`.

### Ce qui casse un contexte sans prévenir : `mv`

Une fois la règle en place, un fichier **créé** dans le répertoire, ou **copié**
dedans, prend le bon type tout seul. Un fichier **déplacé** garde le sien.

```bash
echo "source"  > /tmp/source.txt
echo "source2" > /tmp/source2.txt
echo "nouveau" | sudo tee /opt/partage-demo/nouveau.txt
sudo cp /tmp/source.txt  /opt/partage-demo/copie.txt
sudo mv /tmp/source2.txt /opt/partage-demo/deplace.txt
ls -Z /opt/partage-demo/
```

```text
unconfined_u:object_r:samba_share_t:s0 copie.txt
   unconfined_u:object_r:user_tmp_t:s0 deplace.txt
    system_u:object_r:samba_share_t:s0 memo.txt
unconfined_u:object_r:samba_share_t:s0 nouveau.txt
```

`copie.txt` et `nouveau.txt` sont bons, `deplace.txt` a rapatrié le
`user_tmp_t` de `/tmp`. `mv` ne recrée pas le fichier, il change son nom : le
contexte suit. D'où le réflexe après tout déplacement :

```bash
sudo restorecon -Rv /opt/partage-demo
```

```text
Relabeled /opt/partage-demo/deplace.txt from unconfined_u:object_r:user_tmp_t:s0 to unconfined_u:object_r:samba_share_t:s0
```

### Les booléens

Un booléen est un interrupteur prévu par la politique : il active ou désactive
un paquet de règles sans écrire de module. Il y en a 314 sur cette AlmaLinux 10
(`getsebool -a | wc -l`).

```bash
getsebool samba_export_all_ro
```

```text
samba_export_all_ro --> off
```

`setsebool` sans option agit **uniquement sur le noyau en cours** :

```bash
sudo setsebool samba_export_all_rw on
sudo semanage boolean -l | grep "^samba_export_all_rw"
```

```text
samba_export_all_rw            (on   ,  off)  Allow samba to export all rw
```

Ce couple `(courant, défaut)` est le meilleur outil de diagnostic de tout le
lab : **la première valeur est l'état du noyau, la seconde celle de la
politique**. `(on, off)` veut dire « actif maintenant, éteint au prochain
reboot ». C'est un piège qui ne se voit pas avec `getsebool`, qui n'affiche que
la première.

L'option `-P` écrit la valeur dans la politique :

```bash
sudo setsebool -P samba_export_all_ro on
sudo semanage boolean -l | grep "^samba_export_all_ro"
```

```text
samba_export_all_ro            (on   ,   on)  Allow samba to export all ro
```

`(on, on)` : les deux mémoires sont d'accord, le réglage survivra. Le raccourci
pour ne voir que ce qui a été rendu persistant :

```bash
sudo semanage boolean -l -C
```

```text
SELinux boolean                State  Default Description

samba_export_all_ro            (on   ,   on)  Allow samba to export all ro
```

Le booléen basculé sans `-P` n'y figure pas : c'est bien la liste du persistant.
La valeur vit dans `/var/lib/selinux/targeted/active/booleans.local` :

```text
# This file is auto-generated by libsemanage
# Do not edit directly.

samba_export_all_ro=1
```

`setsebool -P` est plus lent que `setsebool` (il recompile le magasin) : c'est
normal, laissez-le finir.

### Les ports

Un service ne peut se lier qu'à un port dont le type est autorisé pour son
domaine. Changer un service de port sans le dire à SELinux, c'est un échec au
démarrage. On regarde d'abord ce que la politique connaît :

```bash
sudo semanage port -l | grep -E "^ssh_port_t"
```

```text
ssh_port_t                     tcp      22
```

On ajoute le port voulu au type :

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo semanage port -l | grep -E "^ssh_port_t"
```

```text
ssh_port_t                     tcp      2222, 22
```

Et la liste des ajouts locaux, qui prouve que c'est bien dans la politique :

```bash
sudo semanage port -l -C
```

```text
SELinux Port Type              Proto    Port Number

ssh_port_t                     tcp      2222
```

Il n'y a **pas** d'équivalent « à chaud » pour un port : `semanage port` est le
seul geste, il est persistant par construction. C'est le seul des quatre objets
du tableau où l'on ne peut pas se tromper de mémoire.

Pour trouver à qui appartient déjà un port, on cherche le numéro entier :

```bash
sudo semanage port -l | grep -w 3306
```

```text
mysqld_port_t                  tcp      1186, 3306, 63132-63164
```

> **Sur AlmaLinux 10, `semanage port -a` sur un port déjà pris n'échoue pas.**
> Le guide annonce un `ValueError ... already defined` qui obligerait à
> reprendre la commande avec `-m`. La machine, elle, répond :
>
> ```bash
> sudo semanage port -a -t ssh_port_t -p tcp 3306
> ```
>
> ```text
> Port tcp/3306 already defined, modifying instead
> ```
>
> avec un code retour `0`. `semanage` bascule tout seul en modification
> (`policycoreutils-python-utils-3.10-1.el10`, `libsemanage-3.10-1.el10`). Le
> résultat est un port qui apparaît sous **deux** types, l'entrée de base et la
> vôtre :
>
> ```text
> mysqld_port_t                  tcp      1186, 3306, 63132-63164
> ssh_port_t                     tcp      3306, 2222, 22
> ```
>
> Utilisez `-m` quand même : c'est explicite, ça marche sur les versions plus
> anciennes qui refusent `-a`, et c'est ce qu'attend un correcteur d'examen.

On retire un ajout local avec `-d`, sans préciser le type :

```bash
sudo semanage port -d -p tcp 3306
sudo semanage port -l -C
```

```text
SELinux Port Type              Proto    Port Number

ssh_port_t                     tcp      2222
```

Seule l'entrée locale a disparu ; `mysqld_port_t` garde ses ports d'origine,
qui viennent de la politique de base et ne sont pas les vôtres à supprimer.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Le mode retombe en `permissive` après un reboot | `setenforce 1` seul ; la ligne `SELINUX=` de `/etc/selinux/config` n'a pas été modifiée |
| `SELINUX=` semble ignoré | espace autour du `=` dans `/etc/selinux/config` |
| Le contexte d'un fichier revient à l'ancien après un `restorecon` | il a été posé par `chcon` ; il faut une règle `semanage fcontext` |
| `semanage fcontext -a` passé, mais le fichier n'a pas changé | il manque le `restorecon -Rv` qui applique la règle |
| Le répertoire est bon, les fichiers dedans non | l'expression de chemin oublie `(/.*)?` |
| Un fichier arrivé par `mv` a le mauvais type | `mv` conserve le contexte ; relancer `restorecon` |
| Un booléen actif retombe au reboot | `setsebool` sans `-P` ; `semanage boolean -l` affiche alors `(on, off)` |
| Le service refuse de démarrer sur un port non standard | le port n'est pas déclaré dans le type attendu par le domaine |
| `semanage: command not found` | le paquet `policycoreutils-python-utils` n'est pas installé |

Quand un accès est refusé sans explication, les refus sont journalisés même en
`permissive` :

```bash
sudo ausearch -m avc --success no
sudo ausearch -m avc --success no | audit2why
```

`audit2why` traduit le refus et signale souvent qu'un simple booléen suffirait.
Générer un module avec `audit2allow` est le **dernier** recours, après avoir
essayé de corriger l'étiquette puis de basculer un booléen : un module écrit à
l'aveugle peut autoriser un domaine confiné à écrire dans des types système, et
masque le plus souvent un mauvais étiquetage qu'un `restorecon` aurait réglé.

### Tout défaire

```bash
sudo semanage port -d -p tcp 2222
sudo setsebool -P samba_export_all_ro off
sudo semanage fcontext -d "/opt/partage-demo(/.*)?"
sudo restorecon -Rv /opt/partage-demo
sudo rm -rf /opt/partage-demo
sudo setenforce 1
```

L'ordre compte : `semanage fcontext -d` retire la règle, mais les fichiers
gardent leur étiquette tant qu'on n'a pas relancé `restorecon`. C'est la même
mécanique qu'à l'aller, dans l'autre sens.

```text
Relabeled /opt/partage-demo from system_u:object_r:samba_share_t:s0 to system_u:object_r:usr_t:s0
Relabeled /opt/partage-demo/memo.txt from system_u:object_r:samba_share_t:s0 to system_u:object_r:usr_t:s0
```

Vérifiez que vous êtes bien revenu à zéro : les trois listes de customisations
locales doivent être vides, et le mode strict actif.

```bash
sudo semanage fcontext -l -C
sudo semanage boolean -l -C
sudo semanage port -l -C
getenforce
```

> **`setsebool -P <nom> off` ne supprime pas la customisation, il en écrit une
> nouvelle.** Après le `off`, `semanage boolean -l -C` liste toujours le booléen,
> en `(off, off)`. Et contrairement à `semanage port` et `semanage fcontext`,
> `semanage boolean` **n'a pas d'option `-d`** : la commande le dit elle-même,
> `error: one of the arguments -m/--modify -l/--list -E/--extract -D/--deleteall
> is required`. Pour effacer réellement l'entrée, il faut `semanage boolean -D`,
> qui supprime **toutes** les customisations de booléens de la machine, pas
> seulement la vôtre. À réserver à une machine d'atelier.
