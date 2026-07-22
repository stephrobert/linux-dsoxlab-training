# Lab — IPv4 statique persistante avec NetworkManager

## Rappel

[**NetworkManager sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/)

Sur RHEL, `NetworkManager` pilote les interfaces. `nmcli con add` crée un profil
de connexion ; `ipv4.method manual` + `ipv4.addresses` fixe une adresse statique ;
le profil atterrit dans `/etc/NetworkManager/system-connections/` et survit donc
au reboot. `ip addr add` est volatile.

Travaille sur l'interface dédiée indiquée par l'énoncé, jamais sur l'interface de
gestion.

## Le cours

Les exemples ci-dessous travaillent sur une interface d'essai `demo0`, une
connexion nommée `demo-static` et l'adresse `198.51.100.20/24` : le challenge,
lui, vous demandera une autre interface, un autre nom de connexion et une autre
adresse. Le but est d'apprendre la méthode, pas de recopier une ligne. Les sorties
viennent d'une VM AlmaLinux 10 avec `nmcli` 1.56 ; `198.51.100.0/24` est un
préfixe réservé à la documentation, aucune machine réelle ne le porte.

### Repérer d'abord la connexion qui porte votre session

C'est la première commande à taper sur une machine distante, avant toute
modification. Elle vous dit par quelle interface passe votre trafic, donc laquelle
ne jamais toucher :

```bash
ip route get 1.1.1.1
nmcli -t -f NAME,DEVICE,STATE con show --active
```

```text
1.1.1.1 via 10.10.30.1 dev eth0 src 10.10.30.12 uid 1001
    cache
cloud-init eth0:eth0:activated
lo:lo:activated
```

La route par défaut sort par `eth0`, et `eth0` est piloté par la connexion
nommée `cloud-init eth0`. **Ce profil est intouchable** : un `nmcli con mod`
malheureux suivi d'un `nmcli con up` vous éjecte instantanément, et le guide est
formel, aucune commande ne vous ramènera sans accès console. C'est pourquoi tout
le cours se déroule sur une interface fabriquée pour l'occasion.

### Ce que `ip addr add` ne fait pas

Fabriquons une interface d'essai de type `dummy`, une carte purement logicielle
que le noyau accepte de créer à la demande, et posons-lui une adresse à la main :

```bash
sudo ip link add demo0 type dummy
sudo ip link set demo0 up
sudo ip addr add 198.51.100.20/24 dev demo0
ip -4 addr show demo0
```

```text
5: demo0: <BROADCAST,NOARP,UP,LOWER_UP> mtu 1500 [...] state UNKNOWN
    inet 198.51.100.20/24 scope global demo0
```

L'adresse est là, la carte est `UP` : en apparence, le travail est fait. Regardons
pourtant ce que NetworkManager en pense :

```bash
nmcli device status
nmcli -f NAME,FILENAME con show
```

```text
DEVICE  TYPE      STATE                    CONNECTION
demo0   dummy     connecting (externally)  demo0
NAME             FILENAME
cloud-init eth0  /etc/NetworkManager/system-connections/cloud-init-eth0.nmconnection
demo0            /run/NetworkManager/system-connections/demo0.nmconnection
```

Voilà le piège, et il est plus sournois que « il ne se passe rien » : le démon a
**adopté** l'interface et lui a fabriqué une connexion du même nom. Un
`nmcli con show` trop rapide laisserait croire à un profil en bonne et due forme.
La colonne `FILENAME` tranche : ce profil vit sous **`/run`**, pas sous `/etc`.

```bash
findmnt -no TARGET,FSTYPE /run
```

```text
/run tmpfs
```

`/run` est un `tmpfs`, un système de fichiers en mémoire vive, recréé vide à
chaque démarrage. Le profil est donc perdu au reboot, exactement comme l'adresse.
**Retenez la lecture de `FILENAME`** : `/etc` veut dire persistant, `/run` veut
dire volatile. Nettoyons avec `sudo ip link del demo0`, qui fait disparaître
l'interface et la connexion `/run` d'un coup.

### Créer un profil persistant

Un profil se crée en une commande. Le mot-clé `type dummy` remplace ici le
`type ethernet` du guide, tout le reste est identique à ce qu'on écrirait pour
une vraie carte :

```bash
sudo nmcli connection add type dummy ifname demo0 con-name demo-static \
  ipv4.method manual ipv4.addresses 198.51.100.20/24 autoconnect no
```

```text
Connection 'demo-static' (ac314bb7-9bee-493d-9a47-bec7ceef5710) successfully added.
```

Chaque mot-clé porte un rôle : `ifname demo0` désigne la carte cible,
`con-name demo-static` nomme le profil (c'est ce nom que toutes les commandes
suivantes emploieront), `ipv4.method manual` dit « adresse fixe, pas de DHCP » et
`ipv4.addresses` donne l'adresse et son masque. Le guide signale un raccourci :
`ip4 198.51.100.20/24` bascule tout seul `ipv4.method` sur `manual`, la forme
explicite ci-dessus fait la même chose en le disant.

Le `autoconnect no` est volontaire, on s'en servira plus bas pour démonter le
piège du reboot. Notez aussi ce qui n'est **pas** dans la commande : ni
`ipv4.gateway`, ni `ipv4.dns`. Sur une vraie carte on les ajoute, comme le montre
le guide ; sur une interface d'essai on s'en abstient, car une passerelle installe
une route par défaut qui viendrait concurrencer celle de votre lien de gestion.

### Configuré n'est pas actif

Le profil existe. L'interface, elle, n'existe pas encore :

```bash
nmcli con show
ip -br link
```

```text
NAME             UUID                                  TYPE      DEVICE
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
demo-static      ac314bb7-9bee-493d-9a47-bec7ceef5710  dummy     --

lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
eth0             UP             52:54:00:cd:00:11 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

Aucun `demo0` dans `ip -br link` : le tiret `--` de la colonne `DEVICE` est le symptôme : profil enregistré, aucune
carte derrière. C'est la distinction fondamentale du guide, `nmcli connection`
parle des **profils**, `nmcli device` parle des **cartes**. Activons :

```bash
sudo nmcli connection up demo-static
nmcli -f GENERAL.DEVICE,GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS device show demo0
```

```text
Connection successfully activated (D-Bus active path: [...]/ActiveConnection/4)
GENERAL.DEVICE:                         demo0
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     demo-static
IP4.ADDRESS[1]:                         198.51.100.20/24
```

`GENERAL.STATE: 100 (connected)` est l'état **réel** de la carte, et
`GENERAL.CONNECTION` dit quel profil l'a produit. Les deux commandes ne répondent
pas à la même question : `con show` montre ce qui est **écrit**, `device show`
montre ce qui **tourne**.

Le classique du dépannage découle directement de là : `nmcli connection modify`
écrit dans le profil et n'applique rien à chaud.

```bash
sudo nmcli connection modify demo-static ipv4.addresses 198.51.100.21/24
nmcli -g ipv4.addresses con show demo-static      # ce qui est configuré
nmcli -g IP4.ADDRESS device show demo0            # ce qui est actif
```

```text
198.51.100.21/24
198.51.100.20/24
```

Deux valeurs différentes, aucun bug : la configuration et l'état courant sont deux
choses distinctes. On les réconcilie en réactivant le profil, et
`nmcli -g IP4.ADDRESS device show demo0` renvoie alors `198.51.100.21/24`.

```bash
sudo nmcli connection up demo-static
```

### Le fichier sur disque, et ses droits `0600`

C'est lui, et lui seul, qui fait la persistance :

```bash
sudo ls -l /etc/NetworkManager/system-connections/
sudo cat /etc/NetworkManager/system-connections/demo-static.nmconnection
```

```text
-rw-------. 1 root root 331 Jul 22 13:30 cloud-init-eth0.nmconnection
-rw-------. 1 root root 232 Jul 22 16:35 demo-static.nmconnection

[connection]
id=demo-static
uuid=ac314bb7-9bee-493d-9a47-bec7ceef5710
type=dummy
autoconnect=false
interface-name=demo0

[ipv4]
address1=198.51.100.20/24
method=manual
[...]
```

Un format INI lisible, en `0600`, propriété de `root`. Ces droits ne sont pas
décoratifs : ces fichiers contiennent les secrets (clés Wi-Fi, identifiants VPN)
en clair, et NetworkManager **refuse** de charger un fichier trop permissif.
Vérifiable en une manipulation :

```bash
sudo chmod 0644 /etc/NetworkManager/system-connections/demo-static.nmconnection
sudo nmcli connection load /etc/NetworkManager/system-connections/demo-static.nmconnection
sudo journalctl -u NetworkManager -b --no-pager | tail -2
```

```text
Could not load file '/etc/NetworkManager/system-connections/demo-static.nmconnection'
[...] settings: load: failure to load "[...]/demo-static.nmconnection": File permissions (100644) are insecure
[...] audit: op="connections-load" [...] result="fail"
```

Après un redémarrage, le verdict est sans appel : la connexion a **disparu** de
`nmcli con show` alors que le fichier est toujours sur le disque. Un `chmod 0600`
suivi d'un `nmcli connection load` la fait revenir immédiatement (et l'active
aussitôt si `autoconnect` est à `yes`).

### `autoconnect`, le vrai juge du reboot

Notre profil est parfait, sur disque, en `0600`, et il ne remontera pourtant pas.

```bash
nmcli -f connection.autoconnect con show demo-static
```

```text
connection.autoconnect:                 no
```

Preuve par le redémarrage, le seul test qui fasse foi selon le guide :

```bash
sudo systemctl reboot
```

Au retour, `nmcli con show` puis `ip -br link` donnent :

```text
demo-static      ac314bb7-9bee-493d-9a47-bec7ceef5710  dummy     --

lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
eth0             UP             52:54:00:cd:00:11 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

Le profil a survécu, l'interface non. C'est le piège exact du sujet : un fichier
sur disque ne suffit pas, encore faut-il que NetworkManager ait le droit de
l'activer tout seul. La correction tient en une ligne :

```bash
sudo nmcli connection modify demo-static connection.autoconnect yes
sudo grep -n autoconnect /etc/NetworkManager/system-connections/demo-static.nmconnection \
  || echo "(plus de ligne autoconnect)"
```

```text
(plus de ligne autoconnect)
```

Détail utile : la ligne `autoconnect=false` n'est pas passée à `true`, elle a été
**retirée**. Un keyfile n'enregistre que ce qui s'écarte du défaut, et le défaut
est `yes`. Ne concluez donc jamais de l'absence de la ligne que le réglage manque.
Second redémarrage, et cette fois :

```bash
nmcli con show --active
ip -4 -br addr show demo0
```

```text
NAME             UUID                                  TYPE      DEVICE
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
demo-static      ac314bb7-9bee-493d-9a47-bec7ceef5710  dummy     demo0

demo0            UNKNOWN        198.51.100.21/24
```

L'interface est revenue seule avec son adresse, sans qu'on tape quoi que ce soit.
Contrôlez au passage avec `ip route` que le lien de gestion n'a pas bougé :

```text
default via 10.10.30.1 dev eth0 proto dhcp src 10.10.30.12 metric 100
10.10.30.0/24 dev eth0 proto kernel scope link src 10.10.30.12 metric 100
198.51.100.0/24 dev demo0 proto kernel scope link src 198.51.100.21 metric 550
```

Une seule route par défaut, toujours par `eth0`. La route de `demo0` est de portée
`link` : elle ne concerne que son propre réseau.

### Défaire, et dépanner

Une seule commande retire le profil, le fichier et l'interface :

```bash
sudo nmcli connection delete demo-static
nmcli con show
ip -br link
sudo ls -l /etc/NetworkManager/system-connections/
```

```text
Connection 'demo-static' (ac314bb7-9bee-493d-9a47-bec7ceef5710) successfully deleted.
NAME             UUID                                  TYPE      DEVICE
cloud-init eth0  1dd9a779-d327-56e1-8454-c65e2556c12c  ethernet  eth0
lo               6205a4b0-18bc-46db-8d76-6ac467bdb9cc  loopback  lo
[... ip -br link : plus de demo0 ...]
-rw-------. 1 root root 331 Jul 22 13:30 cloud-init-eth0.nmconnection
```

Vérifiez sur les trois plans : plus de profil, plus d'interface, plus de fichier.
Comptez une seconde ou deux, `nmcli con show` peut encore afficher la connexion
juste après la commande, le temps que le démon propage l'information. Le tableau
ci-dessous récapitule les pannes rencontrées dans ce cours.

| Symptôme | Cause probable | Correction |
|---|---|---|
| `con show` donne la bonne IP, `ip addr` l'ancienne | profil modifié, jamais réactivé | `sudo nmcli con up <profil>` |
| Colonne `DEVICE` à `--` | profil enregistré mais inactif | `sudo nmcli con up <profil>` |
| L'adresse disparaît au reboot | posée avec `ip addr add`, ou `connection.autoconnect` à `no` | recréer un profil, ou `nmcli con mod <profil> connection.autoconnect yes` |
| Le profil disparaît de `con show` après reboot | fichier keyfile trop permissif, refusé au chargement | `sudo chmod 0600 <fichier>` puis `nmcli con load <fichier>` |
| `FILENAME` pointe sur `/run/...` | connexion en mémoire, adoptée d'une interface montée à la main | créer un vrai profil avec `nmcli con add` |
| L'interface reste `unmanaged` | un autre gestionnaire revendique la carte | identifier le démon actif avant de continuer |
| Rien ne s'explique | le journal donne toujours la raison exacte | `sudo journalctl -u NetworkManager -b --no-pager \| tail -50` |

Dernier réflexe, valable partout : avant de valider, relisez le **profil**, pas la
sortie de `ip addr`. C'est le profil qui sera rejoué au prochain démarrage.

```bash
nmcli -f connection.autoconnect,ipv4.method,ipv4.addresses con show <profil>
```
