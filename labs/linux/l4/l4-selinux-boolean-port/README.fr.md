# Lab — booléen SELinux et étiquetage de port

## Rappel

[**SELinux sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Sous SELinux enforcing, on accorde l'accès sans le désactiver. Les **booléens**
basculent des interrupteurs de policy prédéfinis — `setsebool -P <bool> on` les
rend persistants. L'**étiquetage de port** permet à un service confiné d'ouvrir un
port non standard — `semanage port -a -t <type> -p tcp <port>`. Lecture avec
`getsebool` et `semanage port -l`.

## Le cours

Les exemples ci-dessous portent sur le booléen `deny_ptrace` et sur un second
serveur SSH qu'on veut faire écouter sur le port `2222` : le challenge, lui, vous
demandera un autre booléen et un autre port. Apprenez la méthode, elle se
transpose telle quelle. Toutes les sorties reproduites ici ont été relevées sur
une VM **AlmaLinux 10** avec `policycoreutils-python-utils` 3.10 et `audit` 4.0.3.

### Vérifier que SELinux est bien en enforcing

Rien de ce qui suit n'a de sens si SELinux ne fait rien. Deux commandes :

```bash
getenforce
# Enforcing
sudo sestatus
```

```text
SELinux status:                 enabled
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
[...]
```

Les deux dernières lignes ne disent pas la même chose : **`Current mode`** est le
mode en vigueur maintenant, **`Mode from config file`** celui du prochain
démarrage. Un écart signale un `setenforce` passé à la main et jamais consolidé,
car `setenforce` ne touche que le mode courant :

```bash
sudo setenforce 0 && getenforce   # Permissive
sudo setenforce 1 && getenforce   # Enforcing
```

> **Ne modifiez pas `/etc/selinux/config` dans ce lab.** Une faute de frappe dans
> ce fichier peut rendre la machine non démarrable, et un passage par `disabled`
> impose un réétiquetage complet au redémarrage suivant, les fichiers créés sans
> SELinux n'ayant plus aucune étiquette. Le mode permissif se prend avec
> `setenforce 0` et se rend tout de suite avec `setenforce 1`.

### Trouver le bon booléen et lire son état

La politique `targeted` d'AlmaLinux 10 expose **314 booléens** (`getsebool -a |
wc -l`). On les cherche par mot-clé :

```bash
getsebool -a | grep ptrace
# deny_ptrace --> off
```

`getsebool` donne une valeur, `semanage boolean -l` donne le contexte complet :

```bash
sudo semanage boolean -l | grep deny_ptrace
```

```text
SELinux boolean                State  Default Description

deny_ptrace                    (off  ,  off)  Allow deny to ptrace
```

**Retenez ces deux colonnes entre parenthèses, tout le sujet est là** : la
première est l'**état courant** (celui que renvoie `getsebool`), la seconde
l'**état enregistré dans la politique**, rechargé au prochain démarrage. Tant
qu'elles sont identiques, tout va bien.

### Le piège : `setsebool` sans `-P` ne survit pas au redémarrage

Activons le booléen sans `-P`. L'effet est immédiat et bien réel : `strace` ne
peut plus tracer personne.

```bash
time sudo setsebool deny_ptrace on
# real  0m0.019s
getsebool deny_ptrace
# deny_ptrace --> on
strace -c -f /bin/true
# strace: ptrace(PTRACE_TRACEME, ...): Permission denied
```

Mais les deux colonnes ont divergé, et `-C`, qui n'affiche que les
**modifications locales enregistrées**, ne renvoie **rien du tout** :

```bash
sudo semanage boolean -l | grep deny_ptrace
# deny_ptrace                    (on   ,  off)  Allow deny to ptrace
sudo semanage boolean -l -C
# (aucune ligne)
```

Courant `on`, politique `off` : un changement absent de `-C` n'existe que dans la
mémoire du noyau. Redémarrage :

```bash
sudo systemctl reboot
# puis, une fois reconnecté :
getsebool deny_ptrace
# deny_ptrace --> off
```

Perdu. Le service qui dépendait de ce booléen retombera en échec des semaines
plus tard, et personne ne fera le lien.

Avec `-P`, le changement est écrit dans le magasin de politique :

```bash
time sudo setsebool -P deny_ptrace on
# real  0m0.326s
sudo semanage boolean -l -C
# deny_ptrace                    (on   ,   on)  Allow deny to ptrace
```

Les deux colonnes concordent, et la modification est maintenant visible dans
`-C`. Après un second redémarrage, `getsebool deny_ptrace` répond toujours `on`.

Sur cette VM, `-P` coûte **environ 0,33 s contre 0,02 s** sans, soit une quinzaine
de fois plus : il réécrit la politique, là où la version volatile n'écrit qu'un
octet dans `/sys/fs/selinux`. Sur une machine plus lente ou plus chargée, l'écart
se compte en secondes, et c'est ce délai qui pousse à oublier le `-P`.

Enfin, `setsebool -P <bool> off` remet la bonne valeur mais **laisse la trace dans
`-C`**. `semanage boolean` n'a pas de `-d` ; c'est `-D`, qui supprime toutes les
personnalisations locales de booléens, qui la fait disparaître :

```bash
sudo setsebool -P deny_ptrace off
sudo semanage boolean -l -C     # deny_ptrace y figure encore, en (off , off)
sudo semanage boolean -D
sudo semanage boolean -l -C     # vide
```

### Étiqueter un port avec `semanage port`

Un domaine confiné ne peut ouvrir que les ports dont le **type** lui est
autorisé. On lit d'abord ce que la politique connaît déjà :

```bash
sudo semanage port -l | grep ssh_port_t
# ssh_port_t                     tcp      22
sudo semanage port -l | grep 2222
# (rien : 2222 n'est associé à aucun type)
```

On ajoute le port au type voulu :

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo semanage port -l | grep ssh_port_t
# ssh_port_t                     tcp      2222, 22
```

**`-C` est l'option à retenir** : elle n'affiche que ce que vous avez ajouté
vous-même, ce qui permet de retrouver ses propres modifications au milieu des
466 lignes de la politique.

```bash
sudo semanage port -l -C
```

```text
SELinux Port Type              Proto    Port Number

ssh_port_t                     tcp      2222
```

Quand le port appartient déjà à un autre type, `-a` ne s'arrête pas : il prévient
et bascule tout seul en modification.

```bash
sudo semanage port -a -t ssh_port_t -p tcp 3306
# Port tcp/3306 already defined, modifying instead
```

Un `-m` à la place du `-a` fait la même chose, sans message.
Prenez l'habitude d'employer `-m` quand vous savez le port déjà défini : c'est
explicite, et sur les versions plus anciennes de `policycoreutils`, `-a` échoue
là où `-m` passe. Attention aussi à la lecture de `semanage port -l` après un tel
ajout : le port apparaît **sous les deux types**, l'entrée d'origine et la vôtre.
Seul `-l -C` lève l'ambiguïté.

Le retrait se fait avec `-d`, et ne concerne que vos ajouts :

```bash
sudo semanage port -d -t ssh_port_t -p tcp 3306   # retire votre modification locale
sudo semanage port -d -t ssh_port_t -p tcp 22
# ValueError: Port tcp/22 is defined in policy, cannot be deleted
sudo semanage port -d -t ssh_port_t -p tcp 2223
# ValueError: Port tcp/2223 is not defined
sudo semanage port -m -t ssh_port_t -p tcp 2224
# ValueError: Port tcp/2224 is not defined
```

Dernier point : `semanage` écrit toujours dans le magasin de politique. Il n'y a
pas d'équivalent volatile pour les ports, un étiquetage survit donc au
redémarrage sans qu'on ait rien à demander, contrairement aux booléens.

### « Permission denied » alors que rien ne le justifie

Pour éprouver tout cela, faisons écouter un second `sshd` sur le port `2222`,
sans toucher au service en place :

```bash
sudo tee /etc/systemd/system/sshd-demo.service <<'EOF'
[Service]
ExecStart=/usr/sbin/sshd -D -e -p 2222 -o PidFile=/run/sshd-demo.pid
EOF
sudo systemctl daemon-reload && sudo systemctl start sshd-demo.service
```

Avant l'étiquetage, le service tombe :

```text
Active: failed (Result: exit-code)
sshd[1412]: Bind to port 2222 on 0.0.0.0 failed: Permission denied.
sshd[1412]: Cannot bind any address.
systemd[1]: sshd-demo.service: Main process exited, code=exited, status=255/EXCEPTION
```

**`Permission denied` alors que le service tourne en root**, sur un port
supérieur à 1024, avec un binaire et une configuration parfaitement lisibles.
Aucun droit Unix n'explique ce refus, et le pare-feu non plus : il filtre les
paquets entrants, il n'empêche pas un processus local de réserver un port.

Un piège de méthode au passage : lancé **à la main**, le même serveur démarre
sans broncher.

```bash
sudo /usr/sbin/sshd -p 2222 -e -o PidFile=/run/sshd-demo.pid   # aucune erreur
ps -eZ | grep sshd
# system_u:system_r:sshd_t:s0-s0:c0.c1023                1101 ? sshd
# unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023  1285 ? sshd
```

Il hérite du contexte `unconfined_t` de votre shell : pas confiné, donc pas
refusé. Seul **systemd** opère la transition vers `sshd_t`. Un test « à la main »
ne prouve donc rien sur le service : passez toujours par `systemctl`.

Une fois le port étiqueté, le service démarre :

```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo systemctl restart sshd-demo.service
sudo ss -tlnp | grep 2222
# LISTEN 0 128 0.0.0.0:2222 0.0.0.0:* users:(("sshd",pid=1718,fd=7))
```

Le port est ouvert **localement**. Une connexion depuis une autre machine échoue
pourtant encore, avec un `bash: connect: No route to host` : c'est `firewalld`
qui rejette le paquet, et il faut `sudo firewall-cmd --add-port=2222/tcp`. Les
deux couches sont indépendantes et se dépannent séparément : SELinux autorise le
processus à **réserver** le port, le pare-feu autorise le trafic à **l'atteindre**.

### Lire le refus : l'AVC

Le refus est journalisé par `auditd`, et `sudo ausearch -m AVC -ts recent` le
relit :

```text
type=AVC msg=audit(1784736098.894:318): avc:  denied  { name_bind } for  pid=1412
  comm="sshd" src=2222 scontext=system_u:system_r:sshd_t:s0-s0:c0.c1023
  tcontext=system_u:object_r:unreserved_port_t:s0 tclass=tcp_socket permissive=0
```

Cinq champs suffisent à décider :

| Champ | Valeur ici | Ce qu'il dit |
|---|---|---|
| `denied { … }` | `name_bind` | l'opération refusée : réserver un port |
| `comm` / `src` | `sshd` / `2222` | qui, et sur quoi |
| `scontext` | `sshd_t` | le type **source**, celui du processus |
| `tcontext` | `unreserved_port_t` | le type **cible**, celui du port aujourd'hui |
| `permissive` | `0` | le refus a **bloqué** ; `1` aurait dit « journalisé mais laissé passer » |

C'est `tcontext` qui donne la réparation : le port porte `unreserved_port_t`
alors que `sshd_t` attend `ssh_port_t`. Il ne manque donc rien d'autre qu'un
`semanage port -a`.

Le champ `permissive` se vérifie facilement : après `setenforce 0`, la même
tentative réussit et l'AVC est journalisé avec `permissive=1`. C'est l'intérêt du
mode permissif pour un diagnostic, et aussi pourquoi « ça marche en permissif »
n'est pas une solution, seulement un test.

Deux avertissements de terrain :

- **`sealert` n'est pas disponible ici** : `rpm -q setroubleshoot-server` répond
  `package setroubleshoot-server is not installed`. Sur une image minimale, ne
  comptez pas dessus, sachez lire l'AVC brut ;
  `sudo grep AVC /var/log/audit/audit.log` donne les mêmes lignes.
- Dans un **script** ou via `ssh machine 'commande'`, l'entrée standard est un
  tuyau : `ausearch` lit dedans au lieu de lire les journaux et répond
  `<no matches>` alors que les refus existent. Ajoutez alors `--input-logs`.

Méfiez-vous enfin des suggestions automatiques. Sur ce refus précis,
`ausearch -m AVC -ts recent | audit2why` conclut :

```text
	Was caused by:
	The boolean nis_enabled was set incorrectly.
	Allow access by executing:
	# setsebool -P nis_enabled 1
```

Cette commande ferait bien disparaître le refus, en autorisant `sshd` à ouvrir
**n'importe quel** port non réservé. Étiqueter le seul port voulu est infiniment
plus précis. `audit2why` désigne un chemin, il ne choisit pas le bon.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Le booléen est bon aujourd'hui, faux après reboot | `setsebool` lancé sans `-P` ; vérifier les deux colonnes de `semanage boolean -l` |
| `semanage boolean -l -C` est vide alors qu'on vient de changer un booléen | le changement est volatile, il n'a pas été écrit dans la politique |
| `Permission denied` au démarrage d'un service, en root, sur un port libre | port non étiqueté ; lire `tcontext` dans l'AVC |
| Le service démarre à la main mais pas via `systemctl` | lancé à la main il reste `unconfined_t` ; seul systemd fait la transition |
| `Port tcp/N already defined, modifying instead` | le port appartient déjà à un type ; employer `-m` explicitement |
| `ValueError: Port tcp/N is defined in policy, cannot be deleted` | `-d` ne retire que vos ajouts, pas les entrées d'origine |
| `ValueError: Port tcp/N is not defined` | `-m` et `-d` exigent un port déjà défini ; utiliser `-a` pour créer |
| Le service écoute (`ss -tlnp`) mais reste injoignable | ce n'est plus SELinux : voir `firewall-cmd --list-ports` |
| `ausearch` répond `<no matches>` depuis un script | ajouter `--input-logs` |
| `sealert: command not found` | `setroubleshoot-server` absent ; lire l'AVC brut |

Pour tout défaire, puis prouver le retour à l'état d'origine : les trois
dernières commandes doivent renvoyer deux listes vides et `Enforcing`.

```bash
sudo systemctl stop sshd-demo.service
sudo rm -f /etc/systemd/system/sshd-demo.service && sudo systemctl daemon-reload
sudo semanage port -d -t ssh_port_t -p tcp 2222
sudo setsebool -P deny_ptrace off && sudo semanage boolean -D
sudo firewall-cmd --reload

sudo semanage port -l -C
sudo semanage boolean -l -C
getenforce
```
