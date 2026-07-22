# Lab — montage NFS persistant

## Rappel

[**NFS sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/stockage/nfs/)

Un serveur exporte un répertoire via `/etc/exports` ; un client le monte avec
`mount -t nfs <serveur>:/chemin <point-de-montage>`. Un montage posé à la main
disparaît au redémarrage : la persistance passe par une ligne dans
`/etc/fstab`. Le paquet `nfs-utils` fournit le client sur les distributions de
la famille RHEL ; `showmount -e <serveur>` liste les exports d'un serveur.

## Le cours

Les exemples ci-dessous travaillent sur un partage `/srv/partage-demo` monté
sur `/mnt/depot` : le challenge, lui, vous demandera un autre export, un autre
point de montage et un autre fichier à lire. Le but est d'apprendre la méthode,
pas de recopier une ligne.

Toutes les sorties reproduites ici viennent d'une machine AlmaLinux 10.2
(noyau 6.12), avec `nfs-utils` 2.8.3, SELinux en `Enforcing` et `firewalld`
actif.

### Le décor : serveur et client sur la même machine

Pour apprendre, on n'a pas besoin de deux machines. On monte un petit serveur
NFS et on s'y connecte par `127.0.0.1`. Côté serveur :

```bash
sudo mkdir -p /srv/partage-demo /srv/archives-demo
echo "inventaire du depot" | sudo tee /srv/partage-demo/bienvenue.txt
echo "note archivee"       | sudo tee /srv/archives-demo/lisez-moi.txt
sudo chown -R nobody:nobody /srv/partage-demo /srv/archives-demo
```

```text title="/etc/exports"
/srv/partage-demo  127.0.0.0/8(rw,sync,no_subtree_check)
/srv/archives-demo 127.0.0.0/8(ro,sync,no_subtree_check)
```

```bash
sudo systemctl enable --now nfs-server
systemctl status nfs-server
```

```text
     Active: active (exited) since Wed 2026-07-22 14:36:32 UTC; 7s ago
```

`active (exited)` n'est pas une panne : le serveur NFS tourne dans des threads
noyau, l'unité systemd ne fait que les amorcer, puis se termine.

> **Un montage sur soi-même passe-t-il vraiment par le réseau ?** Oui. Une fois
> le partage monté, `ss` montre une connexion TCP établie sur le port 2049,
> comme pour un serveur distant :
>
> ```bash
> ss -tn state established '( sport = :2049 or dport = :2049 )'
> ```
>
> ```text
> Recv-Q Send-Q Local Address:Port Peer Address:Port
> 0      0          127.0.0.1:967     127.0.0.1:2049
> 0      0          127.0.0.1:2049    127.0.0.1:967
> ```
>
> Le noyau ne court-circuite pas la pile réseau : les options, les versions et
> les comportements de coupure observés plus bas sont ceux d'un vrai montage
> NFS. Seule la latence est irréaliste.

### Voir ce que le serveur expose

Deux points de vue, à ne pas confondre. Côté **serveur**, `exportfs -v` montre
la configuration effective, options par défaut comprises :

```bash
sudo exportfs -ra     # relit /etc/exports et applique
sudo exportfs -v
```

```text
/srv/partage-demo
		127.0.0.0/8(sync,wdelay,hide,no_subtree_check,sec=sys,rw,secure,root_squash,no_all_squash)
/srv/archives-demo
		127.0.0.0/8(sync,wdelay,hide,no_subtree_check,sec=sys,ro,secure,root_squash,no_all_squash)
```

Trois options n'ont jamais été écrites et sont pourtant là : `sec=sys`,
`root_squash` et `secure`. Ce sont les défauts, et ils comptent (voir plus
bas).

Côté **client**, `showmount -e` interroge le serveur par le réseau :

```bash
showmount -e 127.0.0.1
```

```text
Export list for 127.0.0.1:
/srv/archives-demo 127.0.0.0/8
/srv/partage-demo  127.0.0.0/8
```

C'est la première commande à lancer quand un montage échoue : si `showmount`
ne répond pas, le problème est côté serveur ou réseau, inutile de chercher
dans `fstab`.

### Monter à la main

```bash
sudo mkdir -p /mnt/depot
sudo mount -t nfs 127.0.0.1:/srv/partage-demo /mnt/depot
findmnt /mnt/depot
```

```text
TARGET     SOURCE                      FSTYPE OPTIONS
/mnt/depot 127.0.0.1:/srv/partage-demo nfs4   rw,relatime,vers=4.2,rsize=131072,wsize=131072,namlen=255,hard,fatal_neterrors=none,proto=tcp,timeo=600,retrans=2,sec=sys,clientaddr=127.0.0.1,local_lock=none,addr=127.0.0.1
```

Trois choses à lire dans cette ligne :

- on a demandé `-t nfs`, le noyau répond **`nfs4`** avec **`vers=4.2`** : la
  version la plus haute commune au client et au serveur a été négociée
  automatiquement ;
- `proto=tcp` et le port 2049 suffisent en NFSv4, il n'y a plus de démons
  auxiliaires à ouvrir ;
- `hard`, `timeo=600`, `retrans=2` sont les défauts de comportement en cas de
  coupure. Ils font l'objet d'une section entière plus bas.

`nfsstat -m` donne la même information, montage par montage, et c'est la
commande à retenir pour vérifier la **version réellement négociée** :

```bash
nfsstat -m
```

```text
/mnt/depot from 127.0.0.1:/srv/partage-demo
 Flags:	rw,relatime,vers=4.2,rsize=131072,wsize=131072,namlen=255,hard,...
```

Et le contenu servi par le serveur est là :

```bash
cat /mnt/depot/bienvenue.txt
```

```text
inventaire du depot
```

### Ce que le client demande, ce que le serveur impose

Montons le second partage, exporté en `ro`, et regardons les options côté
client :

```bash
sudo mkdir -p /mnt/archives
sudo mount -t nfs 127.0.0.1:/srv/archives-demo /mnt/archives
findmnt -no OPTIONS /mnt/archives
```

```text
rw,relatime,vers=4.2,rsize=131072,wsize=131072,namlen=255,hard,...
```

Le client affiche **`rw`**. Et pourtant :

```bash
echo test | sudo tee /mnt/archives/interdit.txt
```

```text
tee: /mnt/archives/interdit.txt: Read-only file system
```

Retenez la leçon : les options affichées par `findmnt` ou `mount` sont celles
que le **client** a demandées, pas celles que le **serveur** applique. Un
partage en `ro` refuse l'écriture même si le montage se dit `rw`. Pour
connaître la vérité, il faut regarder `exportfs -v` sur le serveur.

Deuxième surprise, sur le partage en lecture-écriture cette fois :

```bash
echo "ligne ajoutee depuis le client" | sudo tee /mnt/depot/essai.txt
ls -l /mnt/depot
```

```text
total 8
-rw-r--r--. 1 nobody nobody 20 Jul 22 14:36 bienvenue.txt
-rw-r--r--. 1 nobody nobody 31 Jul 22 14:36 essai.txt
```

Le fichier a été créé par `root` via `sudo`, il appartient à `nobody`. C'est
`root_squash`, actif par défaut : le serveur remplace l'UID 0 du client par
l'utilisateur anonyme. NFS raisonne en **UID et GID numériques** ; ce que le
client croit être son identité n'engage pas le serveur.

### `hard` ou `soft` : ce qui se passe quand le serveur disparaît

C'est le point le plus mal compris de NFS, et le plus facile à vérifier : il
suffit d'arrêter le service pendant qu'un montage est actif.

#### Le défaut, `hard` : on attend, indéfiniment

```bash
sudo mount -t nfs -o hard,timeo=30,retrans=2,actimeo=0 \
  127.0.0.1:/srv/partage-demo /mnt/depot
sudo systemctl stop nfs-server
```

Un lecteur est lancé en arrière-plan, et 20 secondes plus tard il n'a toujours
rien produit :

```text
  PID STAT CMD
18530 D    cat /mnt/depot/bienvenue.txt
```

L'état **`D`** est le *uninterruptible sleep* : le processus dort dans le
noyau, en attente d'une réponse qui ne vient pas. Il n'a rien affiché, rien
échoué, il attend. On relance le serveur :

```bash
sudo systemctl start nfs-server
```

```text
14:38:17      <- debut de la lecture
inventaire du depot
rc=0
14:38:38      <- fin, 21 secondes plus tard
```

La lecture s'est terminée **normalement**, avec le bon contenu et un code de
retour 0. C'est exactement ce qu'on attend d'un `hard` : aucune donnée perdue,
aucune erreur remontée à l'application, au prix d'une attente sans limite.

> **Un `hard` bloqué gèle tout ce qui touche au montage.** Pendant l'attente,
> `df`, `ls`, un `umount` et même une complétion de shell qui parcourt le
> point de montage se figent à leur tour. Sur un serveur de production, une
> seule ligne NFS injoignable peut ainsi paralyser des services qui ne
> l'utilisent pas directement.

Comment se dégager quand on ne peut pas relancer le serveur ? Deux recours,
essayés serveur arrêté avec un lecteur encore actif sur le montage. `umount -f`
échoue immédiatement, parce qu'un processus tient toujours le point de
montage :

```bash
sudo umount -f /mnt/depot
```

```text
umount.nfs4: /mnt/depot: device is busy
```

```text
real	0m0.019s      (code de retour 16)
```

`umount -l` (*lazy*), lui, détache le point de montage de l'arborescence sans
attendre les processus, et rend la main après 18 secondes :

```bash
sudo umount -l /mnt/depot
```

```text
real	0m18.077s     (code de retour 0)
```

Retenez l'ordre : relancer le serveur si c'est possible, sinon `umount -f`,
puis `umount -l` en dernier recours. `-l` masque le problème sans le résoudre :
les processus bloqués le restent.

#### Écart entre le guide et la machine : `kill -9` fonctionne

Le guide compagnon affirme qu'un processus bloqué en `D` sur un montage `hard`
ne peut pas être tué, que « `kill -9` n'a aucun effet ». Sur cette machine, ce
n'est pas ce qui se produit :

```bash
sudo kill -9 18756
```

```text
processus disparu apres 1s
```

Testé deux fois, même résultat : le processus meurt en une seconde environ,
sans avoir rien affiché. Les attentes RPC du client NFS moderne sont
*killable* : un signal fatal les interrompt. Ce n'est pas le cas de toutes les
opérations ni de tous les noyaux, et l'essai a été mené serveur arrêté sur la
boucle locale, donc avec un refus de connexion franc, pas un réseau qui avale
les paquets en silence. Conclusion prudente à retenir : `kill -9` **peut**
marcher, ne comptez pas dessus, et surtout ne l'utilisez pas comme argument
pour choisir `hard` à la légère.

#### `soft` : une erreur au bout d'un délai

```bash
sudo mount -t nfs -o soft,timeo=30,retrans=2,actimeo=0 \
  127.0.0.1:/srv/partage-demo /mnt/depot
sudo systemctl stop nfs-server
time cat /mnt/depot/bienvenue.txt
```

```text
cat: /mnt/depot/bienvenue.txt: Input/output error

real	0m18.085s
```

Cette fois, l'appel **rend la main** : une erreur d'entrée-sortie après 18
secondes. Notez l'écart avec le calcul naïf : `timeo=30` vaut 3 secondes
(l'unité est le **dixième** de seconde) et `retrans=2` annonce deux
retransmissions, ce qui ferait 9 secondes. Le client NFSv4 applique sa propre
logique de reprise par-dessus ces valeurs. Mesurez, ne déduisez pas.

Le démontage aussi finit par passer, avec le même délai :

```bash
time sudo umount /mnt/depot
```

```text
real	0m18.130s
```

#### Lequel choisir

| Option | Comportement si le serveur tombe | Usage |
|---|---|---|
| `hard` (défaut) | attente illimitée, reprise intacte au retour | tout ce qui écrit, production |
| `soft` | erreur d'entrée-sortie après expiration | lecture non critique, scripts qui doivent rendre la main |
| `timeo=n` | délai avant retransmission, en **dixièmes de seconde** | ajuster plutôt que passer à `soft` |
| `retrans=n` | nombre de retransmissions avant abandon ou avertissement | idem |

Le guide est net sur le sujet et le manuel `nfs(5)` le confirme : `soft`
expose à une **corruption silencieuse**, une écriture pouvant échouer alors que
l'application la croit réussie. Gardez `hard`, et si l'attente vous inquiète,
jouez sur `timeo` et `retrans`. Pendant vos essais de coupure, en revanche,
`soft` vous évite de rester coincé sans pouvoir nettoyer.

### Rendre le montage persistant

Un `mount` posé à la main ne survit pas au redémarrage. La ligne `/etc/fstab`
suit la même grammaire que pour un disque local, à ceci près que le premier
champ est une ressource distante :

```text title="/etc/fstab"
127.0.0.1:/srv/partage-demo /mnt/depot nfs _netdev,nofail,defaults 0 0
```

Les six champs : la source `<serveur>:/<chemin exporté>`, le point de montage,
le type, les options, puis `0 0` pour dump et fsck (un partage réseau ne se
sauvegarde ni ne se vérifie localement).

**Sauvegardez avant d'éditer.** Une erreur dans `fstab` se paie au démarrage
suivant :

```bash
sudo cp -a /etc/fstab /root/fstab.bak
```

Puis, dans l'ordre :

```bash
sudo systemctl daemon-reload   # systemd relit fstab
sudo findmnt --verify          # controle syntaxique
sudo mount -a                  # applique sans redemarrer
findmnt -no SOURCE,TARGET,FSTYPE /mnt/depot
```

```text
127.0.0.1:/srv/partage-demo /mnt/depot nfs4
```

`mount -a` est rejouable : lancé une seconde fois alors que le partage est déjà
monté, il ne fait rien et rend 0.

Si vous oubliez le `daemon-reload`, `findmnt --verify` vous le rappelle :

```text
0 parse errors   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload
, 0 errors, 1 warning
```

> **`findmnt --verify` avertit, il ne tranche pas.** Avec un type mal
> orthographié (`nsf` au lieu de `nfs`), il signale bien
> `[W] nsf seems unsupported by the current kernel`, mais **sort quand même
> avec le code 0**. C'est `mount -a` qui échoue, lui, avec
> `mount: /mnt/depot: unknown filesystem type 'nsf'.` et un code 32. Utilisez
> les deux : `findmnt --verify` pour lire les avertissements, `mount -a` pour
> la preuve.

### `_netdev` et `nofail` : ce qu'ils font vraiment

Ces deux options existent pour une raison simple : au démarrage, une ligne NFS
est un point de montage qui dépend d'une machine tierce.

**Ce que coûte un serveur injoignable**, mesuré à la main :

```bash
time sudo mount -t nfs 192.0.2.1:/srv/partage-demo /mnt/injoignable
```

```text
mount.nfs: Connection timed out for 192.0.2.1:/srv/partage-demo on /mnt/injoignable

real	3m2.042s
```

Trois minutes avant d'abandonner. Le manuel `nfs(5)` annonce un défaut de
`retry=2` (deux minutes) pour un montage au premier plan ; l'attente réelle
mesurée est plus longue, parce que la dernière tentative épuise son propre
délai après la fin de la fenêtre. Avec `retry=0`, la même commande rend la main
en 9 secondes.

**`_netdev` classe le montage comme réseau.** Le manuel `systemd.mount(5)`,
sur la machine, est explicite :

```text
_netdev
    Normally the file system type is used to determine if a mount is a
    "network mount", i.e. if it should only be started after the network is
    available. Using this option overrides this detection and specifies that
    the mount requires network.

    Network mount units are ordered between remote-fs-pre.target and
    remote-fs.target, instead of local-fs-pre.target and local-fs.target.
    They also pull in network-online.target and are ordered after it and
    network.target.
```

On peut le vérifier sans redémarrer, en lisant l'unité que systemd fabrique à
partir de `fstab` :

```bash
sudo systemctl daemon-reload
systemctl show mnt-depot.mount -p After -p Wants
```

```text
Wants=network-online.target
After=network.target -.mount system.slice remote-fs-pre.target nfs-server.service network-online.target systemd-journald.socket
```

> **Écart avec le guide.** Le guide présente `_netdev` comme indispensable,
> faute de quoi « le démarrage peut rester bloqué ». Sur cette machine, la même
> ligne **sans** `_netdev` produit exactement les mêmes dépendances :
> `Wants=network-online.target`, ordonnancement après `network-online.target`
> et avant `remote-fs.target`. C'est cohérent avec le manuel cité ci-dessus :
> pour un type **connu comme réseau**, la détection automatique suffit et
> `_netdev` ne fait que la confirmer. L'option reste utile, et attendue en
> examen : elle est obligatoire pour un système de fichiers **local posé sur un
> transport réseau** (un `ext4` sur un volume iSCSI, que systemd ne peut pas
> deviner), et elle documente l'intention. Écrivez-la, en sachant maintenant ce
> qu'elle change et ce qu'elle ne change pas.

**`nofail` décide si l'échec est fatal.** C'est elle, et non `_netdev`, qui
change quelque chose au démarrage, et la différence se lit dans les dépendances
de `remote-fs.target`. Sans `nofail` :

```text
Requires=mnt-injoignable.mount
```

Avec `nofail` :

```text
Requires=
Wants=... mnt-injoignable.mount ...
```

Le montage passe de `Requires` à `Wants` : son échec n'entraîne plus celui de
la cible. Attention, `nofail` ne supprime pas l'**attente**, seulement son
caractère fatal. Notez d'ailleurs que systemd borne cette attente, ce que
`mount` seul ne fait pas :

```bash
systemctl show mnt-injoignable.mount -p TimeoutUSec
```

```text
TimeoutUSec=1min 30s
```

> **Ne testez jamais une ligne NFS par un redémarrage.** `mount -a` et
> `findmnt --verify` prouvent la même chose sans risque, et
> `systemctl show <unite>.mount` prouve le reste. Un redémarrage sur un `fstab`
> douteux, c'est une minute et demie d'attente par entrée injoignable, et une
> machine qui remonte dégradée si l'entrée est déclarée sans `nofail`. Rien de
> tout cela ne vous apprend quoi que ce soit que les commandes ci-dessus ne
> disent plus vite.

### L'alternative : monter à la demande

Quand le partage n'est pas nécessaire au démarrage, on peut le faire monter au
premier accès plutôt qu'au boot :

```text title="/etc/fstab"
127.0.0.1:/srv/partage-demo /mnt/depot nfs _netdev,noauto,x-systemd.automount 0 0
```

```bash
sudo systemctl daemon-reload
sudo systemctl start mnt-depot.automount
findmnt -no TARGET,FSTYPE /mnt/depot
```

```text
/mnt/depot autofs
```

Avant tout accès, le point de montage est un `autofs` : rien n'est connecté,
le démarrage n'attend personne. Au premier accès :

```bash
cat /mnt/depot/bienvenue.txt
findmnt -no SOURCE,TARGET,FSTYPE /mnt/depot
```

```text
inventaire du depot
systemd-1                   /mnt/depot autofs
127.0.0.1:/srv/partage-demo /mnt/depot nfs4
```

Le montage NFS s'est empilé sur l'`autofs`. Attention toutefois : `noauto`
signifie que rien n'est monté tant que personne ne regarde. Un contrôle qui
exige un montage **actif** après `mount -a` ne sera pas satisfait par cette
méthode.

### Quand le chemin de l'export n'est pas celui qu'on croit

Le côté serveur réserve un piège qui se manifeste côté client. Ajoutons une
racine d'export NFSv4 avec `fsid=0` :

```text title="/etc/exports"
/srv                127.0.0.0/8(rw,sync,fsid=0,crossmnt,no_subtree_check)
/srv/partage-demo   127.0.0.0/8(rw,sync,no_subtree_check)
```

Trois montages, trois résultats différents, tous mesurés :

```bash
sudo mount -t nfs  127.0.0.1:/srv/partage-demo /mnt/depot && nfsstat -m
```

```text
/mnt/depot from 127.0.0.1:/srv/partage-demo
 Flags:	rw,relatime,vers=3,...,mountvers=3,mountport=20048,mountproto=udp,...
```

Le montage a **réussi**, mais en **NFSv3**. Rien ne l'a signalé : il a fallu
lire `vers=3` dans `nfsstat -m`.

```bash
sudo mount -t nfs  127.0.0.1:/partage-demo /mnt/depot && nfsstat -m
```

```text
/mnt/depot from 127.0.0.1:/partage-demo
 Flags:	rw,relatime,vers=4.2,...
```

Avec le chemin **relatif à la racine `fsid=0`**, on obtient bien NFSv4.2.

```bash
sudo mount -t nfs4 127.0.0.1:/srv/partage-demo /mnt/depot
```

```text
mount.nfs4: mounting 127.0.0.1:/srv/partage-demo failed, reason given by server: No such file or directory
```

En forçant `nfs4` sur le chemin complet, l'échec devient explicite : pour
NFSv4, ce chemin n'existe pas, puisque tout est relatif à la racine déclarée
par `fsid=0`.

À retenir : `fsid=0` change la manière dont le **client** doit nommer l'export.
Sans `fsid=0` dans `/etc/exports` (la configuration du début de ce cours), le
chemin complet fonctionne et donne directement du NFSv4.2. Dans tous les cas,
`showmount -e` liste les chemins **système** du serveur, pas forcément ceux
qu'un client NFSv4 doit demander : vérifiez la version obtenue avec
`nfsstat -m` après chaque montage.

### Pare-feu et SELinux

Sur la machine de démonstration, le montage par la boucle locale n'a rien
demandé au pare-feu, mais la zone active ne contient pas NFS :

```bash
sudo firewall-cmd --list-services
```

```text
cockpit dhcpv6-client ssh
```

```bash
sudo firewall-cmd --info-service=nfs
```

```text
nfs
  ports: 2049/tcp
```

Pour un client **distant**, il faut donc ouvrir le service côté serveur :

```bash
sudo firewall-cmd --add-service=nfs --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-services
```

```text
cockpit dhcpv6-client nfs ssh
```

Côté client, rien à ouvrir : la connexion observée plus haut part du client
(port source 967) vers le port 2049 du serveur, c'est donc lui qui l'initie.

SELinux est resté en `Enforcing` pendant tous les essais ci-dessus sans rien
bloquer. Il peut en revanche s'interposer quand une application confinée lit un
partage NFS ; le symptôme est un `Permission denied` que les droits Unix
n'expliquent pas, et le réflexe reste `sudo ausearch -m AVC -ts recent`.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `showmount -e <serveur>` ne répond pas | service NFS arrêté, ou port 2049 filtré côté serveur |
| `mount.nfs: Connection timed out` après trois minutes | serveur injoignable ; vérifier l'adresse, la route, le pare-feu |
| `mount.nfs: access denied by server` | l'adresse du client n'est pas couverte par la ligne de `/etc/exports` |
| `mount.nfs4: ... No such file or directory` | chemin d'export erroné, ou racine `fsid=0` qui rend les chemins relatifs |
| `mount: unknown filesystem type 'nsf'` | faute de frappe sur le type dans `fstab` ; `mount -a` sort en 32 |
| Le montage fonctionne mais en `vers=3` | négociation redescendue ; le lire avec `nfsstat -m`, forcer avec `-t nfs4` ou `vers=4.2` |
| Écriture refusée alors que le client affiche `rw` | l'export est en `ro` côté serveur ; regarder `exportfs -v` |
| Les fichiers créés appartiennent à `nobody` | `root_squash` (défaut) : l'UID 0 du client est projeté sur l'anonyme |
| `df`, `ls` et `umount` figés | montage `hard` dont le serveur ne répond plus ; relancer le serveur, sinon `umount -f`, puis `umount -l` |
| `umount -f` répond `device is busy` (code 16) | un processus tient encore le point de montage ; passer à `umount -l` |
| `Input/output error` sur un partage réseau | montage `soft` qui a expiré ; le serveur ne répond pas |
| Le partage disparaît au redémarrage | pas de ligne dans `/etc/fstab` |
| `findmnt --verify` ne signale rien mais `mount -a` échoue | `--verify` n'émet que des avertissements et sort en 0 ; se fier au code de `mount -a` |
| Le démarrage attend une minute et demie | entrée NFS injoignable ; systemd borne le montage à `TimeoutUSec` (1 min 30 s par défaut) |
| `remote-fs.target` en échec après le boot | entrée NFS en échec **sans** `nofail` : la cible la déclare en `Requires` |
| `fstab` modifié mais systemd ignore le changement | `sudo systemctl daemon-reload` oublié |
| `Stale file handle` | export modifié sans `exportfs -ra` ; réappliquer côté serveur puis remonter |

Pour tout défaire et repartir de zéro :

```bash
sudo umount /mnt/depot /mnt/archives
sudo cp -a /root/fstab.bak /etc/fstab      # restaurer la sauvegarde
sudo systemctl daemon-reload
sudo systemctl disable --now nfs-server
sudo rm -rf /srv/partage-demo /srv/archives-demo /mnt/depot /mnt/archives
sudo truncate -s 0 /etc/exports            # ou restaurer votre sauvegarde
sudo exportfs -ra
```

Vérifiez que plus rien ne traîne :

```bash
findmnt -t nfs,nfs4     # aucune sortie attendue
sudo exportfs -v        # aucune sortie attendue
```
