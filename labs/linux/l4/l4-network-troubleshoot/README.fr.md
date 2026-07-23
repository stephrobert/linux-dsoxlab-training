# Lab — diagnostiquer une connexion réseau tombée

## Rappel

[**Le diagnostic réseau sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/)

Quand « ça ne marche pas », la question n'est pas quelle commande lancer, mais à
quelle couche se situe la panne. On remonte donc dans l'ordre : le lien,
l'adresse, la route, le nom, puis le service. Chaque étage a sa commande
(`ip link`, `ip addr`, `ip route get`, `getent hosts`, `ss -tlnp`) et son
symptôme propre. Une interface peut être entièrement configurée et pourtant
inactive : c'est l'état vivant qui fait foi, jamais le fichier de configuration.

## Le cours

Les exemples ci-dessous montent un réseau de démonstration complet dans un
espace de noms réseau, sur le sous-réseau `203.0.113.0/24`, avec un serveur HTTP
sur le port 8080 : le challenge, lui, porte sur une autre interface, d'autres
adresses et d'autres outils. Le but est d'apprendre à lire les symptômes, pas de
recopier une ligne.

Avant de diagnostiquer, sachez de quoi vous disposez. Sur la VM AlmaLinux 10 de
ce lab :

```bash
for c in ip ss ping curl getent dig nc traceroute mtr nmap; do
  printf "%-12s %s\n" "$c" "$(command -v $c || echo ABSENT)"
done
```

```text
ip           /usr/sbin/ip
ss           /usr/sbin/ss
[...]
dig          /usr/bin/dig
nc           ABSENT
traceroute   ABSENT
mtr          ABSENT
nmap         ABSENT
```

`nc`, `traceroute` et `mtr` sont **absents**, alors que le guide en ligne les
donne comme première commande de plusieurs parcours. Il faut donc savoir s'en
passer : `curl` teste un port TCP, et **bash** ouvre une socket tout seul avec
`/dev/tcp/<hôte>/<port>`. À l'inverse `ifconfig`, `netstat` et `route` sont bien
là (paquet `net-tools`, tiré par la préparation de la VM), mais ce sont les
commandes dépréciées : on s'en tient à `ip` et `ss`.

### Un banc d'essai jetable : l'espace de noms réseau

On n'apprend pas à casser un réseau sur la machine par laquelle on est connecté.
Un **espace de noms réseau** (`netns`) donne une pile réseau complète et isolée :
ses propres interfaces, sa propre table de routage, ses propres règles de
pare-feu. On la relie à la machine par une paire `veth`, deux interfaces
virtuelles soudées comme les deux bouts d'un câble.

```bash
sudo ip netns add banc
sudo ip link add veth-atelier type veth peer name veth-banc
sudo ip link set veth-banc netns banc
sudo ip addr add 203.0.113.1/24 dev veth-atelier
sudo ip link set veth-atelier up
sudo ip netns exec banc ip link set lo up
sudo ip netns exec banc ip link set veth-banc up
sudo ip netns exec banc ip addr add 203.0.113.2/24 dev veth-banc
```

`ip netns exec banc <commande>` exécute une commande **dans** l'espace de noms.
Vu de dedans, le reste de la machine n'existe pas :

```bash
sudo ip netns exec banc ip -br addr
# lo               UNKNOWN        127.0.0.1/8 ::1/128
# veth-banc@if4    UP             203.0.113.2/24 fe80::c098:bdff:fecf:9d1a/64
```

Le `@if4` est précieux : c'est l'index de l'interface d'en face. Côté machine,
`ip link show veth-atelier` affiche symétriquement `link-netns banc`.

### Le lien : `ip link` avant tout le reste

Un lien a **deux** états, et c'est la première chose à lire. L'état
administratif (`UP` ou `DOWN`) dit si vous l'avez activé. L'état physique
(`LOWER_UP`) dit si le câble est branché. Coupons le bout du câble qui est dans
le banc :

```bash
sudo ip netns exec banc ip link set veth-banc down
ip -br link show veth-atelier
```

```text
veth-atelier@if3 DOWN           9a:1d:e8:2a:ca:4c <NO-CARRIER,BROADCAST,MULTICAST,UP>
```

Lisez bien : le drapeau `UP` est toujours là (l'interface est activée), mais
`LOWER_UP` a disparu et `NO-CARRIER` s'affiche. Personne n'est branché en face.
`ip -br addr` est encore plus trompeur, il montre l'adresse comme si tout allait
bien :

```text
veth-atelier@if3 DOWN           203.0.113.1/24 fe80::981d:e8ff:fe2a:ca4c/64
```

L'adresse est configurée, la route existe, et pourtant `ping` ne reçoit rien.
Une paire `veth` reproduit exactement le symptôme d'un câble débranché ou d'un
port de commutateur éteint. On remonte le lien, le trafic repart :

```bash
sudo ip netns exec banc ip link set veth-banc up
ip -br link show veth-atelier
# veth-atelier@if3 UP    9a:1d:e8:2a:ca:4c <BROADCAST,MULTICAST,UP,LOWER_UP>
```

Deux commandes complètent l'étage : `ip neigh show dev veth-atelier` affiche
l'adresse MAC apprise en face (`203.0.113.2 lladdr c2:98:bd:cf:9d:1a STALE`),
preuve que la couche 2 fonctionne, et `ip -s link show <iface>` donne les
compteurs `errors` et `dropped`, qui doivent rester à zéro.

### L'adresse et la route : `ip route get` plutôt que `ip route`

`ip route` liste la table ; `ip route get <destination>` répond à la seule
question qui compte : par où **ce** paquet va-t-il sortir ? La nuance n'est pas
cosmétique. Reprenons le banc au moment où l'adresse était posée mais
l'interface pas encore activée :

```bash
ip route | grep 203 || echo "(aucune route 203.0.113.0/24)"
ip route get 203.0.113.2
```

```text
(aucune route 203.0.113.0/24)
203.0.113.2 via 10.10.30.1 dev eth0 src 10.10.30.12
    cache
```

Voilà le vrai visage d'une panne de routage sur une machine ordinaire. La route
directe n'existe pas (le noyau ne crée la route connectée qu'une fois
l'interface activée), donc le paquet part vers la **passerelle par défaut**, sur
la mauvaise interface, et se perd : `curl` finit en timeout. Le guide annonce un
`unreachable` en cas de problème de routage ; dès qu'une route par défaut
existe, vous ne verrez pas `unreachable`, vous verrez un `dev` inattendu. C'est
cette ligne qu'il faut savoir lire.

Une fois l'interface activée, la même commande dit la vérité :

```text
203.0.113.2 dev veth-atelier src 203.0.113.1
    cache
```

`Network is unreachable` existe bel et bien, mais seulement quand **aucune**
route ne couvre la destination, route par défaut comprise. Le banc, qui n'a pas
de passerelle, le montre :

```bash
sudo ip netns exec banc ip route get 8.8.8.8
# RTNETLINK answers: Network is unreachable
sudo ip netns exec banc ping -c1 -W1 8.8.8.8
# ping: connect: Network is unreachable
```

Notez enfin que tout ce qui est posé avec `ip addr add` ou `ip link set up` vit
**en mémoire** : rien ne survit au redémarrage. La configuration persistante est
gérée ailleurs, par NetworkManager sur cette famille de distributions.

### Le nom : `getent hosts` plutôt que `ping`

Tester la résolution avec `ping <nom>`, c'est éprouver deux choses à la fois et
ne pas savoir laquelle a échoué. `getent hosts` interroge la résolution
**seule**, par le même chemin que les applications (celui de
`/etc/nsswitch.conf`) :

```bash
getent hosts serveur-banc.lab ; echo "rc=$?"     # rc=2, aucune sortie
ping -c1 -W1 serveur-banc.lab
# ping: serveur-banc.lab: Name or service not known
curl -sS --connect-timeout 3 http://serveur-banc.lab:8080/
# curl: (6) Could not resolve host: serveur-banc.lab
```

Aucun paquet n'est parti vers le réseau : inutile de chercher un pare-feu. Pour
prouver que **seul** le nom est en cause, court-circuitez la résolution avec
`curl --resolve`, qui associe un nom à une adresse le temps d'une requête :

```bash
curl -sS --resolve serveur-banc.lab:8080:203.0.113.2 http://serveur-banc.lab:8080/
# page de test
```

Le service répond parfaitement : la panne est bien dans le nommage. Deux pièges
à connaître. D'abord, **`dig` ne voit pas `/etc/hosts`** : il parle directement
au serveur DNS, alors que les applications passent par NSS. Sur cette VM, les
deux outils donnent deux réponses différentes pour le même nom :

```bash
getent hosts atelier.lab      # ::1        atelier.lab atelier.lab
dig +short atelier.lab        # 10.10.30.12
```

Un `dig` triomphant ne prouve donc rien sur ce que verra l'application. Ensuite,
`dig +short` renvoie **0 même sur un NXDOMAIN**, avec une sortie vide, alors que
`getent hosts` renvoie 2 : dans un script, testez avec `getent`, et gardez `dig`
pour lire l'en-tête de la réponse et le résolveur interrogé.

```bash
dig serveur-banc.lab | grep -E "^;; ->>HEADER|^;; SERVER"
# ;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 33212
# ;; SERVER: 10.10.30.1#53(10.10.30.1) (UDP)
```

Ce résolveur vient de `/etc/resolv.conf` (ici `nameserver 10.10.30.1`, écrit par
NetworkManager). Méfiance avec `resolvectl status`, souvent cité : le service
`systemd-resolved` n'est **pas actif** sur cette VM et la commande échoue avec
`Failed to get global data: The name is not activatable`.

### Le service : qui écoute, qui filtre

Dernier étage, celui du service distant. `ss -tlnp` liste les sockets en écoute
(`-t` TCP, `-l` en écoute, `-n` sans résolution, `-p` avec le processus) :

```bash
sudo ip netns exec banc ss -tlnp
```

```text
State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
LISTEN 0      5        203.0.113.2:8080      0.0.0.0:*    users:(("python3",pid=3208,fd=3))
LISTEN 0      5          127.0.0.1:8081      0.0.0.0:*    users:(("python3",pid=3462,fd=3))
```

Lisez la colonne **Local Address**, pas seulement le port. Le service du port
8081 n'écoute que sur `127.0.0.1` : il répond en local et refuse toute connexion
venue du réseau, alors que `systemctl` le déclare parfaitement actif. Sans
`sudo`, `ss` affiche bien les sockets mais laisse la colonne `Process` vide.

Faute de `nc`, deux façons de tester un port. `bash` d'abord, qui donne le
message d'erreur brut :

```bash
timeout 3 bash -c "echo > /dev/tcp/203.0.113.2/9090"
# bash: connect: Connection refused
```

`curl` ensuite, mais il lui faut `-v` : depuis sa version 8, son message de
résumé noie la cause réelle sous un « Could not connect to server » sans
intérêt.

```bash
curl -v --connect-timeout 3 http://203.0.113.2:9090/ 2>&1 | grep "^\*"
```

```text
[...]
* connect to 203.0.113.2 port 9090 from 203.0.113.1 port 54814 failed: Connection refused
* Failed to connect to 203.0.113.2 port 9090 after 0 ms: Could not connect to server
```

Filtrons maintenant. Un espace de noms a **ses propres** règles `nftables` :
tout ce qui suit reste sans effet sur la machine, `nft list tables` ne montrant
côté machine que la table `inet firewalld`.

```bash
sudo ip netns exec banc nft add table inet filtre
sudo ip netns exec banc nft add chain inet filtre entree \
  "{ type filter hook input priority 0; policy accept; }"
sudo ip netns exec banc nft add rule inet filtre entree tcp dport 8080 drop
time curl -sS --connect-timeout 5 http://203.0.113.2:8080/
```

```text
curl: (28) Connection timed out after 5002 milliseconds
real	0m5.009s
```

Même port, même service, message radicalement différent : `Connection refused`
plus haut, **timeout** ici. Le refus est une réponse, donc l'hôte est joignable
et rien n'écoute. Le timeout est un silence, donc quelque chose jette les
paquets. C'est le seul des quatre messages qui accuse un filtrage.

### Quatre messages, quatre pannes, et le cas de `ping`

Chaque étage a son message. Les reconnaître, c'est sauter droit à la bonne
commande au lieu de tout revérifier :

| Message | Ce qu'il prouve | Où regarder |
|---|---|---|
| `Name or service not known`, `Could not resolve host` | aucun paquet n'est parti, le nom n'a pas été résolu | `getent hosts`, `/etc/resolv.conf`, `dig` |
| `Network is unreachable` | aucune route ne couvre la destination | `ip route get <ip>`, `ip route show default` |
| `Connection refused` | l'hôte répond, rien n'écoute sur ce port | `ss -tlnp` sur la machine distante |
| un timeout | les paquets partent, rien ne revient : filtrage | pare-feu des deux côtés, route de retour |

Reste le cas de `ping`, mauvais premier test pour deux raisons. Il mêle
résolution et joignabilité, on vient de le voir. Et il éprouve ICMP, un
protocole que le service visé n'utilise pas. Les deux erreurs se démontrent sur
le banc. Avec la règle qui bloque le port 8080, `ping` est parfaitement
rassurant alors que le service est inatteignable :

```text
2 packets transmitted, 2 received, 0% packet loss, time 1006ms
```

Et à l'inverse, en ne bloquant que l'ICMP :

```bash
sudo ip netns exec banc nft flush chain inet filtre entree
sudo ip netns exec banc nft add rule inet filtre entree ip protocol icmp drop
ping -c2 -W1 203.0.113.2 | tail -2
# 2 packets transmitted, 0 received, 100% packet loss, time 1033ms
curl -sS --connect-timeout 3 -o /dev/null -w "code=%{http_code}\n" http://203.0.113.2:8080/
# code=200
```

Le `ping` échoue à 100 %, le service répond `200`. Conclure « la machine est
éteinte » sur un `ping` muet est donc une erreur de raisonnement, pas un
raccourci acceptable : testez toujours le port réellement utilisé.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `ip -br link` affiche `NO-CARRIER` et `UP` ensemble | interface activée, mais rien de branché en face |
| l'adresse s'affiche dans `ip addr` et rien ne passe | lire l'état du lien : une adresse survit à un lien mort |
| `ip route get` désigne un `dev` inattendu | la route directe manque, le paquet part par la route par défaut |
| `Network is unreachable` | aucune route, y compris par défaut, ne couvre la destination |
| `Name or service not known` | résolution en échec, aucun paquet émis : voir `/etc/resolv.conf` |
| `dig` répond alors que l'application échoue | `dig` ignore `/etc/hosts`, comparer avec `getent hosts` |
| `Connection refused` | rien n'écoute : `ss -tlnp`, vérifier l'adresse d'écoute (`127.0.0.1` ?) |
| timeout franc sur un port précis | filtrage : pare-feu local, pare-feu distant ou route de retour |
| `ping` muet, service pourtant joignable | ICMP filtré : ne jamais conclure sur le seul `ping` |
| `resolvectl` échoue avec `not activatable` | `systemd-resolved` est inactif ici, lire `/etc/resolv.conf` |
| la configuration disparaît au redémarrage | `ip addr add` ne persiste pas, il faut passer par NetworkManager |

Pour démonter le banc, arrêtez d'abord ce qui tourne dedans, puis supprimez
l'espace de noms : la disparition d'un bout de `veth` emporte l'autre.

```bash
sudo ip netns pids banc         # ce qui vit encore dans le banc
sudo kill <pid> ...             # on l'arrête
sudo ip netns del banc
ip netns list                   # aucune sortie
ip -br link                     # veth-atelier a disparu
```

L'ordre n'est pas décoratif. Lancé alors que les serveurs tournaient encore,
`ip netns del banc` a bien vidé `ip netns list`, mais `veth-atelier` était
toujours là, `UP` : un espace de noms survit à la suppression de son nom tant
qu'un processus l'occupe. Vérifiez donc par `ip -br link`, pas `ip netns list`.
