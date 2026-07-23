# Lab — récupérer une config sshd cassée

## Rappel

[**Perte d'accès SSH sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/)

sshd lit `/etc/ssh/sshd_config` et les drop-ins de `/etc/ssh/sshd_config.d/`.
`sshd -t` valide la config hors ligne — une config cassée ne mord qu'au prochain
reload/reboot, donc lance **toujours** `sshd -t` avant de recharger. `sshd -T`
affiche les réglages effectifs. `systemctl reload sshd` applique une config
valide sans couper les connexions.

## Le cours

Les exemples ci-dessous portent sur un compte jetable nommé `depanne`, sur un
fichier `60-atelier.conf` et sur la directive `LoginGraceTime` : le challenge,
lui, vous fera travailler sur un autre fichier et une autre directive. Ce que
vous devez emporter d'ici est une **méthode de diagnostic**, pas une ligne à
recopier.

Toutes les sorties ont été relevées sur une AlmaLinux 10.2, OpenSSH_9.9p1,
SELinux en `Enforcing`.

> **Avertissement.** Apprendre à réparer un accès SSH suppose d'en casser un.
> Deux règles rendent l'exercice sûr, et elles ne se négocient pas. D'abord,
> ouvrez une **seconde session** avant de commencer et gardez-la ouverte : une
> session déjà établie survit à tout, c'est votre unique porte. Ensuite, cassez
> l'accès d'un **compte que vous venez de créer**, jamais le vôtre : toutes les
> pannes de ce cours ont été reproduites sur `depanne`, sans jamais mettre en
> jeu la session de travail.

### Qualifier le refus avant de toucher au serveur

Le message du client trie déjà les causes en trois familles, qui n'ont ni le
même coupable ni la même procédure.

| Ce que dit le client | Signification | Coupable probable |
|---|---|---|
| `Connection refused` | le serveur répond, mais **rien n'écoute** sur ce port | `sshd` arrêté, ou à l'écoute ailleurs |
| `Connection timed out` | **aucune réponse**, les paquets sont jetés en silence | pare-feu, groupe de sécurité, machine éteinte |
| `Permission denied (publickey)` | la connexion **aboutit**, c'est l'**authentification** qui échoue | clé, droits de `authorized_keys`, ou compte |

Les deux premiers se reproduisent en une commande, sans rien casser :

```bash
ssh -o ConnectTimeout=5 -p 2222 depanne@127.0.0.1 true
ssh -o ConnectTimeout=5 depanne@10.255.255.1 true
```

```text
ssh: connect to host 127.0.0.1 port 2222: Connection refused
ssh: connect to host 10.255.255.1 port 22: Connection timed out
```

Un refus prouve que la machine est vivante et joignable : le réseau va bien, le
problème est sur le service. Un timeout ne dit rien du service. Vérifiez donc
d'abord qui écoute, et sur quel port :

```bash
sudo ss -tlnp | grep -E ':22\b'
```

```text
LISTEN 0      128          0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=1104,fd=7))
LISTEN 0      128             [::]:22           [::]:*    users:(("sshd",pid=1104,fd=8))
```

Le reste de ce cours traite la troisième colonne, la seule où le serveur ne
vous dit rien.

### Ne jamais modifier le fichier principal

`/etc/ssh/sshd_config` commence par `Include /etc/ssh/sshd_config.d/*.conf`.
Déposer un fichier à soi dans ce répertoire vaut mieux que d'éditer le fichier
principal : revenir en arrière se résume à supprimer le fichier, sans risque
d'abîmer l'original. Sauvegardez tout de même le répertoire avant :

```bash
sudo cp -a /etc/ssh/sshd_config.d /root/sshd_config.d.orig
```

Le numéro en tête du nom n'est pas décoratif. `sshd` retient, pour la plupart
des directives, la **première valeur rencontrée**, à l'inverse de `sudoers` où
c'est la dernière qui gagne. Comme l'`Include` est en tête du fichier principal,
les fichiers de `sshd_config.d/` sont lus avant lui, dans l'ordre lexical de
leurs noms. Mesuré avec deux fichiers déposés pour l'occasion :

```bash
sudo grep -r LoginGraceTime /etc/ssh/sshd_config.d/
sudo sshd -T | grep -i '^logingracetime'
```

```text
/etc/ssh/sshd_config.d/60-atelier.conf:LoginGraceTime 45
/etc/ssh/sshd_config.d/10-atelier.conf:LoginGraceTime 90
logingracetime 90
```

C'est bien `10-` qui l'emporte. Préfixez donc vos réglages d'un numéro **bas**
pour passer devant ceux de la distribution et de cloud-init, et ne concluez
jamais sans `sshd -T`.

### Valider avant d'appliquer

Une valeur invalide déposée dans un drop-in ne casse rien tout de suite : le
`sshd` en cours garde en mémoire la configuration qu'il a lue au démarrage.

```bash
sudo sshd -t; echo "code retour = $?"
systemctl is-active sshd
```

```text
/etc/ssh/sshd_config.d/60-atelier.conf line 2: invalid time value.
code retour = 255
active
```

Le message nomme le **fichier** et la **ligne** : c'est le diagnostic complet,
et il ne coûte rien. Notez au passage que `sshd -T` échoue avec exactement la
même erreur : tant que la configuration est invalide, vous ne pouvez plus lire
les valeurs effectives.

La mine est amorcée pour le prochain rechargement. `systemctl cat sshd.service`
montre pourquoi :

```text
ExecReload=/bin/kill -HUP $MAINPID
```

Un `reload` envoie un `SIGHUP`, sur lequel `sshd` se relance en relisant sa
configuration. Si celle-ci est invalide, le processus qui portait l'écoute
s'arrête : plus rien sur le port 22, et toute nouvelle connexion se prend un
`Connection refused`. Un reboot produit le même résultat. Votre session en
cours, elle, survit : elle est portée par un processus déjà forké.

D'où la séquence, dans cet ordre, à chaque modification :

```bash
sudo sshd -t                          # 1. syntaxe, silence = succès
sudo sshd -T | grep -i '<directive>'  # 2. valeur réellement effective
sudo systemctl reload sshd            # 3. reload, jamais restart
ssh utilisateur@serveur               # 4. NOUVELLE session de test
```

`reload` relit la configuration sans couper les sessions établies, `restart` les
tue. Pour vérifier un fichier isolé avant de le déposer, `sshd -t -f` accepte un
chemin :

```bash
sudo sshd -t -f /tmp/essai.conf; echo "code retour = $?"
```

```text
/tmp/essai.conf line 2: invalid time value.
code retour = 255
```

Dernier avertissement : `sshd -t` ne valide que la **grammaire**, jamais la
logique d'accès. Un `AllowUsers` qui vous oublie passe `sshd -t` avec un code 0.

### Un seul message client, trois raisons serveur

C'est le cœur du sujet. Quatre pannes sans rapport entre elles ont été
provoquées sur le compte `depanne`, et le client dit presque toujours la même
chose. Le serveur, lui, sait exactement pourquoi :

| Panne provoquée | Ce que voit le client | Ce que dit `journalctl -u sshd` |
|---|---|---|
| `~/.ssh` en `770` | `Permission denied (publickey,...)` | `Authentication refused: bad ownership or modes for directory /home/depanne/.ssh` |
| shell du compte inexistant | `Permission denied (publickey,...)` | `User depanne not allowed because shell /sbin/pas-de-shell does not exist` |
| compte hors `AllowUsers` | `Permission denied (publickey,...)` | `User depanne from 127.0.0.1 not allowed because not listed in AllowUsers` |
| `authorized_keys` absent | `Permission denied (publickey,...)` | *(aucune ligne explicite)* `Connection closed by authenticating user depanne` |
| compte expiré (`chage -E`) | `Connection closed by 127.0.0.1 port 22` | `fatal: Access denied for user depanne by PAM account configuration` |

Trois enseignements. Le premier : **le message client n'est pas un diagnostic**,
c'est un accusé de refus. Le serveur reste volontairement vague pour ne rien
apprendre à qui sonderait les comptes. Le deuxième : la dernière ligne est
l'exception qui confirme la règle, un refus **PAM** intervient après la
validation de la clé et produit un autre message. Le troisième : une clé
simplement absente ne laisse **aucune** trace explicite, elle se déduit du
silence.

D'où l'ordre de diagnostic, du plus bavard au plus détaillé :

**1. Le journal du serveur**, toujours en premier, c'est lui qui a la réponse :

```bash
sudo journalctl -u sshd --since '-2min' --no-pager
```

```text
Jul 22 17:15:19 atelier.lab sshd-session[3448]: Authentication refused: bad ownership or modes for directory /home/depanne/.ssh
Jul 22 17:15:19 atelier.lab sshd-session[3448]: Connection closed by authenticating user depanne 127.0.0.1 port 54018 [preauth]
```

Notez le nom du processus : `sshd-session`, et non `sshd`. Depuis OpenSSH 9.8 la
session est portée par un binaire séparé. Filtrer sur la chaîne `sshd` raterait
la ligne ; `journalctl -u sshd` suit l'unité, processus enfants compris.

**2. `ssh -vvv` côté client**, quand le journal ne suffit pas. Sur la même panne :

```bash
ssh -vvv -i ~/.ssh/depanne_key depanne@127.0.0.1 true 2>&1 | grep -iE 'Offering|continue|denied'
```

```text
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic
debug1: Offering public key: /home/ansible/.ssh/depanne_key ED25519 SHA256:ZXi+Vtuh7NQzQ2ZPpg4jg6JqQxUHjhuBFeqQ5fBuEVc explicit
depanne@127.0.0.1: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

Le client dit **quelle** clé il a proposée et dans quel ordre, jamais pourquoi
elle a été rejetée. C'est utile quand on soupçonne que ce n'est pas la bonne clé
qui part, inutile pour tout le reste.

**3. `sshd -T`** en dernier, pour confronter ce que vous croyez avoir configuré
à ce que `sshd` applique vraiment. Exemple sur la liste blanche :

```bash
sudo sshd -T | grep -iE '^(allowusers|strictmodes)'
```

```text
allowusers ansible
allowusers student
strictmodes yes
```

Une liste blanche se rédige en y mettant **d'abord** les comptes dont vous
dépendez, et elle se teste sur un compte jetable. Une fois rechargée, `depanne`
est refusé alors que sa clé et ses droits sont parfaits.

> **Un piège d'OpenSSH 9.8 et suivants.** Après quelques échecs d'authentification
> rapprochés, la source est mise en pénalité et les connexions suivantes sont
> coupées avant même l'authentification, avec un message trompeur :
> `kex_exchange_identification: read: Connection reset by peer`. Le journal dit
> `drop connection ... penalty: failed authentication`. En pleine séance de
> diagnostic, on croit avoir aggravé la panne. Les paramètres sont visibles avec
> `sshd -T | grep -i persource` ; sur la machine d'essai la pénalité était
> retombée en moins de vingt secondes.

### La règle exacte des droits, mesurée

Les pannes de droits sont les plus fréquentes, et l'approximation courante
(« 600 et 700, sinon ça ne marche pas ») est fausse. Voici ce qui a été mesuré,
cas par cas, sur le compte d'essai :

| État de `~depanne/.ssh` et de `authorized_keys` | Résultat |
|---|---|
| répertoire `700 depanne` / fichier `600 depanne` | acceptée |
| répertoire `750 depanne` / fichier `600` | acceptée |
| répertoire `755 depanne` / fichier `600` | acceptée |
| répertoire `770 depanne` (écriture par le groupe) | **refusée** |
| répertoire `700 root:root` | **refusée** |
| fichier `644 depanne` | acceptée |
| fichier `664 depanne` (écriture par le groupe) | **refusée** |
| fichier `606 depanne` (écriture par les autres) | **refusée** |
| fichier `600 root:root` | **refusée** |
| **home** `/home/depanne` en `770` | **refusée** |

Ce que ce tableau établit : `sshd` refuse dès qu'un **autre compte que le
propriétaire peut écrire**, ou dès que le propriétaire n'est pas le bon. Un
fichier seulement **lisible** par tous passe encore, et le contrôle remonte
jusqu'au **répertoire personnel**, ce qu'on oublie presque toujours. Ce n'est
pas une raison pour laisser un `644` : `700` sur le répertoire et `600` sur le
fichier restent la cible, parce que c'est ce que tout audit vérifie. Mais quand
vous diagnostiquez, cherchez d'abord un **droit d'écriture** ou un
**propriétaire** de travers.

Le journal distingue d'ailleurs deux situations que le client confond :

```text
Authentication refused: bad ownership or modes for directory /home/depanne/.ssh
Could not open user 'depanne' authorized keys '/home/depanne/.ssh/authorized_keys': Permission denied
```

La première ligne est le refus de `StrictModes` sur des droits trop larges. La
seconde apparaît quand le fichier ou son répertoire appartient à **root** :
`sshd` abandonne ses privilèges pour lire le fichier au nom de l'utilisateur, et
n'y arrive plus. La correction, dans les deux cas :

```bash
sudo chown -R depanne:depanne /home/depanne/.ssh
sudo chmod 700 /home/depanne/.ssh
sudo chmod 600 /home/depanne/.ssh/authorized_keys
sudo restorecon -Rv /home/depanne/.ssh
```

### Quand plus aucune session ne passe

Si le service est tombé et que vous n'avez plus de session ouverte, aucune
commande de ce cours n'est accessible : il faut une console, c'est-à-dire un
accès qui ne dépend pas de `sshd`.

- **La console de l'hyperviseur ou du fournisseur.** Sur une machine libvirt,
  `virsh list --all` puis `virsh console <domaine>` donnent un terminal série.
  Chez un hébergeur, c'est la « console VNC » ou « console série » de l'interface
  d'administration.
- **Le mode urgence**, quand la machine ne va même plus jusqu'à la connexion :
  au menu GRUB, `e` puis `systemd.unit=emergency.target` sur la ligne du noyau.
  Les cibles existent bien (`systemctl list-units --type=target --all` liste
  `rescue.target` et `emergency.target`).
- **Le montage du disque depuis une autre machine**, en dernier recours : on
  attache le disque à un système sain, on corrige `/etc/ssh/sshd_config.d/`, on
  détache.

Ces trois voies n'ont pas été exécutées pour rédiger ce cours : la machine
d'essai est restée joignable du début à la fin, précisément parce que les pannes
ont été provoquées sur un compte tiers. Retenez surtout que la meilleure console
est celle dont on n'a pas besoin : une seconde session ouverte pendant la
manipulation coûte trois secondes et évite le déplacement.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `Connection refused` | `sshd` arrêté, ou config invalide relue au dernier reload | `systemctl is-active sshd`, `sudo sshd -t` |
| `Connection timed out` | pare-feu, ou machine éteinte | `firewall-cmd --list-all` depuis la console |
| `Permission denied (publickey)`, journal `bad ownership or modes` | droits trop larges sur `~/.ssh`, le fichier ou le home | `stat -c '%a %U:%G' ~/.ssh ~/.ssh/authorized_keys` |
| `Permission denied (publickey)`, journal `Could not open ... Permission denied` | propriétaire root sur le fichier ou le répertoire | `chown -R <user>:<user> ~<user>/.ssh` |
| `Permission denied (publickey)`, journal `not listed in AllowUsers` | liste blanche côté serveur | `sudo sshd -T \| grep -i allowusers` |
| `Access denied ... by PAM account configuration` | compte expiré ou verrouillé | `chage -l <user>`, `passwd -S <user>` |
| réglage sans effet | une autre occurrence, lue avant, l'emporte | `sudo sshd -T`, puis `grep -r` dans `sshd_config.d/` |
| `Connection reset by peer` en rafale | pénalité `PerSourcePenalties` après des échecs | `sudo sshd -T \| grep -i persource`, attendre |
| `sshd -t` vert mais le service refuse de démarrer | port non standard, SELinux, clé d'hôte | `journalctl -u sshd -n 20`, `ausearch -m avc -ts recent` |

Le cas du port non standard bloqué par SELinux, classique du RHCSA, est traité
en détail dans le guide compagnon lié plus haut.

Pour tout défaire après un exercice de ce genre :

```bash
sudo rm -f /etc/ssh/sshd_config.d/60-atelier.conf
sudo sshd -t && sudo systemctl reload sshd
sudo userdel -r depanne
ssh utilisateur@serveur          # une NOUVELLE session, la seule preuve qui vaille
```
