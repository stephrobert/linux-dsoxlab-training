# Lab — redirection de port NAT persistante avec nftables

## Rappel

[**NAT & redirection de port sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/)

Le routage exige `net.ipv4.ip_forward = 1` (persiste-le dans `/etc/sysctl.d/`).
nftables fait le travail : une table `nat` avec une chaîne `prerouting`
(`dnat` = la redirection de port) et une chaîne `postrouting` (`masquerade` =
SNAT). Sur RHEL, la persistance passe par `/etc/sysconfig/nftables.conf` (qui
`include` ton fichier `.nft`) plus le service `nftables` activé.

## Le cours

Les exemples ci-dessous montent une passerelle de démonstration entre deux
réseaux fictifs, avec ses propres ports et ses propres adresses : le challenge
vous en demandera d'autres. Le but est d'apprendre la méthode et de savoir la
prouver, pas de recopier une ligne. Toutes les sorties qui suivent ont été
produites sur une AlmaLinux 10.

### Les deux sens du NAT

Le NAT réécrit les adresses des paquets qui traversent la passerelle, et
nftables le fait dans deux chaînes distinctes :

- **`prerouting`** (entrée) : dès l'arrivée du paquet, on réécrit l'adresse
  **destination**. C'est le **DNAT**, celui de la redirection de port.
- **`postrouting`** (sortie) : juste avant d'émettre, on réécrit l'adresse
  **source**. C'est le **SNAT** ; sa forme automatique est le **masquerade**,
  qui prend l'adresse de l'interface de sortie.

Retenez la formule du guide : **DNAT pour entrer, masquerade pour sortir**. Et
retenez la méthode : une redirection ne se démontre pas en lisant une règle,
mais en mesurant deux fois, avec et sans elle.

### Le banc d'essai : deux réseaux sans deuxième machine

Pour prouver une redirection, il faut un client qui arrive de l'extérieur et un
service à joindre. Les **espaces de noms réseau** (`ip netns`) donnent les deux
sur une seule machine : chacun a sa propre pile réseau, ses interfaces et sa
table de routage. Une paire `veth` les relie à l'hôte comme un câble.

```bash
for ns in client backend; do sudo ip netns add demo-$ns; done
sudo ip link add to-client  type veth peer name eth-c
sudo ip link add to-backend type veth peer name eth-b
sudo ip link set eth-c netns demo-client
sudo ip link set eth-b netns demo-backend

# Côté hôte : la passerelle a un pied dans chaque réseau
sudo ip addr add 198.51.100.1/24 dev to-client  && sudo ip link set to-client up
sudo ip addr add 203.0.113.1/24  dev to-backend && sudo ip link set to-backend up

# Le client, avec l'hôte comme route par défaut
sudo ip netns exec demo-client ip addr add 198.51.100.2/24 dev eth-c
sudo ip netns exec demo-client ip link set eth-c up
sudo ip netns exec demo-client ip route add default via 198.51.100.1

# Le backend, volontairement sans route par défaut (on y reviendra)
sudo ip netns exec demo-backend ip addr add 203.0.113.2/24 dev eth-b
sudo ip netns exec demo-backend ip link set eth-b up
```

Enfin, deux services sur le port haut `18443`, un sur l'hôte et un dans le
backend, chacun servant une page qui dit d'où elle vient :

```bash
sudo mkdir -p /tmp/demo-local /tmp/demo-distant
echo SERVEUR-LOCAL-PORT-18443   | sudo tee /tmp/demo-local/index.html
echo SERVEUR-DISTANT-PORT-18443 | sudo tee /tmp/demo-distant/index.html
sudo sh -c 'cd /tmp/demo-local && setsid python3 -m http.server 18443 &'
sudo sh -c 'cd /tmp/demo-distant && setsid ip netns exec demo-backend \
  python3 -m http.server 18443 >/tmp/demo-distant.log 2>&1 &'
```

### Rediriger un port vers un service local

Premier cas : le port d'entrée et le service sont sur la **même** machine. On
expose sur `9443` un service qui écoute en `18443`.

Mesure 1, sans aucune règle :

```bash
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
curl: (7) Failed to connect to 198.51.100.1 port 9443 after 0 ms: Could not connect to server
```

La table, la chaîne, la règle :

```bash
sudo nft add table ip demo-nat
sudo nft add chain ip demo-nat prerouting '{ type nat hook prerouting priority dstnat ; }'
sudo nft add rule  ip demo-nat prerouting iifname "to-client" tcp dport 9443 dnat to 198.51.100.1:18443
sudo nft list table ip demo-nat
```

```text
table ip demo-nat {
	chain prerouting {
		type nat hook prerouting priority dstnat; policy accept;
		iifname "to-client" tcp dport 9443 dnat to 198.51.100.1:18443
	}
}
```

Mesure 2, le même `curl`, précédé de l'état du routage :

```bash
sysctl net.ipv4.ip_forward
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
net.ipv4.ip_forward = 0
SERVEUR-LOCAL-PORT-18443
```

**Retenez ce `0`.** Une redirection vers un service local n'a pas eu besoin du
routage : le paquet entre, sa destination est réécrite vers une adresse de la
machine elle-même, il est livré localement. Il ne traverse rien.

Mesure 3, on retire la règle, rien d'autre ne change :

```bash
sudo nft flush chain ip demo-nat prerouting
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
curl: (7) Failed to connect to 198.51.100.1 port 9443 after 0 ms: Could not connect to server
```

Trois mesures, et la règle est la seule variable : le mécanisme est prouvé.

### Rediriger vers une autre machine : le routage devient obligatoire

Deuxième cas, la vraie passerelle : le service est sur une **autre** machine.
Seule la cible du `dnat` change.

```bash
sudo nft add rule ip demo-nat prerouting iifname "to-client" tcp dport 9443 dnat to 203.0.113.2:18443
sysctl net.ipv4.ip_forward
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
net.ipv4.ip_forward = 0
curl: (28) Connection timed out after 5003 milliseconds
```

Notez le changement de symptôme : `(7)` devient `(28)`. Un refus immédiat
signifie « personne n'écoute » ; un **délai d'attente** signifie que le paquet
est parti quelque part et que rien n'est revenu. Ici, il a été jeté faute de
routage.

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
net.ipv4.ip_forward = 1
curl: (28) Connection timed out after 5002 milliseconds
```

Toujours en échec, mais plus pour la même raison. `conntrack` le dit :

```bash
sudo conntrack -L | grep dport=9443
```

```text
tcp 6 114 SYN_SENT src=198.51.100.2 dst=198.51.100.1 sport=59474 dport=9443 [UNREPLIED] src=203.0.113.2 dst=198.51.100.2 sport=18443 dport=59474
```

Lisez les **deux tuples**. Le premier est la connexion vue du client. Le second
est le retour que le noyau attend : il devrait venir de `203.0.113.2:18443` et
aller vers `198.51.100.2`. La mention `[UNREPLIED]` dit que ce retour n'est
jamais arrivé. Le DNAT a bien fonctionné, le paquet a bien été routé ; c'est la
**réponse** qui manque.

### MASQUERADE : faire revenir les réponses

Pourquoi le backend ne répond-il pas ? Sa table de routage :

```text
203.0.113.0/24 dev eth-b proto kernel scope link src 203.0.113.2
```

Il ne connaît que son propre réseau. Le paquet qu'il a reçu portait
`src=198.51.100.2`, une adresse qu'il n'a aucun moyen de joindre. C'est le
piège signalé par le guide : sans route de retour vers le client, la traduction
casse en chemin. Deux issues possibles : donner au backend une route par défaut
vers la passerelle, ou masquer la source pour qu'il croie parler à son voisin
direct. La seconde est celle du NAT :

```bash
sudo nft add chain ip demo-nat postrouting '{ type nat hook postrouting priority srcnat ; }'
sudo nft add rule  ip demo-nat postrouting ip daddr 203.0.113.2 oifname "to-backend" masquerade
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
SERVEUR-DISTANT-PORT-18443
```

Le journal du serveur distant (`/tmp/demo-distant.log`) montre qui l'a
contacté :

```text
203.0.113.1 - - [22/Jul/2026 16:42:35] "GET / HTTP/1.1" 200 -
```

`203.0.113.1` est la passerelle, pas le client : la source a bien été masquée.
Et `conntrack` porte maintenant les **deux** réécritures sur une seule ligne :

```text
tcp 6 119 TIME_WAIT src=198.51.100.2 dst=198.51.100.1 sport=37046 dport=9443 src=203.0.113.2 dst=203.0.113.1 sport=18443 dport=37046 [ASSURED]
```

Destination réécrite (`198.51.100.1:9443` devient `203.0.113.2:18443`) et
source réécrite (`198.51.100.2` devient `203.0.113.1`). C'est l'outil de
diagnostic numéro un du NAT : il montre ce que le noyau fait, pas ce que vous
croyez avoir écrit.

### Rendre tout ça persistant

Deux choses ont été posées en mémoire, et **les deux disparaissent au
redémarrage**.

**Le routage.** Un `sysctl -w` ne survit pas ; il faut un fichier dans
`/etc/sysctl.d/` :

```bash
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/98-demo-routeur.conf
sudo sysctl --system
```

```text
* Applying /etc/sysctl.d/98-demo-routeur.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
```

`sysctl --system` rejoue exactement ce que fait le démarrage : c'est la façon
de vérifier son fichier sans redémarrer.

> **Le piège à connaître.** Supprimer le fichier ne remet pas la valeur d'avant.
> Mesuré : après `rm` du fichier, `sysctl -n net.ipv4.ip_forward` renvoie
> toujours `1`. Le fichier décide de la valeur **au démarrage**, pas de la
> valeur courante. Pour vraiment revenir en arrière, reposez-la à la main avec
> `sudo sysctl -w net.ipv4.ip_forward=0`.

**Le ruleset.** Écrivez la table dans un fichier, puis prouvez qu'il suffit à
la reconstruire en simulant le redémarrage :

```bash
sudo sh -c 'nft list table ip demo-nat > /etc/nftables/demo-nat.nft'
sudo nft delete table ip demo-nat          # comme au reboot : tout est perdu
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
sudo nft -f /etc/nftables/demo-nat.nft     # ce que fera le service au boot
sudo ip netns exec demo-client curl -sS --max-time 5 http://198.51.100.1:9443/
```

```text
curl: (7) Failed to connect to 198.51.100.1 port 9443 after 0 ms: Could not connect to server
SERVEUR-DISTANT-PORT-18443
```

Reste à faire rejouer ce fichier au démarrage, et c'est le rôle du service
`nftables`. **Ne devinez pas le chemin qu'il lit, demandez-le à l'unité :**

```bash
systemctl cat nftables | grep ExecStart
```

```text
ExecStart=/sbin/nft -f /etc/sysconfig/nftables.conf
```

> **Écart avec le guide.** Le guide écrit `nft list ruleset > /etc/nftables.conf`,
> qui est la convention Debian. Sur cette AlmaLinux 10, `/etc/nftables.conf`
> **n'existe pas** (`ls` renvoie « No such file or directory ») et le service lit
> `/etc/sysconfig/nftables.conf`. Suivre le guide à la lettre ici produirait un
> fichier que rien ne charge : une règle qu'on croit persistée et qui ne revient
> jamais. Le `systemctl cat` ci-dessus est votre garde-fou, sur n'importe quelle
> distribution.

Ce fichier accepte deux formes : les règles écrites directement dedans, ou une
directive `include` pointant vers votre propre fichier `.nft`. La seconde garde
votre travail séparé de celui de la distribution.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `curl: (7)` immédiat | Aucune règle ne correspond | `nft list table ip <table>` |
| `curl: (28)` en délai d'attente | Paquet parti sans retour | `conntrack -L`, chercher `[UNREPLIED]` |
| DNAT local qui échoue | Mauvaise `iifname` ou mauvais port | Ajouter un `counter` (ci-dessous) |
| DNAT distant sans effet | Routage désactivé | `sysctl net.ipv4.ip_forward` doit valoir `1` |
| Le backend ne répond pas | Pas de route de retour vers le client | `masquerade` en `postrouting`, ou route par défaut côté backend |
| Tout disparaît au reboot | Ruleset non persisté | `systemctl cat nftables` pour trouver le bon fichier |

Le **compteur** répond à la seule question qui compte quand rien ne marche : la
règle est-elle seulement traversée ?

```bash
sudo nft add rule ip demo-nat prerouting iifname "to-client" tcp dport 9443 counter dnat to 203.0.113.2:18443
sudo nft list chain ip demo-nat prerouting
```

```text
iifname "to-client" tcp dport 9443 counter packets 1 bytes 60 dnat to 203.0.113.2:18443
```

Un compteur à zéro écarte d'emblée le NAT : le paquet n'arrive pas jusqu'à la
règle, cherchez du côté de l'interface, du port ou du routage en amont.

Sur AlmaLinux, **firewalld possède sa propre table** et cohabite avec la vôtre ;
l'ordre est donné par la priorité des chaînes :

```bash
sudo nft list ruleset | grep "hook prerouting priority dstnat"
```

```text
		type nat hook prerouting priority dstnat + 10; policy accept;
		type nat hook prerouting priority dstnat; policy accept;
```

La première est celle de firewalld, la seconde la vôtre. Plus la valeur est
basse, plus la chaîne est appelée tôt : ici la vôtre passe avant.

> **Prudence avec le service.** `systemctl cat nftables` montre aussi
> `ExecStop=/sbin/nft flush ruleset` : arrêter le service vide **tout** le
> ruleset, y compris les tables d'un autre pare-feu. Sur une machine dont vous
> dépendez pour votre session, préférez `nft -f <fichier>` pour tester un
> rechargement.

Enfin, démontez le banc d'essai. Supprimer un espace de noms emporte avec lui
son interface `veth` et les processus qui y tournaient :

```bash
sudo nft delete table ip demo-nat
sudo ip netns delete demo-client && sudo ip netns delete demo-backend
sudo sysctl -w net.ipv4.ip_forward=0
```
