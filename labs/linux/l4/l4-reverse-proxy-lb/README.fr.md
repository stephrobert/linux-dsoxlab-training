# Lab — reverse proxy & répartition de charge avec HAProxy

## Rappel

[**HAProxy sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/reseau/haproxy/)

HAProxy est un proxy L7 : un `frontend` écoute un port, un `backend` liste les
`server`s réels et `balance` la charge entre eux. `haproxy -c -f <cfg>` valide la
conf avant de démarrer le service.

## Le cours

Les exemples de ce cours ne sont pas ceux du challenge : ils montent un proxy
avec **un autre outil** (nginx), sur **d'autres ports**, devant **d'autres
backends**. C'est volontaire : la mécanique d'un proxy inverse est la même
partout, seuls les mots-clés changent, et ce qui est démontré ici se transpose
sur l'outil du challenge, dont la syntaxe est décrite dans le guide ci-dessus.

Toutes les sorties ci-dessous viennent d'une VM AlmaLinux 10.2 (`10.10.30.13`),
interrogée depuis un poste client (`10.10.30.1`).

### Proxy inverse ou répartiteur de charge : ce qui les sépare

Les deux termes sont souvent confondus. Le guide
[Reverse proxy](https://blog.stephane-robert.info/docs/services/reseau/reverse-proxy/)
les distingue ainsi :

| Concept | Ce qu'il fait |
|---|---|
| **Proxy inverse** | Point d'entrée HTTP(S) : TLS, routage, en-têtes, sécurité |
| **Répartiteur de charge** | Répartit le trafic entre plusieurs serveurs (L4 ou L7) |

Retenez la règle simple : un proxy inverse relaie vers **un** service, un
répartiteur de charge distribue entre **plusieurs**. En pratique la plupart des
outils font les deux, et le passage de l'un à l'autre tient en deux lignes.

### Fabriquer deux backends sans rien installer

Il faut au minimum deux services qui répondent différemment. Le module
`http.server` de Python, présent sur l'image, suffit :

```bash
mkdir -p ~/atelier/alpha ~/atelier/beta
echo "reponse du serveur alpha" > ~/atelier/alpha/index.html
echo "reponse du serveur beta"  > ~/atelier/beta/index.html

cd ~/atelier
setsid nohup python3 -m http.server 9510 --bind 127.0.0.1 --directory alpha > alpha.log 2>&1 &
setsid nohup python3 -m http.server 9511 --bind 127.0.0.1 --directory beta  > beta.log  2>&1 &
```

`--bind 127.0.0.1` limite l'écoute à la boucle locale : les backends ne sont
joignables que par le proxy, jamais directement depuis le réseau. C'est déjà un
bénéfice du proxy inverse, il cache les serveurs réels.

```bash
curl -s http://127.0.0.1:9510/ ; curl -s http://127.0.0.1:9511/
```

```text
reponse du serveur alpha
reponse du serveur beta
```

Les deux backends répondent : tout ce qui suit se diagnostique par rapport à ce
point de départ connu.

### Installer le proxy et relayer vers un seul backend

Sur l'image AlmaLinux 10 du lab, aucun serveur web n'est présent :

```bash
rpm -q nginx haproxy httpd
dnf -q repoquery --qf "%{name} %{version} %{reponame}" nginx haproxy httpd
```

```text
package nginx is not installed        [... idem pour haproxy et httpd ...]
nginx 1.26.3 appstream
haproxy 3.0.5 appstream
httpd 2.4.63 appstream
```

Les trois sont dans **AppStream**, le dépôt de la distribution : aucun dépôt
tiers, aucun EPEL n'est nécessaire. Ce cours installe `nginx`, dont la
configuration rend la différence relais / répartition particulièrement lisible.

```bash
sudo dnf install -y nginx && nginx -v    # nginx version: nginx/1.26.3
```

La configuration minimale d'un proxy inverse tient en un fichier déposé dans
`/etc/nginx/conf.d/` :

```nginx
# /etc/nginx/conf.d/atelier-proxy.conf
server {
    listen 8008;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:9510;
        proxy_set_header Host $host;
    }
}
```

Le port d'écoute n'est pas choisi au hasard : SELinux n'autorise un serveur web
à écouter que sur une liste de ports connus, `8008` en fait partie.

```bash
sudo semanage port -l | grep ^http_port_t
```

```text
http_port_t   tcp   80, 81, 443, 488, 8008, 8009, 8443, 9000
```

On valide **avant** de démarrer, réflexe qui vaut pour tout proxy :

```bash
sudo nginx -t     # configuration file /etc/nginx/nginx.conf test is successful
sudo systemctl start nginx
```

### Les trois obstacles, dans l'ordre

Sur une distribution de la famille RHEL, trois barrières se dressent entre le
client et le backend, à traiter **dans cet ordre** : tant que le pare-feu bloque
on ne voit rien de SELinux, et tant que SELinux bloque on ne voit rien de la
configuration.

**Obstacle 1, le pare-feu.** Depuis le poste client :

```bash
curl -sS --max-time 5 http://10.10.30.13:8008/
```

```text
curl: (7) Failed to connect to 10.10.30.13 port 8008 after 0 ms: Could not connect to server
```

Signature : erreur **côté client**, immédiate (« after 0 ms » : le port est
rejeté, pas filtré en silence), et **rien** dans les journaux du proxy, que la
requête n'a jamais atteint. On ouvre le port, en **runtime seulement** :

```bash
sudo firewall-cmd --add-port=8008/tcp     # success
sudo firewall-cmd --list-ports            # 8008/tcp
sudo firewall-cmd --permanent --list-ports # (vide)
```

Sans `--permanent`, la règle disparaît au prochain `firewall-cmd --reload` ou au
redémarrage : parfait pour une démonstration, insuffisant pour un service qui
doit survivre au reboot. **Ne touchez jamais au service `ssh` de la zone**,
c'est votre seul accès à la machine.

**Obstacle 2, SELinux.** Le port est ouvert, la requête arrive, et le proxy
répond `HTTP/1.1 502 Bad Gateway`. Son journal d'erreur nomme le coupable :

```bash
sudo tail -1 /var/log/nginx/error.log
```

```text
[crit] 13631#13631: *1 connect() to 127.0.0.1:9510 failed (13: Permission denied)
while connecting to upstream, client: 10.10.30.1, server: _, request: "GET / HTTP/1.1",
upstream: "http://127.0.0.1:9510/", host: "10.10.30.13:8008"
```

`Permission denied` sur un `connect()` vers la boucle locale n'a aucun sens du
point de vue Unix : c'est la marque de SELinux. Le journal d'audit le confirme :

```bash
sudo ausearch --input /var/log/audit/audit.log -m AVC | grep name_connect | tail -1
```

```text
avc: denied { name_connect } for pid=13631 comm="nginx" dest=9510
scontext=system_u:system_r:httpd_t:s0 tcontext=system_u:object_r:unreserved_port_t:s0
```

Un serveur web tourne dans le domaine `httpd_t`, et par défaut ce domaine n'a pas
le droit d'ouvrir une connexion sortante vers un port quelconque. Le booléen qui
lève cette restriction est documenté dans le guide
[SELinux](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/) :

```bash
getsebool httpd_can_network_connect     # httpd_can_network_connect --> off
sudo setsebool httpd_can_network_connect on
curl -sS http://10.10.30.13:8008/       # reponse du serveur alpha
```

Sans `-P`, le changement vit en mémoire et sera perdu au redémarrage : c'est ce
qu'on veut pour une démonstration, on ne réécrit pas la politique de la machine.
Conséquence à connaître, un booléen posé sans `-P` **n'apparaît pas** dans
`semanage boolean -l -C`, qui ne liste que les personnalisations persistantes ;
pour contrôler l'état réel, c'est `getsebool` qu'il faut interroger.

**Obstacle 3, la configuration.** Pointons volontairement le proxy vers un port
où personne n'écoute. La réponse HTTP est la **même** (502), le journal non :

```text
[error] connect() failed (111: Connection refused) while connecting to upstream,
client: 10.10.30.1, server: _, upstream: "http://127.0.0.1:9599/"
```

D'où le tableau de diagnostic, à garder en tête :

| Ce que vous voyez | Journal du proxy | Cause |
|---|---|---|
| `curl: (7) Failed to connect` | rien du tout | pare-feu |
| `502 Bad Gateway` | `(13: Permission denied)` | SELinux |
| `502 Bad Gateway` | `(111: Connection refused)` | backend absent ou mauvais port dans la conf |

Les deux `errno` disent tout : **13** veut dire « on t'interdit », **111** veut
dire « personne ne répond ».

### Passer à la répartition de charge, et le prouver

Le proxy inverse relaie vers une adresse écrite en dur. Pour répartir, on déclare
un **groupe** de serveurs et on relaie vers ce groupe :

```nginx
# /etc/nginx/conf.d/atelier-proxy.conf
upstream atelier_pool {
    server 127.0.0.1:9510;
    server 127.0.0.1:9511;
}

server {
    listen 8008;
    server_name _;

    location / {
        proxy_pass http://atelier_pool;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    }
}
```

Une seule chose a changé de nature : `proxy_pass` ne vise plus une adresse mais
un nom de groupe. C'est la bascule que tout proxy propose, sous d'autres
mots-clés. Et une configuration ne prouve rien tant que la répartition n'a pas
été **observée** : dix requêtes suffisent.

```bash
sudo nginx -t && sudo systemctl reload nginx
for i in $(seq 1 10); do curl -sS http://10.10.30.13:8008/; done
```

```text
reponse du serveur alpha
reponse du serveur beta
[... 8 lignes, alternance stricte ...]
```

Piège observé pendant ce test : lancée **pendant** le `reload`, la même boucle a
donné 8 réponses `alpha` pour 2 `beta`. Le temps du rechargement, deux
générations de processus de travail coexistent, chacune avec son propre compteur
de rotation. Mesurez une fois le rechargement terminé.

Second bénéfice, gratuit : arrêtons `beta`, puis relançons six requêtes.

```bash
pkill -f "http.server 9511"
for i in $(seq 1 6); do curl -sS http://10.10.30.13:8008/; done
```

Les six réponses viennent de `alpha`, **aucune erreur n'est renvoyée au client**,
et le proxy explique ce qu'il a fait :

```text
[error] connect() failed (111: Connection refused) ... upstream: "http://127.0.0.1:9511/"
[warn]  upstream server temporarily disabled while connecting to upstream ...
```

Le serveur défaillant est retiré du groupe automatiquement, puis réessayé plus
tard : la panne d'un backend devient invisible pour l'utilisateur.

### Les en-têtes X-Forwarded-For et X-Real-IP

C'est l'oubli le plus fréquent en production, et il ne se voit pas : tout
fonctionne, mais **les journaux applicatifs deviennent inutilisables**. Avec un
proxy en frontal, le backend n'ouvre plus de connexion avec le client mais avec
le proxy. Un backend qui affiche les en-têtes reçus le montre sans discussion,
ici une requête émise depuis `10.10.30.1` sans aucun `proxy_set_header` :

```text
Host: 127.0.0.1:9512
[... Connection, User-Agent, Accept ...]
127.0.0.1 - - [22/Jul/2026 16:33:29] "GET / HTTP/1.0" 200 -
```

Le backend croit que tous ses visiteurs viennent de `127.0.0.1` (dernière ligne,
son journal d'accès), et il a perdu le nom d'hôte demandé par le client. Avec les
trois directives de la configuration précédente, la même requête arrive ainsi :

```text
Host: 10.10.30.13
X-Real-IP: 10.10.30.1
X-Forwarded-For: 10.10.30.1
[... Connection, User-Agent, Accept ...]
```

| En-tête | Ce qu'il transporte |
|---|---|
| `Host` | le nom d'hôte demandé par le client, sinon le backend voit l'adresse du groupe |
| `X-Real-IP` | l'adresse du client immédiat |
| `X-Forwarded-For` | la chaîne des adresses traversées, à laquelle chaque proxy ajoute la sienne |

La variable `$proxy_add_x_forwarded_for` **ajoute** l'adresse au `X-Forwarded-For`
existant au lieu de l'écraser, ce qui permet de remonter une chaîne de plusieurs
proxies. Corollaire de sécurité : n'importe quel client pouvant envoyer un
`X-Forwarded-For`, seule la valeur ajoutée par **votre** proxy de bordure est
digne de confiance.

### Remettre la machine en état

Une démonstration se défait entièrement, dans l'ordre : les processus, le
paquet, puis les deux réglages système.

```bash
pkill -f "http[.]server"
sudo systemctl stop nginx
sudo dnf remove -y nginx
sudo firewall-cmd --remove-port=8008/tcp
sudo setsebool httpd_can_network_connect off
```

Et surtout, on vérifie plutôt que de supposer :

```bash
sudo firewall-cmd --list-all          # ports: (vide), services: cockpit dhcpv6-client ssh
getsebool httpd_can_network_connect   # httpd_can_network_connect --> off
sudo semanage boolean -l -C           # aucune ligne httpd_*
ss -tlnp                              # seul le port 22 reste en écoute
```

Le pare-feu n'ayant été modifié qu'en runtime, `--permanent` n'a jamais bougé.
Le booléen SELinux, lui, doit être remis à `off` explicitement : désinstaller le
proxy ne le change pas. Même piège qu'une valeur `sysctl` posée à la main,
supprimer ce qui l'utilisait ne la réinitialise pas.
