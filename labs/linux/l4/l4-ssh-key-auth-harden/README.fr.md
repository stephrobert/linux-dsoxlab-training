# Lab — accès SSH par clé durci pour un utilisateur de service

## Rappel

[**Les clés SSH sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/)

`sshd` impose des permissions strictes sur les fichiers de clés : `~/.ssh` doit
être `0700` et détenu par l'utilisateur, `authorized_keys` doit être `0600` et
détenu par l'utilisateur. Trop ouvert, ou détenu par un autre, et la clé est
**ignorée en silence**. Lis-les avec `stat -c '%a %U:%G'`.

## Le cours

Les exemples ci-dessous portent sur un compte de service nommé `sonde` et sur
des clés fabriquées pour l'occasion. Le challenge, lui, vous fera travailler sur
un autre compte et d'autres fichiers : l'objectif est d'apprendre la méthode et
les réflexes de vérification, pas de recopier une ligne.

Toutes les sorties de ce cours ont été relevées sur une AlmaLinux 10,
OpenSSH_9.9p1, SELinux en `Enforcing`.

> **Avertissement.** Ce cours modifie la configuration du service par lequel
> vous êtes connecté. Avant toute modification de `sshd`, ouvrez une **seconde
> session** et gardez-la ouverte jusqu'à validation. C'est votre seul filet.

### Fabriquer une paire de clés

`ssh-keygen` produit deux fichiers indissociables : la **clé privée**, qui ne
quitte jamais la machine cliente, et la **clé publique** (`.pub`), qui est faite
pour être diffusée sur les serveurs.

```bash
ssh-keygen -t ed25519 -C "sonde@atelier"
```

```text
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/ansible/.ssh/id_ed25519):
Enter passphrase for "/home/ansible/.ssh/id_ed25519" (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/ansible/.ssh/id_ed25519
Your public key has been saved in /home/ansible/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:eIkhcUdYg2tDanqBuoN2taSnjSN+11IiQazjJ4P6bLw sonde@atelier
[...]
```

Trois questions, trois réponses : l'emplacement (Entrée pour le défaut), puis la
passphrase deux fois. Le guide recommande **Ed25519** depuis OpenSSH 6.5 : clé
plus courte, plus rapide, aussi sûre qu'un RSA 4096. On ne garde `-t rsa -b 4096`
que pour dialoguer avec des systèmes trop anciens pour Ed25519.

`ssh-keygen` pose lui-même les bons droits, ce qui se vérifie :

```bash
ls -l ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub
```

```text
-rw-------. 1 ansible ansible 399 Jul 22 16:25 /home/ansible/.ssh/id_ed25519
-rw-r--r--. 1 ansible ansible  95 Jul 22 16:25 /home/ansible/.ssh/id_ed25519.pub
```

`600` sur la privée, `644` sur la publique : c'est la règle, et elle est
respectée par défaut. Les problèmes commencent quand un fichier a voyagé (copie,
archive, `scp`) et a perdu ses droits en route.

### Installer la clé publique sur le compte cible

Deux méthodes, la même finalité : ajouter une ligne dans le fichier
`~/.ssh/authorized_keys` du compte visé, **sur le serveur**.

La méthode manuelle est celle attendue en examen, et la seule possible quand la
connexion par mot de passe est déjà fermée :

```bash
sudo install -d -o sonde -g sonde -m 700 /home/sonde/.ssh
echo 'ssh-ed25519 AAAA... sonde@atelier' | sudo tee -a /home/sonde/.ssh/authorized_keys
sudo chown sonde:sonde /home/sonde/.ssh/authorized_keys
sudo chmod 600 /home/sonde/.ssh/authorized_keys
sudo restorecon -Rv /home/sonde/.ssh
```

`install -d` pose le propriétaire et le mode en une seule fois, ce qui évite la
fenêtre pendant laquelle le répertoire existe encore avec de mauvais droits.
`restorecon` remet le contexte SELinux attendu (`ssh_home_t`) sur des fichiers
créés à la main : sur la machine d'essai le contexte était déjà correct et la
commande n'a rien affiché, mais le réflexe ne coûte rien.

L'autre méthode, `ssh-copy-id`, fait le même travail depuis le poste client :

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub sonde@127.0.0.1
```

Elle a l'avantage de ne pas se tromper sur les droits, ce que confirme la
lecture du script lui-même (`ssh-copy-id` est un script shell) :

```bash
grep -nE "mkdir|chmod" /usr/bin/ssh-copy-id | head -4
```

```text
333:	-mkdir "$AUTH_KEY_DIR"
334:	chmod 700 "$AUTH_KEY_DIR"
336:	chmod 600 "$AUTH_KEY_FILE"
```

Vérifiez toujours le résultat, puis la connexion :

```bash
sudo stat -c '%a %U:%G %n' /home/sonde/.ssh /home/sonde/.ssh/authorized_keys
ssh -i ~/.ssh/id_ed25519 sonde@127.0.0.1 'id -un'
```

```text
700 sonde:sonde /home/sonde/.ssh
600 sonde:sonde /home/sonde/.ssh/authorized_keys
sonde
```

### Les droits : la panne numéro un

Côté **client**, une clé privée lisible par d'autres est refusée par `ssh`
lui-même, avant même que le serveur ne soit consulté. Le message ne laisse aucun
doute :

```bash
chmod 644 ~/.ssh/id_ed25519
ssh -i ~/.ssh/id_ed25519 sonde@127.0.0.1
```

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/home/ansible/.ssh/id_ed25519' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/ansible/.ssh/id_ed25519": bad permissions
sonde@127.0.0.1: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

Correction : `chmod 600` sur la clé privée.

Côté **serveur**, `sshd` applique le même genre de contrôle, mais **sans rien
dire au client**. Voici ce qui a été mesuré, cas par cas, sur le compte d'essai :

| État de `~sonde/.ssh` et de `authorized_keys` | Résultat |
|---|---|
| `700 sonde:sonde` / `600 sonde:sonde` | connexion acceptée |
| répertoire `770 sonde:sonde` (écriture par le groupe) | **refusée** |
| répertoire `755 root:root` (mauvais propriétaire) | **refusée** |
| `authorized_keys` en `660` (écriture par le groupe) | **refusée** |
| `authorized_keys` en `644`, répertoire `700 sonde:sonde` | acceptée |

Ce que ce tableau apprend : `sshd` refuse dès qu'un **autre compte que le
propriétaire peut écrire** dans le répertoire ou dans le fichier, ou dès que le
répertoire n'appartient pas au bon utilisateur. Un `authorized_keys` seulement
**lisible** par tous passe encore. Ce n'est pas une raison pour le laisser
ainsi : `700` et `600` restent la cible, parce que c'est ce que tout audit
vérifie et parce que la marge d'erreur est nulle. Mais quand vous diagnostiquez,
cherchez d'abord un **droit d'écriture** ou un **propriétaire** de travers.

Le journal du serveur nomme précisément le coupable :

```text
Authentication refused: bad ownership or modes for directory /home/sonde/.ssh
Authentication refused: bad ownership or modes for file /home/sonde/.ssh/authorized_keys
```

### Lire la configuration effective avec `sshd -T`

C'est le point le plus important du durcissement, et le même principe que
`systemctl show` pour systemd : **le fichier ne dit pas la vérité, la commande
si**. `sshd -T` affiche la configuration telle que `sshd` la comprend, toutes
inclusions résolues.

La démonstration tient en deux commandes sur une AlmaLinux 10 sortie de son
installation :

```bash
sudo grep -n -iE '^#?PasswordAuthentication' /etc/ssh/sshd_config
sudo sshd -T | grep -i '^passwordauthentication'
```

```text
65:#PasswordAuthentication yes
passwordauthentication no
```

Le fichier principal semble annoncer `yes` (ligne commentée, donc le défaut
d'OpenSSH). La valeur réellement appliquée est `no`. Elle vient d'ailleurs :

```bash
sudo grep -r . /etc/ssh/sshd_config.d/ | grep -i password
```

```text
/etc/ssh/sshd_config.d/50-cloud-init.conf:PasswordAuthentication no
```

Qui aurait audité ce serveur en lisant `/etc/ssh/sshd_config` se serait trompé.
`sshd -T` demande les privilèges root, car il lit aussi les clés d'hôte.

### La première occurrence l'emporte

Sur RHEL, AlmaLinux, Debian et Ubuntu, `/etc/ssh/sshd_config` commence par :

```text
Include /etc/ssh/sshd_config.d/*.conf
```

Or `sshd` retient, pour la plupart des directives, la **première valeur
rencontrée**, à l'inverse de `sudoers` où c'est la dernière qui gagne. Comme
l'`Include` est en tête, les fichiers de `sshd_config.d/` sont lus **avant** le
corps du fichier principal, et dans l'ordre lexical de leurs noms.

Vérification, avec deux fichiers déposés pour l'occasion :

```bash
sudo grep -r MaxAuthTries /etc/ssh/sshd_config.d/
sudo sshd -T | grep -i '^maxauthtries'
```

```text
/etc/ssh/sshd_config.d/00-demo-atelier.conf:MaxAuthTries 4
/etc/ssh/sshd_config.d/99-demo-atelier.conf:MaxAuthTries 2
maxauthtries 4
```

C'est bien `00-` qui gagne. D'où deux règles de travail : préfixez vos réglages
d'un numéro **bas** (`00-hardening.conf`) pour passer devant les fichiers posés
par la distribution ou par cloud-init, et ne concluez jamais sans `sshd -T`.

Travailler dans un fichier à vous de `sshd_config.d/` plutôt que dans
`sshd_config` a un autre mérite : revenir en arrière se résume à supprimer ce
fichier, sans risque d'abîmer le fichier d'origine.

### Durcir sans se verrouiller dehors

L'ordre des gestes n'est pas négociable. `sshd -t` valide la **syntaxe** et
retourne 255 avec le nom du fichier et la ligne fautive :

```bash
sudo sshd -t; echo "code retour = $?"
```

```text
/etc/ssh/sshd_config.d/99-demo-atelier.conf: line 2: Bad configuration option: PermitRootLogn
/etc/ssh/sshd_config.d/99-demo-atelier.conf: terminating, 1 bad configuration options
code retour = 255
```

Une faute de frappe non détectée et le service refuse de redémarrer : vous
restez dehors dès que la session en cours tombe. Après correction, `sshd -t` ne
dit plus rien et retourne 0 : le silence est le succès.

La séquence complète, en quatre temps :

```bash
sudo sshd -t                                       # 1. syntaxe
sudo sshd -T | grep -iE 'allowusers|passwordauth'  # 2. valeurs effectives
sudo systemctl reload sshd                         # 3. reload, pas restart
ssh utilisateur@serveur                            # 4. NOUVELLE session de test
```

`reload` relit la configuration **sans couper les sessions établies** ; `restart`
les tue. Sur RHEL et AlmaLinux le service s'appelle `sshd`, sur Debian et Ubuntu
historiquement `ssh`.

Attention : `sshd -t` ne valide que la grammaire, jamais la logique d'accès. Un
`AllowUsers` qui vous oublie passe `sshd -t` sans broncher. Cette directive est
la liste blanche des comptes autorisés à se connecter, le réglage le plus
efficace du durcissement, donc aussi le plus dangereux :

```bash
# /etc/ssh/sshd_config.d/00-demo-atelier.conf
AllowUsers ansible student
```

```bash
sudo sshd -T | grep -i '^allowusers'
```

```text
allowusers ansible
allowusers student
```

Une fois rechargé, le compte `sonde`, absent de la liste, est refusé alors que sa
clé et ses droits sont parfaits. Testez toujours ce genre de règle sur un compte
d'essai, jamais sur celui qui vous sert à administrer la machine, et vérifiez
avant toute chose que les comptes dont vous dépendez figurent bien dans la
liste.

### Diagnostiquer un refus : le journal contre `ssh -vvv`

Un refus se lit des deux côtés, et les deux côtés ne disent pas la même chose.

Côté **client**, sur le refus provoqué par `AllowUsers` :

```bash
ssh -vvv -i ~/.ssh/id_ed25519 sonde@127.0.0.1 2>&1 | grep -iE 'Offering|continue|denied'
```

```text
debug1: Offering public key: /home/ansible/.ssh/id_ed25519 ED25519 SHA256:E8nYXqP... explicit
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic
sonde@127.0.0.1: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

Le client apprend seulement que sa clé a été proposée et que le serveur n'en a
pas voulu. **Ce message est exactement le même** que celui obtenu plus haut avec
un répertoire `.ssh` mal protégé : deux causes sans rapport, un seul message. Le
serveur reste volontairement vague, pour ne rien apprendre à un attaquant qui
sonderait les comptes.

Côté **serveur**, le journal donne la raison exacte :

```bash
sudo journalctl -u sshd --no-pager --since '-1min'
```

```text
sshd-session[4844]: User sonde from 127.0.0.1 not allowed because not listed in AllowUsers
sshd-session[4844]: Connection closed by invalid user sonde 127.0.0.1 port 58660 [preauth]
```

Notez le nom du processus : `sshd-session`, et non `sshd`. Depuis OpenSSH 9.8 la
session est portée par un binaire séparé. Un filtre trop strict sur le nom
`sshd` manquerait la ligne ; `journalctl -u sshd` reste la bonne porte d'entrée,
puisqu'il suit l'unité, processus enfants compris.

Ces deux vues sont complémentaires : `ssh -vvv` dit **quelle clé** a été
proposée et dans quel ordre, le journal dit **pourquoi** elle a été rejetée.

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `UNPROTECTED PRIVATE KEY FILE!` | clé privée trop permissive côté client | `chmod 600` sur la clé privée |
| `Permission denied (publickey)`, journal : `bad ownership or modes` | droits ou propriétaire de `~/.ssh` ou de `authorized_keys` | `stat -c '%a %U:%G'` sur les deux |
| `Permission denied (publickey)`, journal : `not listed in AllowUsers` | liste blanche côté serveur | `sshd -T \| grep -i allowusers` |
| réglage sans effet | une autre occurrence, lue avant, l'emporte | `sshd -T`, puis `grep -r` dans `sshd_config.d/` |
| `sshd -t` vert mais `restart` en échec | port, clé d'hôte, SELinux | `journalctl -u sshd -n 20` |

Dernier réflexe : `sshd -t` contrôle la grammaire, pas la capacité du service à
démarrer, et `sshd -T` dit ce que `sshd` croit, pas ce que le système fait.
Seule une **nouvelle connexion réussie** prouve que le durcissement est bon.
