# Lab — créer un compte local

## Rappel

[**Utilisateurs et groupes sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`useradd -u <uid> -m -d <home> -s <shell> -g <primaire> -G <secondaire> <nom>`
crée un compte avec une identité complète. Un utilisateur a **un seul groupe
primaire** (`-g`) et un nombre quelconque de **groupes secondaires** (`-G`).
Ensuite, `usermod -aG <groupe> <user>` ajoute un groupe : le `-a` est vital, sans
lui tu remplaces tous les groupes secondaires. `id` et `getent passwd`
inspectent le résultat.

## Le cours

Les exemples ci-dessous créent les comptes `lucien` et `hector` dans les groupes
`bureau`, `archives` et `impression` : le challenge, lui, vous demandera un autre
compte, un autre UID et d'autres groupes. Le but est d'apprendre la méthode et de
savoir la vérifier, pas de recopier une ligne.

Toutes les sorties de cette page ont été produites sur une VM **AlmaLinux 10**.
Sur Debian et Ubuntu, quelques chemins et quelques défauts diffèrent : ils sont
signalés au fil du texte.

### D'où viennent les valeurs par défaut de `useradd`

`useradd` ne décide presque rien tout seul. Il lit deux fichiers. Le premier est
**`/etc/default/useradd`**, que `useradd -D` ne fait que relire :

```bash
sudo useradd -D
```

```plaintext
HOME=/home
SHELL=/bin/bash
SKEL=/etc/skel
CREATE_MAIL_SPOOL=yes
[...]
```

Le reste de la politique vit dans **`/etc/login.defs`** :

```bash
grep -E '^(UID_MIN|UID_MAX|HOME_MODE|UMASK|USERGROUPS_ENAB|CREATE_HOME)' /etc/login.defs
```

```plaintext
UMASK		022
HOME_MODE	0700
UID_MIN                  1000
UID_MAX                 60000
USERGROUPS_ENAB yes
CREATE_HOME	yes
```

Quatre lignes à retenir :

- **`UID_MIN 1000`** : c'est la frontière entre comptes système et comptes
  humains. Un UID choisi à la main doit rester au-dessus, sinon le compte se
  mélange aux comptes de service.
- **`HOME_MODE 0700`** : le mode du répertoire personnel créé.
- **`USERGROUPS_ENAB yes`** : `useradd` crée un **groupe privé homonyme** du
  compte, sauf si vous imposez un groupe primaire avec `-g`.
- **`CREATE_HOME yes`** : voir juste en dessous, c'est un piège.

> **Sur AlmaLinux 10, `-m` ne change rien.** Le guide en ligne dit que `useradd`
> seule ne crée pas le répertoire personnel. Ce n'est pas vrai ici : avec
> `CREATE_HOME yes` dans `/etc/login.defs`, `sudo useradd lucien` sans aucune
> option produit déjà `/home/lucien` peuplé par `/etc/skel`. Ne comptez pas sur
> ce défaut pour autant : il n'est pas le même partout, et l'énoncé qui vous
> demande un home créé attend de vous le `-m` explicite.

`/etc/skel` est le gabarit recopié dans chaque nouveau home ; `ls -A /etc/skel`
y montre ici `.bash_logout`, `.bash_profile` et `.bashrc`. Un fichier que vous y
déposez apparaît dans le home de **tous** les comptes créés ensuite, et dans
aucun de ceux qui existent déjà.

### Créer un compte avec des attributs imposés

C'est le geste central. Les groupes doivent exister **avant**, `useradd` ne les
crée pas :

```bash
sudo groupadd bureau
sudo groupadd archives
sudo useradd -u 2400 -m -d /home/hector -s /bin/bash \
             -g bureau -G archives -c "Hector, poste 42" hector
```

- **`-u`** fixe l'UID. Il doit être libre, sinon la commande échoue.
- **`-m`** crée le home, **`-d`** dit lequel.
- **`-s`** fixe le shell de connexion.
- **`-g`** fixe le groupe **primaire**, **`-G`** la liste des groupes
  **secondaires**.
- **`-c`** remplit le champ commentaire, purement descriptif.

Deux commandes vérifient, et elles ne disent pas la même chose :

```bash
getent passwd hector
id hector
```

```plaintext
hector:x:2400:1003:Hector, poste 42:/home/hector:/bin/bash
uid=2400(hector) gid=1003(bureau) groups=1003(bureau),1004(archives)
```

`getent passwd` donne les sept champs de `/etc/passwd` : nom, `x` qui renvoie
vers `/etc/shadow`, UID, **GID primaire**, commentaire, home, shell. C'est la
seule des deux qui montre le **home** et le **shell**. `id` traduit les
identifiants numériques en noms et ajoute les **groupes secondaires**, que
`/etc/passwd` ne connaît pas.

Cette répartition explique une confusion fréquente :

```bash
getent group bureau archives
```

```plaintext
bureau:x:1003:
archives:x:1004:hector
```

`bureau` a l'air vide alors que c'est le groupe primaire d'`hector`. C'est
normal : **une appartenance primaire s'écrit dans `/etc/passwd`** (le 4e champ),
**une appartenance secondaire dans `/etc/group`**. Chercher un membre dans
`getent group` seul vous fera rater tous les comptes dont c'est le groupe
primaire.

Deux effets de bord du `-g` : aucun groupe homonyme n'a été créé (`getent group
hector` sort en erreur), et le home appartient au compte et à son groupe
primaire, en `0700` comme l'annonçait `HOME_MODE` :

```plaintext
$ ls -ld /home/hector
drwx------. 2 hector bureau 62 Jul 22 14:57 /home/hector
```

### `-aG` ou `-G` : l'erreur qui coûte le plus cher

`usermod -aG` **ajoute** un groupe secondaire. Rendons `lucien` membre de
`bureau` et `archives`, puis ajoutons `impression` **sans le `-a`** :

```plaintext
$ sudo usermod -aG archives lucien ; sudo usermod -aG bureau lucien ; id lucien
uid=1002(lucien) gid=1002(lucien) groups=1002(lucien),1003(bureau),1004(archives)
$ sudo usermod -G impression lucien ; id lucien
uid=1002(lucien) gid=1002(lucien) groups=1002(lucien),1005(impression)
```

`bureau` et `archives` ont disparu. La commande n'a affiché **ni avertissement,
ni erreur, ni code retour non nul** : `-G` remplace la liste entière par celle
que vous donnez. Le fichier confirme la perte :

```bash
grep -E '^(bureau|archives|impression):' /etc/group
```

```plaintext
bureau:x:1003:
archives:x:1004:hector
impression:x:1005:lucien
```

`hector` est resté dans `archives` : seul le compte cité par la commande a été
réécrit. Sur un vrai serveur, la même faute retire l'utilisateur de `wheel` (ou
`sudo` sur Debian) et lui coupe son accès administrateur sur-le-champ.

Deux réflexes : relever l'état avec `id` **avant** de toucher aux groupes, et
n'utiliser `-G` seul que lorsque vous voulez délibérément imposer la liste
complète. Pour retirer une seule appartenance, `gpasswd -d <user> <groupe>` est
plus sûr que de recomposer la liste à la main.

> Une **session déjà ouverte** garde les groupes qu'elle avait à la connexion.
> Après un ajout, l'utilisateur doit se reconnecter, et la vérification par `id`
> se fait dans la **nouvelle** session.

### Quatre façons de rendre un compte inutilisable

Ces quatre états se confondent facilement, se cumulent, et ne bloquent pas les
mêmes choses. Ils se lisent dans deux fichiers seulement.

**1. Aucun mot de passe utilisable.** C'est l'état d'un compte neuf : le champ
mot de passe de `/etc/shadow` contient `!` **sans hash derrière**. Après
`echo 'lucien:<secret>' | sudo chpasswd`, il porte un vrai hash :

```plaintext
$ sudo getent shadow lucien ; sudo passwd -S lucien     # compte neuf
lucien:!:20656:0:99999:7:::
lucien L 2026-07-22 0 99999 7 -1
$ sudo getent shadow lucien ; sudo passwd -S lucien     # apres chpasswd
lucien:$y$j9T$dAMR20K0L1tMxzejKPxtR/$NfkS8E1[...]:20656:0:99999:7:::
lucien P 2026-07-22 0 99999 7 -1
```

Attention, sur le compte neuf `passwd -S` annonce `L` alors que rien n'a été
verrouillé : il n'y a simplement jamais eu de mot de passe.

**2. Mot de passe verrouillé.** `usermod -L` (ou `passwd -l`, strictement
identique) préfixe le hash existant d'un `!` :

```plaintext
$ sudo usermod -L lucien ; sudo getent shadow lucien
lucien:!$y$j9T$dAMR20K0L1tMxzejKPxtR/$NfkS8E1[...]:20656:0:99999:7:::
```

Le hash est **conservé**, d'où le retour en arrière immédiat par `passwd -u`. Et
c'est ici qu'est le piège : le verrouillage ne concerne **que** le mot de passe.
Avec une clé dans `~/.ssh/authorized_keys`, la connexion passe toujours. Vérifié
sur la VM, compte verrouillé, `passwd -S` affichant `L` :

```plaintext
$ ssh -i cle_lucien lucien@atelier.lab 'id -un'
lucien
```

**3. Compte expiré.** C'est le seul état qui ferme réellement la porte. Il
s'écrit dans le **8e champ** de `/etc/shadow`, en jours depuis le 1er janvier
1970 :

```plaintext
$ sudo chage -E 1970-01-02 lucien
$ sudo chage -l lucien | grep -i 'account expires'
Account expires						: Jan 02, 1970
$ sudo getent shadow lucien | awk -F: '{print "champ 8 =", $8}'
champ 8 = 1
```

Déverrouillons alors le mot de passe pour isoler l'effet, en laissant
l'expiration en place :

```plaintext
$ sudo passwd -u lucien ; sudo passwd -S lucien
lucien P 2026-07-22 0 99999 7 -1
```

`passwd -S` affiche `P`, tout va bien de son point de vue. Et pourtant :

```plaintext
$ ssh -i cle_lucien lucien@atelier.lab
Your account has expired; please contact your system administrator.
Connection closed by 10.10.30.14 port 22
```

**Un compte déverrouillé peut donc être parfaitement inutilisable.** Retenez-en
la conséquence pratique : `passwd -S` ne dit rien de l'expiration, seul
`chage -l` fait foi. On lève l'expiration par `chage -E -1` (le champ 8
redevient vide), ou par `usermod --expiredate ""`.

**4. Shell de connexion refusant la session.** Rien dans `/etc/shadow` cette
fois, tout est dans le **7e champ de `/etc/passwd`** :

```plaintext
$ sudo usermod -s /sbin/nologin lucien ; getent passwd lucien
lucien:x:1002:1002::/home/lucien:/sbin/nologin
```

Le compte n'est ni verrouillé (`P`) ni expiré (`never`), et la connexion tombe
quand même, y compris pour une simple commande à distance :

```plaintext
$ ssh -i cle_lucien lucien@atelier.lab 'id -un'
This account is currently not available.
```

C'est l'état normal d'un compte de service, qui n'a aucune raison d'ouvrir une
session interactive. Sur AlmaLinux 10, `/sbin` est un lien vers `usr/sbin` : les
deux chemins `/sbin/nologin` et `/usr/sbin/nologin` désignent le même binaire.
Sur Debian et Ubuntu, seul `/usr/sbin/nologin` existe.

Le tableau de lecture, tous états confondus :

| Ce que vous voyez | Où | Ce que ça bloque |
|---|---|---|
| `!` seul dans `/etc/shadow` | champ 2 | mot de passe jamais défini ; clé SSH intacte |
| `!` devant un hash | champ 2 | mot de passe verrouillé ; **clé SSH intacte** |
| champ 2 **vide** (`passwd -S` = `NP`) | champ 2 | rien du tout : connexion sans mot de passe, à corriger d'urgence |
| une date passée en champ 8 | `/etc/shadow` | **tout**, y compris la clé SSH |
| `/sbin/nologin` en champ 7 | `/etc/passwd` | toute session, y compris `ssh <machine> <commande>` |

Une désactivation qui tient vraiment combine l'expiration, le verrouillage et la
fermeture des sessions déjà ouvertes : `sudo chage -E 0 <user>`, puis
`sudo passwd -l <user>`, puis `sudo pkill -KILL -u <user>`.

### Supprimer un compte, et ce qu'il reste après

Relevez l'UID **avant** : une fois le compte parti, le nom n'existe plus et vous
ne pourrez plus chercher par nom.

```bash
id -u hector          # 2400
sudo userdel -r hector
```

`-r` a un périmètre exact et étroit : le **répertoire personnel** et la **boîte
mail locale**. Vérification après coup :

```plaintext
$ grep -c '^hector:' /etc/passwd /etc/group ; sudo grep -c '^hector:' /etc/shadow
/etc/passwd:0
/etc/group:0
0
$ ls -ld /home/hector /var/spool/mail/hector
ls: cannot access '/home/hector': No such file or directory
ls: cannot access '/var/spool/mail/hector': No such file or directory
```

En revanche, tout ce que le compte possédait ailleurs reste, avec un UID qui ne
correspond plus à personne, affiché en **numéro brut**. Et chercher par nom
échoue désormais :

```plaintext
$ ls -l /srv/demo/rapport.txt
-rw-r--r--. 1 2400 bureau 0 Jul 22 14:58 /srv/demo/rapport.txt
$ sudo find /srv -user hector
find: invalid user name or UID argument to -user: ‘hector’
```

Deux méthodes marchent : l'UID relevé avant, ou `-nouser` qui ne demande rien.

```bash
sudo find / -xdev -uid 2400 -ls
sudo find / -xdev -nouser -ls
```

Le groupe `bureau`, lui, a survécu : `userdel` ne supprime que le groupe privé
homonyme. Un `groupadd` fait à la main se défait à la main, et `groupdel` refuse
tant qu'il sert de groupe primaire à quelqu'un.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `useradd: UID 2400 is not unique` | l'UID demandé est déjà pris ; `getent passwd <uid>` dit par qui |
| `groupdel: cannot remove the primary group of user '<nom>'` | changez d'abord ce groupe primaire (`usermod -g`) |
| Le home n'existe pas après `useradd` | `CREATE_HOME` est à `no` et vous avez oublié `-m` |
| `getent group <g>` n'affiche pas un membre que vous venez d'ajouter | c'est son groupe **primaire** : il est dans `/etc/passwd`, pas dans `/etc/group` |
| Le nouveau groupe n'a pas d'effet | la session date d'avant l'ajout ; déconnexion, reconnexion, puis `id` |
| L'utilisateur a perdu tous ses groupes secondaires | `usermod -G` a été tapé sans `-a` ; rien n'avertit, seul `id` le montre |
| Un compte verrouillé se connecte encore | le verrouillage n'agit que sur le mot de passe ; il faut expirer le compte |
| `passwd -S` dit `P` mais la connexion est refusée | compte expiré, ou shell `nologin` ; regardez `chage -l` et `getent passwd` |
| `ls -l` affiche un nombre au lieu d'un nom | fichier orphelin ; `sudo find / -xdev -nouser -ls` |
