# Lab — pare-feu Debian avec ufw

## Rappel

[**ufw sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/)

`ufw allow <service|port>` ajoute une règle ; `ufw enable` active le pare-feu et le
rend persistant au boot ; `ufw status` montre les règles. C'est le pendant Debian
de `firewall-cmd`. Garde toujours `OpenSSH` autorisé avant d'activer.

## Le cours

Les exemples ci-dessous ouvrent un service de supervision sur `9100/tcp` et une
base PostgreSQL sur `5432/tcp` : le challenge, lui, vous demandera un autre
service. Apprenez l'enchaînement autoriser / activer / vérifier / défaire, ne
recopiez pas une ligne. Sorties réelles d'une Ubuntu 24.04.4 LTS, `ufw 0.36.2-6`.

### Où en est ufw sur cette machine

Avant de poser la moindre règle, relevez l'état que vous devrez savoir rendre :
il cache un piège.

```bash
sudo ufw status ; systemctl is-enabled ufw ; systemctl is-active ufw
grep ^ENABLED /etc/ufw/ufw.conf ; sudo iptables -S
```

```text
Status: inactive
enabled
active
ENABLED=no
-P INPUT ACCEPT
-P FORWARD ACCEPT   [...]
```

Lisez bien : l'unité systemd `ufw.service` est **`enabled` et `active`**, alors
que `ufw status` répond **`inactive`**. Ce sont deux notions distinctes. L'unité
n'est qu'un lanceur ; l'état réel du pare-feu vit dans `ENABLED` de
`/etc/ufw/ufw.conf`, que seuls `ufw enable` et `ufw disable` écrivent. D'où la
conséquence pratique : **`systemctl status ufw` ne dira jamais si le pare-feu
filtre**. La seule réponse fiable est `ufw status`, confirmée par les trois
politiques `iptables` en `ACCEPT`. Ubuntu livre ufw installé mais désarmé : c'est
votre point de comparaison.

### La règle d'or : autoriser SSH avant d'activer

La politique par défaut d'ufw est `deny incoming` : à l'activation, **tout ce qui
n'est pas explicitement autorisé tombe**, y compris le port 22. Sur un serveur
distant, l'ordre des deux commandes suivantes décide donc si vous gardez votre
accès. D'abord la règle, ensuite l'activation :

```bash
sudo ufw allow OpenSSH
sudo ufw show added
```

```text
Rules updated
Added user rules (see 'ufw status' for running firewall):
ufw allow OpenSSH
```

Tant qu'ufw est inactif, les règles ne filtrent rien : elles s'empilent dans une
file d'attente que `ufw show added` affiche, et seront appliquées d'un bloc à
l'activation. C'est ce qui rend la préparation sans risque.

```bash
sudo ufw enable ; sudo ufw status verbose
```

```text
Command may disrupt existing ssh connections. Proceed with operation (y|n)? y
Firewall is active and enabled on system startup
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
22/tcp (OpenSSH)           ALLOW IN    Anywhere
[...]
```

L'avertissement n'est pas décoratif : contrôlez toujours depuis une **nouvelle**
connexion, pas seulement dans le terminal déjà ouvert.

> **Ce que donne l'erreur inverse.** En rédigeant ce cours, la règle SSH a été
> supprimée alors qu'ufw était encore actif. La session en cours a survécu, ufw
> laissant vivre les connexions établies ; la **suivante** est morte en silence :
> `ssh: connect to host ... port 22: Connection timed out`. Ni refus ni message,
> le paquet est jeté, et aucun second compte ne rattrape cela puisque `student`
> passe par le même port 22. Il a fallu éteindre la machine côté hyperviseur pour
> réécrire `ENABLED=no` dans le disque. **Sans console de secours, cette erreur
> est définitive.**

Deux réflexes en découlent. Gardez **une seconde session SSH ouverte** avant de
toucher au pare-feu : elle survivra à une bêtise et vous laissera taper
`sudo ufw disable`. Et si SSH est exposé sur Internet, préférez `ufw limit 22/tcp`
à `allow` : d'après le guide, `limit` bloque une source au delà de six connexions
par trente secondes.

### Ce que ufw fabrique réellement dans netfilter

ufw n'est pas un pare-feu : c'est une **façade** qui écrit des règles netfilter.

```bash
sudo iptables -S | wc -l
sudo iptables -S INPUT
sudo iptables -S ufw-user-input
update-alternatives --display iptables | sed -n '3p'
sudo nft list tables
```

```text
101
-P INPUT DROP
-A INPUT -j ufw-before-logging-input
[...]
-A ufw-user-input -p tcp -m tcp --dport 22 -m comment --comment "\'dapp_OpenSSH\'" -j ACCEPT
  link currently points to /usr/sbin/iptables-nft
# Warning: table ip filter is managed by iptables-nft, do not touch!
```

Trois lignes avant l'activation, cent une après. La politique `INPUT` est passée
de `ACCEPT` à `DROP` et la chaîne ne fait plus que déléguer à une douzaine de
chaînes `ufw-*` ; vos règles à vous atterrissent dans une seule d'entre elles,
`ufw-user-input`. Sur Ubuntu 24.04, `iptables` est d'ailleurs `iptables-nft` :
tout cela finit dans nftables, qui le signale lui-même. D'où la mise en garde du
guide : **ne mélangez jamais ufw et des règles iptables posées à la main**. Une
règle manuelle insérée dans `INPUT` passerait avant les chaînes `ufw-*` et
contredirait en silence l'affichage de `ufw status`, qui ne connaît que ce qu'ufw
a écrit. Pour prévisualiser une règle sans l'appliquer : `ufw --dry-run allow …`.

### Les profils d'application

C'est la particularité d'ufw face à firewalld, et ce que l'examen attend. Un
**profil** est un fichier déposé dans `/etc/ufw/applications.d/` par le paquet qui
installe le service. Créez-en un :

```bash
sudo tee /etc/ufw/applications.d/atelier-exporter <<'EOF'
[Exporteur]
title=Exporteur de metriques
description=Agent de collecte interroge par le superviseur
ports=9100/tcp
EOF
sudo ufw app list ; sudo ufw app info Exporteur
```

```text
Available applications:
  Exporteur
  OpenSSH
Profile: Exporteur
Title: Exporteur de metriques
[...]
Port:
  9100/tcp
```

La règle s'écrit alors avec le nom du profil, plus lisible qu'un numéro de port :

```bash
sudo ufw allow Exporteur ; sudo ufw allow postgresql ; sudo ufw status
```

```text
To                         Action      From
OpenSSH                    ALLOW       Anywhere
Exporteur                  ALLOW       Anywhere
5432/tcp                   ALLOW       Anywhere
```

Ces deux `allow` n'ont pas le même mécanisme, et la sortie le trahit.
`postgresql` est un nom de **service** résolu une fois pour toutes via
`/etc/services` (`grep ^postgresql /etc/services` renvoie `postgresql 5432/tcp`) :
il devient `5432/tcp` dans le statut, le nom est perdu. `Exporteur` est un
**profil** : il reste nommé, sa définition étant relue depuis le fichier. D'où
une conséquence : modifier un profil déjà utilisé ne suffit pas.

```bash
sudo sed -i 's|^ports=9100/tcp|ports=9100,9101/tcp|' /etc/ufw/applications.d/atelier-exporter
sudo ufw app update Exporteur
sudo ufw reload
sudo iptables -S ufw-user-input | grep Exporteur
```

```text
Rules updated for profile 'Exporteur'
Skipped reloading firewall
Firewall reloaded
-A ufw-user-input -p tcp -m multiport --dports 9100,9101 -m comment --comment "\'dapp_Exporteur\'" -j ACCEPT
```

`Skipped reloading firewall` est l'avertissement à ne pas manquer : `app update`
réécrit le fichier de règles mais **laisse le pare-feu en mémoire tel quel**. Sans
le `ufw reload`, la chaîne serait restée sur le seul port 9100.

### L'ordre des règles compte, et ufw le rend visible

`ufw status numbered` numérote les règles, et ce numéro est l'ordre réel
d'évaluation. Ajoutez une interdiction pour un poste précis **après** une
autorisation générale :

```bash
sudo ufw deny from 10.10.30.1 to any port 9100 proto tcp comment 'test ordre'
sudo ufw status numbered
```

```text
[ 1] OpenSSH                    ALLOW IN    Anywhere
[ 2] Exporteur                  ALLOW IN    Anywhere
[ 3] 5432/tcp                   ALLOW IN    Anywhere
[ 4] 9100/tcp                   DENY IN     10.10.30.1                 # test ordre
```

La règle est listée, et pourtant elle ne sert à rien. Preuve faite depuis
10.10.30.1, un service écoutant sur le port :

```bash
nc -zv 10.10.30.18 9100 ; sudo iptables -S ufw-user-input
```

```text
Connection to 10.10.30.18 9100 port [tcp/*] succeeded!
-A ufw-user-input -p tcp -m tcp --dport 9100 [...] -j ACCEPT
-A ufw-user-input -s 10.10.30.1/32 -p tcp -m tcp --dport 9100 -j DROP
```

netfilter lit de haut en bas et s'arrête au premier verdict : l'`ACCEPT` du
profil tranche avant que le `DROP` de la dernière ligne ne soit atteint. Une
règle de refus placée après une autorisation qui la couvre **ne s'applique
jamais**. Corrigez par insertion à un rang précis :

```bash
sudo ufw --force delete 4 ; sudo ufw status numbered
sudo ufw insert 1 deny from 10.10.30.1 to any port 9100 proto tcp comment 'test ordre'
```

```text
Rule inserted
[ 1] 9100/tcp                   DENY IN     10.10.30.1                 # test ordre
[ 2] OpenSSH                    ALLOW IN    Anywhere
[...]
```

Le même `nc` ne passe plus : il reste bloqué jusqu'à son délai d'attente (code de
sortie 124), sans message de refus, signature d'un `DROP`. Deux détails : les
numéros **se décalent** après chaque suppression, relisez `status numbered` entre
deux `delete` ; et `ufw delete allow Exporteur` marche aussi, plus sûr en script.

### Activer et persister sont la même commande

C'est la différence d'ergonomie avec firewalld, où il faut penser à
`--permanent`. Ici `ufw enable` fait les deux d'un coup : il écrit `ENABLED=yes`
dans `/etc/ufw/ufw.conf`, et les règles vivent dans `/etc/ufw/user.rules`
(`user6.rules` pour IPv6) :

```bash
sudo sed -n '/### RULES ###/,/### END RULES ###/p' /etc/ufw/user.rules
```

```text
### tuple ### deny tcp 9100 0.0.0.0/0 any 10.10.30.1 in comment=74657374206f72647265
-A ufw-user-input -p tcp --dport 9100 -s 10.10.30.1 -j DROP
### tuple ### allow tcp 22 0.0.0.0/0 any 0.0.0.0/0 OpenSSH - in
-A ufw-user-input -p tcp --dport 22 -j ACCEPT -m comment --comment 'dapp_OpenSSH'
```

Chaque règle y figure deux fois : la ligne `### tuple ###` est la forme qu'ufw
sait relire et renuméroter, la suivante est sa traduction netfilter. Les
commentaires sont encodés en hexadécimal (`74657374206f72647265` se décode en
`test ordre`). Ne vous y fiez pas pour autant : vérifiez par un redémarrage,
c'est ce que fait l'examen.

```bash
sudo systemctl reboot   # puis, une fois la machine revenue :
sudo ufw status numbered ; grep ^ENABLED /etc/ufw/ufw.conf
```

```text
Status: active
[ 1] 9100/tcp                   DENY IN     10.10.30.1                 # test ordre
[ 2] OpenSSH                    ALLOW IN    Anywhere
[...]
ENABLED=yes
```

État, règles **et ordre** sont revenus intacts, insertion en position 1 comprise.
Rien de plus à faire : pas de `--permanent`, pas de `systemctl enable`.

Dernier point, la trace. `ufw status verbose` affiche `Logging: on (low)`, mais
`/var/log/ufw.log` **n'existe pas** tant qu'aucun paquet n'a été journalisé :
c'est `rsyslog` qui le crée à la première ligne, via `/etc/rsyslog.d/20-ufw.conf`.
Une connexion vers un port fermé la déclenche, et y écrit une ligne
`[UFW BLOCK] ... SRC=10.10.30.1 DST=10.10.30.18 PROTO=TCP DPT=4444 SYN`. Attention
toutefois à ce que ce journal contient : au niveau `low`, seuls les paquets
bloqués par la **politique par défaut** y apparaissent. Le refus explicite posé
plus haut sur le port 9100 n'y a laissé aucune trace (`grep -c DPT=9100` renvoie
`0` quand `DPT=4444` en compte quatre). Un `ufw deny` filtre en silence ; passez
en `sudo ufw logging medium` si vous devez l'auditer.

### Dépannage et retour à l'état initial

| Symptôme | Cause probable | Solution |
|---|---|---|
| `ufw status` dit `inactive` alors que `systemctl is-active ufw` dit `active` | Deux notions distinctes : `ENABLED=no` dans `/etc/ufw/ufw.conf` | `sudo ufw enable`, jamais `systemctl start` |
| SSH tombe juste après `ufw enable` | Port 22 non autorisé, politique `deny incoming` | Console de secours, `sudo ufw disable`, corriger, réessayer |
| Une règle `deny` listée dans `status` ne bloque rien | Elle est placée après un `allow` qui la couvre | `sudo ufw status numbered`, puis `ufw delete N` et `ufw insert 1 ...` |
| Un profil modifié n'a aucun effet | `ufw app update` écrit le fichier sans recharger | `sudo ufw reload` |
| Le service reste injoignable alors que `status` semble bon | Règle `iptables` manuelle en amont des chaînes `ufw-*` | `sudo iptables -S INPUT`, et ne pas mélanger les deux outils |
| `/var/log/ufw.log` absent, ou règles invisibles dans `iptables -L` | Aucun paquet journalisé ; ufw écrit ses propres chaînes | Normal ; `ufw logging medium` et `iptables -S ufw-user-input` |

Pour tout défaire, **l'ordre est critique** : désactivez ufw **avant** de retirer
la règle SSH, jamais l'inverse.

```bash
sudo ufw disable                     # d'abord : plus rien ne filtre
sudo ufw delete allow Exporteur      # ensuite seulement, les regles
sudo ufw delete allow postgresql
sudo ufw delete deny from 10.10.30.1 to any port 9100 proto tcp
sudo ufw delete allow OpenSSH
sudo rm -f /etc/ufw/applications.d/atelier-exporter
```

Supprimée par sa description complète, une règle part sans confirmation ; par son
numéro, `ufw delete N` demande à valider. `ufw reset` fait tout cela d'un coup
mais efface **aussi** votre autorisation SSH : ne l'employez que devant une
console, et reposez `sudo ufw allow OpenSSH` dans la foulée. Vérifiez enfin le
retour au point de départ, en comparant avec la première section :

```bash
sudo ufw status ; sudo ufw show added ; sudo ufw app list ; sudo iptables -S
```

```text
Status: inactive
Added user rules (see 'ufw status' for running firewall):
(None)
Available applications:
  OpenSSH
-P INPUT ACCEPT
-P FORWARD ACCEPT   [...]
```

Un détail si vous comparez juste après le `disable` : les chaînes `ufw-*`, vidées
de leurs règles, **restent déclarées** jusqu'au prochain redémarrage.
`sudo iptables -S` renvoie alors une quarantaine de lignes de sauts, sans un seul
verdict. Ce sont les trois politiques `ACCEPT` qui font foi.
