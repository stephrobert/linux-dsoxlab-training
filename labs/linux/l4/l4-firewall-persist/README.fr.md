# Lab — ouvrir un service firewalld de façon permanente

## Rappel

[**firewalld sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/)

`firewalld` filtre par **zone** (défaut `public`). `firewall-cmd --add-service`
change le runtime seulement (perdu au reload/reboot) ; `--permanent` écrit la
config de zone, et `--reload` applique le permanent au runtime. Vérifie avec
`--list-services` (runtime) et `--permanent --list-services`.

Ne retire jamais `ssh` — ça fermerait ton accès de gestion.

## Le cours

Les exemples ci-dessous ouvrent un **port brut `8443/tcp`** puis le service
nommé `ftp`, sur une machine de démonstration AlmaLinux 10 : le challenge, lui,
vous demandera un autre service. Le but est d'apprendre le mécanisme runtime /
permanent, pas de recopier une ligne.

Toutes les sorties reproduites ici sont celles de la machine d'atelier.

### Où s'applique une règle : la zone

`firewalld` n'a pas une liste de règles, il en a une **par zone**. Chaque
interface réseau appartient à une zone, et une commande sans `--zone` vise la
**zone par défaut**.

```bash
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --get-zone-of-interface=eth0
sudo firewall-cmd --get-active-zones
```

```text
public
public
public (default)
  interfaces: eth0
```

Ici les deux coïncident : la zone par défaut est `public`, et `eth0` (celle qui
porte la session SSH) est justement dans `public`. **Ce n'est pas une garantie**,
c'est une commodité de configuration par défaut. Sur une machine à plusieurs
cartes, vérifiez les deux avant d'écrire quoi que ce soit.

`--list-all` donne l'état complet de la zone active :

```bash
sudo firewall-cmd --list-all
```

```text
public (default, active)
  target: default
  [...]
  interfaces: eth0
  sources:
  services: cockpit dhcpv6-client ssh
  ports:
  [...]
  rich rules:
```

Trois services autorisés, aucun port brut. Tout le reste est refusé : c'est le
point de départ. Notez `ssh` dans la liste, c'est votre accès. Il ne doit jamais
en sortir.

### Un port de test pour voir le pare-feu à l'œuvre

Pour prouver qu'une règle agit, il faut quelque chose qui écoute derrière. Un
mini-serveur TCP qui accepte puis raccroche suffit :

```bash
nohup python3 -c 'import socketserver; socketserver.TCPServer(("",8443), socketserver.BaseRequestHandler).serve_forever()' >/dev/null 2>&1 &
ss -tlnp | grep 8443
```

```text
LISTEN 0      5      0.0.0.0:8443      0.0.0.0:*    users:(("python3",pid=28029,fd=3))
```

Le service écoute sur toutes les adresses. Depuis un **autre poste**, on teste
la connexion sans aucun client dédié :

```bash
timeout 5 bash -c 'exec 3<>/dev/tcp/<ip-de-la-vm>/8443'; echo $?
```

```text
bash: connect: No route to host
1
```

`No route to host` n'est pas une panne de routage : le pare-feu ne se contente
pas d'ignorer le paquet, il le **rejette**, et c'est ce rejet que le client
traduit ainsi. Le service tourne, le pare-feu le rend injoignable.

### Runtime : le brouillon qui disparaît au reload

```bash
sudo firewall-cmd --add-port=8443/tcp
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --list-ports
```

```text
success
8443/tcp
```

La deuxième liste est **vide** : la règle n'existe qu'en runtime. Depuis
l'autre poste, la connexion passe maintenant (`echo $?` répond `0`).

Puis le rechargement :

```bash
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

```text
success

```

La ligne suivante est vide : plus aucun port. `--reload` relit la configuration
permanente et **jette** tout ce qui n'était qu'en runtime. La connexion redonne
`No route to host`, et la session SSH, elle, n'a pas bougé (les connexions TCP
déjà établies survivent au rechargement).

C'est le comportement à retenir : le runtime est un **brouillon**. C'est aussi
votre filet de sécurité, une erreur en runtime s'efface d'un `--reload`.

### Permanent : écrit sur le disque, mais inactif jusqu'au reload

L'inverse déroute tout autant :

```bash
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --list-ports              # runtime
sudo firewall-cmd --permanent --list-ports  # permanent
```

```text
success

8443/tcp
```

La règle est enregistrée, et pourtant la connexion depuis l'autre poste est
toujours refusée. `--permanent` **n'agit pas sur le pare-feu en cours**, il
écrit un fichier. C'est ce que le guide résume par « ajoutée en `--permanent`
sans `--reload` ».

Ce fichier, le voici :

```bash
sudo ls -l /etc/firewalld/zones/
sudo cat /etc/firewalld/zones/public.xml
```

```text
-rw-r--r--. 1 root root 393 Jul 22 16:22 public.xml
```

```xml
<zone>
  <short>Public</short>
  [...]
  <service name="ssh"/>
  <service name="dhcpv6-client"/>
  <service name="cockpit"/>
  <port port="8443" protocol="tcp"/>
  <forward/>
</zone>
```

Détail qui surprend : **avant cette commande, `/etc/firewalld/zones/` était
vide**. La zone `public` livrée par la distribution vit dans
`/usr/lib/firewalld/zones/public.xml`, et `--permanent` en fabrique une copie
locale au premier écrit. Un répertoire vide ne veut donc pas dire « aucune règle
permanente », il veut dire « rien n'a encore été personnalisé ».

Il ne reste qu'à appliquer :

```bash
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

```text
success
8443/tcp
```

Cette fois la connexion passe, et elle passera encore après un redémarrage.

### `--runtime-to-permanent`, et son effet de bord

Quand on a enchaîné plusieurs essais concluants en runtime, une commande fige
l'état courant d'un coup :

```bash
sudo firewall-cmd --runtime-to-permanent
sudo firewall-cmd --permanent --list-services
sudo firewall-cmd --permanent --list-ports
```

```text
success
cockpit dhcpv6-client ftp ssh
8443/tcp
```

Pratique, mais à manier en connaissance de cause : elle **réécrit toutes les
zones**, pas seulement celle que vous modifiiez. Après cette seule commande, le
répertoire des zones ne contenait plus un fichier mais onze, plus six fichiers
de politiques :

```text
block.xml  dmz.xml  drop.xml  external.xml  home.xml  internal.xml
nm-shared.xml  public.xml  public.xml.old  trusted.xml  work.xml
```

Aucune règle n'a changé (comparés aux originaux de `/usr/lib/firewalld/`, ces
fichiers sont identiques au reformatage près), mais ces copies locales
**masquent désormais** les définitions livrées par la distribution, pour toutes
les zones d'un coup. Sur un serveur qu'on garde, préférez la séquence explicite
`--permanent` puis `--reload`, qui ne touche qu'un fichier.

### Service nommé ou port numéroté : deux listes distinctes

Un « service » `firewalld` est un alias vers un ou plusieurs ports. On peut
l'inspecter avant de l'ouvrir :

```bash
sudo firewall-cmd --info-service=ftp
```

```text
ftp
  ports: 21/tcp
  protocols:
  source-ports:
  modules:
  destination:
  includes:
  helpers: ftp
```

`--add-service=ftp` ouvre donc `21/tcp`, et la définition mentionne en plus un
`helper` de suivi de connexion. Un `--add-port=21/tcp` n'ouvrirait que le
numéro de port, sans rien d'autre : les deux écritures ne recouvrent pas la même
chose, et surtout elles ne se lisent pas au même endroit.

```bash
sudo firewall-cmd --add-service=ftp
sudo firewall-cmd --list-services
sudo firewall-cmd --list-ports
```

```text
success
cockpit dhcpv6-client ftp ssh
8443/tcp
```

Deux listes séparées : `--list-services` ne montrera **jamais** un port ajouté
par `--add-port`, et réciproquement. Un service qu'on cherche dans la mauvaise
liste passe pour absent. En cas de doute, `--list-all` affiche les deux.

Règle de choix : le service nommé quand il existe (lisible, maintenable), le
port brut pour tout ce qui écoute sur un port non standard.

### La bonne règle dans la mauvaise zone

C'est l'erreur la plus fréquente, et la plus silencieuse : `firewall-cmd`
répond `success` et rien ne marche.

```bash
sudo firewall-cmd --remove-port=8443/tcp             # zone par défaut
sudo firewall-cmd --zone=work --add-port=8443/tcp    # zone "work"
sudo firewall-cmd --zone=work --list-ports
sudo firewall-cmd --list-ports
sudo firewall-cmd --get-active-zones
```

```text
success
success
8443/tcp

public (default)
  interfaces: eth0
```

Le port est bien ouvert dans `work`, la commande a réussi, et pourtant la
connexion depuis l'autre poste est refusée : **aucune interface n'est dans
`work`**, la règle ne voit passer aucun paquet. Le trafic arrive par `eth0`,
donc dans `public`.

D'où le réflexe : `--get-active-zones` d'abord, `--zone=<celle-là>` ensuite, ou
rien du tout si la zone active est déjà la zone par défaut.

### Défaire, et ce qu'il ne faut jamais faire

Retirer une règle permanente demande la même paire de commandes que l'ajouter :

```bash
sudo firewall-cmd --permanent --remove-port=8443/tcp
sudo firewall-cmd --permanent --remove-service=ftp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

```text
public (default, active)
  [...]
  services: cockpit dhcpv6-client ssh
  ports:
  [...]
```

L'état de départ est rendu. Trois gestes, en revanche, coupent la session
immédiatement, et le second compte administrateur ne sauve pas puisqu'il passe
par le même port :

- `--remove-service=ssh` sur la zone active ;
- `--set-default-zone=drop` ou `block`, deux zones qui n'autorisent pas `ssh`
  (leur `--list-all` montre `services:` vide) ;
- `--panic-on`, qui coupe tout le trafic entrant **et** sortant.

Le guide les documente comme outils de réponse à incident, à n'employer qu'avec
un accès console de secours.

Pour le dépannage courant, deux commandes valent tout le reste :
`firewall-cmd --list-all` (ce que la zone active autorise vraiment) et
`sudo firewall-cmd --set-log-denied=unicast`, qui fait apparaître les paquets
refusés dans `journalctl -u firewalld`. Pensez à la remettre sur `off` ensuite.

Le tableau de dépannage du guide compagnon couvre les autres symptômes
(règle visible mais inactive, règle disparue au reboot, port ouvert mais service
injoignable) : il vaut la lecture avant de se lancer.
