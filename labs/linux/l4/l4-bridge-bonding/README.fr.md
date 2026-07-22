# Lab — agrégation bond + bridge avec nmcli

## Rappel

[**Bond & bridge sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/)

Un **bond** agrège plusieurs liens en une seule interface logique, pour la
redondance ou le débit ; un **bridge** est un commutateur logiciel qui met
plusieurs interfaces sur le même segment L2. Les deux se combinent : le bond en
bas, le pont par-dessus. `nmcli con add type bond|dummy|bridge`, l'option
`bond.options` et le couple contrôleur/port câblent le tout, et chaque profil de
connexion persiste au reboot. `/proc/net/bonding/<bond>` et
`/sys/class/net/<pont>/brif/` montrent le résultat côté noyau. Travaille sur les
interfaces dédiées indiquées par l'énoncé, jamais sur l'interface de gestion.

## Le cours

Les exemples ci-dessous montent une agrégation `agg0` sur deux liens d'essai
`demo0` et `demo1`, sous un pont `pont0`, avec `miimon=200` et l'adresse
`192.0.2.10/24` : le challenge vous demandera d'autres noms et d'autres valeurs.
Le but est d'apprendre la méthode, pas de recopier une ligne. Les sorties
viennent d'une VM AlmaLinux 10.2 (noyau 6.12) avec `nmcli` 1.56 ; `192.0.2.0/24`
est un préfixe réservé à la documentation, aucune machine réelle ne le porte.

### Repérer d'abord la carte qui porte votre session

Le guide ouvre sur cet avertissement : agréger l'interface par laquelle vous êtes
connecté coupe votre propre session, sans retour possible.

```bash
ip route get 1.1.1.1
nmcli -t -f NAME,DEVICE,TYPE con show --active
```

```text
1.1.1.1 via 10.10.30.1 dev eth0 src 10.10.30.14 uid 1001
cloud-init eth0:eth0:802-3-ethernet
```

La route par défaut sort par `eth0`, piloté par le profil `cloud-init eth0` :
**ni cette carte ni ce profil ne doivent apparaître dans une commande de ce
cours**.

### Un pont et une agrégation répondent à deux besoins opposés

On les confond parce qu'ils se ressemblent en ligne de commande. Le guide les
distingue par le sens dans lequel ils travaillent :

- une **agrégation** (bond) fusionne plusieurs liens physiques en une interface
  unique, pour la **redondance** (un câble tombe, l'autre prend le relais) ou le
  **débit**. Elle regarde **vers le bas**, côté matériel ;
- un **pont** (bridge) est un **commutateur logiciel** qui place plusieurs
  interfaces sur un même segment, pour donner un accès réseau à des **machines
  virtuelles** ou à des conteneurs. Il regarde **vers le haut**, côté machines.

Les deux se combinent : c'est l'architecture classique d'un hôte de
virtualisation. Le **mode** décide ensuite de la façon dont les liens coopèrent,
et la colonne de droite est la seule qui compte en exploitation :

| Mode | Comportement | Contrainte côté commutateur |
|---|---|---|
| `active-backup` (1) | un lien actif, l'autre en secours | **aucune** |
| `balance-rr` (0) | répartition paquet par paquet | aucune, mais risque de déséquencement |
| `802.3ad` (4, LACP) | les liens s'additionnent, négociés en LACP | **port-channel LACP configuré en face** |

### Fabriquer deux liens d'essai et les agréger

Une interface de type `dummy` est une carte purement logicielle que le noyau crée
à la demande. Elle s'enrôle dans une agrégation exactement comme une vraie carte,
ce qui permet de tout démontrer sans toucher au lien de gestion. On commence
volontairement en `balance-rr`, on changera de mode ensuite :

```bash
sudo nmcli con add type bond ifname agg0 con-name demo-agg \
  bond.options "mode=balance-rr,miimon=200" ipv4.method disabled ipv6.method disabled
sudo nmcli con add type dummy ifname demo0 con-name port-a controller demo-agg port-type bond
sudo nmcli con add type dummy ifname demo1 con-name port-b controller demo-agg port-type bond
ip -br link
```

```text
Connection 'demo-agg' (7937f0c0-22bd-49f0-8081-bbf9f68a8395) successfully added.
[... deux lignes identiques pour port-a et port-b ...]
agg0     UP        e6:20:b2:04:08:1d <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP>
demo0    UNKNOWN   e6:20:b2:04:08:1d <BROADCAST,NOARP,SLAVE,UP,LOWER_UP>
demo1    UNKNOWN   e6:20:b2:04:08:1d <BROADCAST,NOARP,SLAVE,UP,LOWER_UP>
```

Les trois interfaces partagent **la même adresse MAC**, celle de l'agrégation :
vue de l'extérieur, il n'y a qu'une carte. Avec les marqueurs `MASTER` et
`SLAVE`, c'est le signe que l'enrôlement a réussi. L'état réel vit dans un
fichier du noyau :

```bash
cat /proc/net/bonding/agg0
```

```text
Bonding Mode: load balancing (round-robin)
MII Status: up
MII Polling Interval (ms): 200
[...]
Slave Interface: demo0
MII Status: up
Link Failure Count: 0
[... même bloc pour demo1 ...]
```

Ce fichier est la **source de vérité** : mode effectif, intervalle de sonde,
liste des liens et santé de chacun. `miimon` demande au noyau de contrôler l'état
des liens toutes les 200 ms ; sans lui, aucune bascule automatique. Passons en
`active-backup`, avec un lien préféré :

```bash
sudo nmcli con mod demo-agg bond.options "mode=active-backup,miimon=200,primary=demo0"
grep "Bonding Mode" /proc/net/bonding/agg0     # => load balancing (round-robin)
```

Le profil sur disque dit bien `mode=active-backup`, le noyau tourne toujours en
round-robin : `nmcli con mod` **écrit** la configuration, il ne l'applique pas.
Il faut réactiver, et réactiver aussi les ports, que la réactivation du
contrôleur détache :

```bash
sudo nmcli con up demo-agg
sudo nmcli con up port-a && sudo nmcli con up port-b
cat /proc/net/bonding/agg0
```

```text
Connection successfully activated (controller waiting for ports) [...]

Bonding Mode: fault-tolerance (active-backup)
Primary Slave: demo0 (primary_reselect always)
Currently Active Slave: demo0
MII Status: up
[...]
Slave Interface: demo0
MII Status: up
[... idem demo1 ...]
```

Le message `controller waiting for ports` dit exactement ce qui se passe : le
contrôleur est monté, il attend ses ports. Une agrégation dont tous les ports
sont tombés reste dans cet état, avec `Currently Active Slave: None`.

### Prouver la bascule, et ce que donne LACP sans commutateur

Une agrégation qui n'a jamais basculé sous vos yeux reste une promesse :

```bash
sudo ip link set demo0 down
grep -E "Currently Active|Slave Interface|MII Status|Link Failure" /proc/net/bonding/agg0
ip -br link show agg0
```

```text
Currently Active Slave: demo1
MII Status: up
Slave Interface: demo0
MII Status: down
Link Failure Count: 1
Slave Interface: demo1
MII Status: up
Link Failure Count: 0
agg0    UP    6e:5b:a7:b8:ac:a2 <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP>
```

Trois choses à lire. Le lien actif est devenu `demo1`. Le compteur
`Link Failure Count` de `demo0` est passé à **1** et il ne redescendra pas : cet
historique des pannes vous dit qu'un lien a lâché même si tout va bien au moment
où vous regardez. Et surtout, **l'agrégation reste `UP`** : pour les couches
supérieures, il ne s'est rien passé. On remet le lien :

```bash
sudo ip link set demo0 up
grep -E "Currently Active|Link Failure Count" /proc/net/bonding/agg0
```

```text
Currently Active Slave: demo0
Link Failure Count: 1
Link Failure Count: 0
```

`demo0` a **repris la main** tout seul, parce qu'il est déclaré `primary`. Sans
ce paramètre, l'agrégation serait restée sur `demo1`.

Même manipulation en `802.3ad` (`bond.options "mode=802.3ad,miimon=200"`, puis
réactivation du contrôleur et des ports) : `/proc/net/bonding/agg0` annonce bien
`IEEE 802.3ad Dynamic link aggregation`, mais les deux liens passent
`MII Status: down` et chacun se retrouve dans un **agrégateur différent**
(`Aggregator ID: 2` et `Aggregator ID: 3`). Rien n'est agrégé, faute de
port-channel LACP configuré sur le commutateur en face : c'est exactement la
contrainte annoncée par le tableau des modes. Détail perfide, l'agrégation
elle-même continue d'afficher `MII Status: up` ; ne vous fiez jamais à cette
seule ligne, descendez toujours jusqu'aux ports. On revient en `active-backup`
avant la suite.

### Poser un pont par-dessus : l'adresse change de porteur

Donnons d'abord une adresse à l'agrégation, puis créons le pont, dont les
paramètres par défaut méritent un regard :

```bash
sudo nmcli con add type bridge ifname pont0 con-name demo-pont ipv4.method disabled ipv6.method disabled
nmcli -f bridge.stp,bridge.forward-delay,bridge.priority con show demo-pont
cat /sys/class/net/pont0/bridge/forward_delay
```

```text
bridge.stp:                             yes
bridge.forward-delay:                   15
bridge.priority:                        32768
1500
```

`stp` est **activé par défaut** : le pont participe au *Spanning Tree Protocol*,
qui détecte les boucles réseau. `forward-delay` vaut 15 secondes côté `nmcli` et
`1500` côté noyau, qui compte en centièmes de seconde : même valeur, deux unités.
Enrôlons l'agrégation :

```bash
ip -br addr show agg0
sudo nmcli con mod demo-agg controller demo-pont port-type bridge
sudo nmcli con up demo-agg && sudo nmcli con up port-a && sudo nmcli con up port-b
ip -br addr show agg0
nmcli -f ipv4.method,ipv4.addresses con show demo-agg
```

```text
agg0    UP    192.0.2.10/24
agg0    UP
```

L'adresse a **disparu**, et la dernière commande n'affiche rien du tout : quand
une connexion devient port d'un pont, NetworkManager ne lui laisse plus aucun
réglage IPv4. Le fichier sur disque le confirme, sa section `[ipv4]` a été
remplacée par une section `[bridge-port]` vide, sous un en-tête devenu
`port-type=bridge`. C'est la surprise classique du sujet : **un port n'a pas
d'adresse, c'est le pont qui la porte**. Sur une vraie carte, l'adresse de
production doit donc être déplacée sur le pont dans le même mouvement, sous peine
de coupure.

```bash
sudo nmcli con mod demo-pont ipv4.method manual ipv4.addresses 192.0.2.10/24
sudo nmcli con up demo-pont
ip -br addr show pont0
bridge link show
```

```text
pont0    DOWN    192.0.2.10/24
14: agg0: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 master pont0 state listening priority 32 cost 100
```

Le pont a l'adresse mais il est **`DOWN`**, et son port est en `listening`. Rien
n'est cassé : c'est le STP qui fait son travail. En sondant toutes les cinq
secondes, on voit la séquence complète :

```text
  5s  port: learning     pont0  DOWN  <NO-CARRIER,BROADCAST,MULTICAST,UP>
 15s  port: learning     pont0  DOWN  <NO-CARRIER,BROADCAST,MULTICAST,UP>
 20s  port: forwarding   pont0  UP    <BROADCAST,MULTICAST,UP,LOWER_UP>
```

Un port de pont traverse `listening` puis `learning`, chacun d'une durée de
`forward-delay`, avant de passer en `forwarding`. **Environ trente secondes de
silence** pendant lesquelles le pont ne passe aucun trafic. C'est la cause
numéro un des « ça ne marche pas » sur ce sujet : on teste trop tôt. On peut s'en
affranchir quand aucune boucle n'est possible, avec
`sudo nmcli con mod demo-pont bridge.stp no` suivi de la réactivation du pont,
du contrôleur et des ports : `bridge link show` affiche alors
`state forwarding` **immédiatement**, et `pont0` monte dans la foulée. Le prix à
payer est réel : sans STP, deux chemins entre les mêmes commutateurs produisent
une tempête de diffusion qui sature le segment. Sur un hôte de virtualisation
dont le pont n'a qu'un seul lien vers l'extérieur, la boucle est impossible et
couper STP est courant ; ailleurs, laissez-le. Contrôle final de l'empilement :
`ls /sys/class/net/pont0/brif/` liste `agg0`, et dans `ip -br link` les quatre
interfaces partagent la même adresse MAC.

### `master`/`slave` ou `controller`/`port` : le vocabulaire a changé

Beaucoup de guides encore en ligne écrivent `master <bond> slave-type bond`, et
c'est une vraie source de confusion. Sur `nmcli` 1.56, les deux vocabulaires
fonctionnent et interrogent **la même propriété** :

```bash
nmcli -f connection.master,connection.slave-type,connection.controller,connection.port-type con show port-a
```

```text
connection.master:                      7937f0c0-22bd-49f0-8081-bbf9f68a8395
connection.slave-type:                  bond
connection.controller:                  7937f0c0-22bd-49f0-8081-bbf9f68a8395
connection.port-type:                   bond
```

Deux détails utiles. La valeur rendue est l'**UUID** du contrôleur, pas son nom,
même si vous l'avez désigné par son nom à la création. Et quel que soit le
mot-clé employé, le fichier écrit sur disque emploie **toujours** la forme
moderne, `controller=` et `port-type=`. Le manuel confirme le sens de
l'évolution : `man nmcli | grep -i "deprecated for ethernet"` renvoie
`bond-slave (deprecated for ethernet with controller)` et sa jumelle pour
`bridge-slave`. En sens inverse, tout ce qui vient du noyau reste à l'ancien
vocabulaire :
`/proc/net/bonding/` écrit `Slave Interface`, `ip -br link` affiche les
marqueurs `MASTER` et `SLAVE`, et `bridge link show` dit `master pont0`. Retenez
la règle : **`nmcli` parle moderne, le noyau parle ancien**, et les deux
désignent la même chose.

### Défaire, et dépanner

Une seule commande retire les quatre profils, leurs fichiers et leurs interfaces :

```bash
sudo nmcli con delete demo-pont demo-agg port-a port-b
nmcli con show ; ip -br link ; ls /proc/net/bonding
```

```text
Connection 'demo-pont' (8da45496-...) successfully deleted.
[... trois lignes identiques ...]
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
lo               5a266d1c-6574-4c58-9d79-067b8f446d10  loopback  lo
eth0     UP        52:54:00:cd:00:13 <BROADCAST,MULTICAST,UP,LOWER_UP>
ls: cannot access '/proc/net/bonding': No such file or directory
```

La suppression est **asynchrone** : juste après la commande, `ip -br link`
montrait encore `agg0`, `demo0` et `demo1` détachés avec de nouvelles adresses
MAC, et `nmcli con show` listait toujours les profils avec un `--` en colonne
`DEVICE`. Quelques secondes plus tard tout avait disparu, `/proc/net/bonding`
compris, puisqu'il n'existe que tant qu'une agrégation existe. Vérifiez sur les
trois plans : profils, interfaces, fichiers.

| Symptôme | Cause probable | Correction |
|---|---|---|
| Le mode du profil ne correspond pas à `/proc/net/bonding` | `con mod` écrit, n'applique pas | réactiver le contrôleur **puis** chaque port |
| `Currently Active Slave: None`, `MII Status: down` | ports non remontés après la réactivation | `nmcli con up <port>` pour chacun |
| Les ports restent `MII Status: down` en `802.3ad` | aucun LACP en face | passer en `active-backup`, ou configurer le port-channel |
| Aucune bascule quand un lien tombe | `miimon` absent des `bond.options` | ajouter `miimon=<ms>` |
| Le lien préféré ne reprend pas la main | pas de `primary=` | l'ajouter aux `bond.options` |
| Le pont reste `DOWN` avec `NO-CARRIER` | port en `listening`/`learning`, STP en cours | attendre deux fois `forward-delay`, ou `bridge.stp no` |
| L'interface enrôlée a perdu son adresse | comportement normal | poser l'adresse sur le pont |
| Rien ne s'explique | le journal donne la raison exacte | `sudo journalctl -u NetworkManager -b --no-pager \| tail -50` |

Dernier réflexe : avant de valider, relisez `/proc/net/bonding/<bond>` et
`/sys/class/net/<pont>/brif/`. Ce sont les deux seuls endroits où l'état est
celui du noyau, et non celui de votre intention.
