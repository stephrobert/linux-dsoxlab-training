# Lab — expiration et complexité des mots de passe

## Rappel

[**Utilisateurs et groupes sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`chage -M <max> -m <min> -W <warn> <user>` règle l'expiration par compte
(`chage -l` l'affiche). `/etc/login.defs` contient `PASS_MAX_DAYS` et consorts —
les défauts appliqués aux comptes nouvellement créés. `/etc/security/pwquality.conf`
impose la complexité, ex. `minlen` pour la longueur minimale.

## Le cours

Les exemples ci-dessous travaillent sur deux comptes de démonstration,
`pwd-demo-lea` et `pwd-demo-tom`, avec d'autres délais et d'autres longueurs
que ceux du challenge : celui-ci vous demandera un autre compte et d'autres
valeurs. Le but est d'apprendre la méthode, pas de recopier une ligne.

Toutes les sorties de cette page ont été relevées sur une VM AlmaLinux 10.2.

### Trois réglages, trois endroits, trois portées

C'est le point qui coûte le plus cher quand on le confond :

| Ce que vous réglez | Où | Sur qui cela agit |
|---|---|---|
| l'expiration d'un compte précis | `chage`, qui écrit dans `/etc/shadow` | ce compte, immédiatement |
| le défaut d'expiration | `/etc/login.defs` | les comptes créés **ensuite**, jamais les existants |
| la qualité exigée d'un mot de passe | `/etc/security/pwquality.conf` | toute saisie de mot de passe, tout de suite |

Durcir `/etc/login.defs` ne touche donc **aucun** compte déjà présent, et
`chage` sur un compte ne change rien pour les suivants. Il faut les deux.

### Le décor de démonstration

```bash
sudo useradd -m -s /bin/bash pwd-demo-lea
id pwd-demo-lea
```

```text
uid=1005(pwd-demo-lea) gid=1007(pwd-demo-lea) groups=1007(pwd-demo-lea)
```

Avant de régler quoi que ce soit, regardez ce que le compte a reçu à sa
naissance :

```bash
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: never
Password inactive					: never
Account expires						: never
Minimum number of days between password change		: 0
Maximum number of days between password change		: 99999
Number of days of warning before password expires	: 7
```

`99999` jours, soit environ 273 ans : c'est la façon de dire « jamais ». Ces
valeurs ne sortent pas de nulle part, elles ont été recopiées depuis
`/etc/login.defs` au moment du `useradd` ; on y revient plus bas.

Les libellés de `chage -l` sont des chaînes traduisibles, et un script qui les
analyse casse dès que la machine change de langue. Sur cette VM la question ne
se pose pas (`locale -a | grep '^fr'` ne renvoie rien, aucune locale française
n'est installée, et la sortie reste en anglais même avec
`LC_ALL=fr_FR.UTF-8`), mais prenez le réflexe qui marche partout :
`sudo LC_ALL=C chage -l pwd-demo-lea`.

Un compte neuf n'a pas encore de mot de passe utilisable. Le guide le dit, et
`/etc/shadow` le confirme : le champ contient un `!`.

```bash
sudo passwd -S pwd-demo-lea
sudo awk -F: '$1=="pwd-demo-lea" {print $1" : ["$2"]"}' /etc/shadow
```

```text
pwd-demo-lea L 2026-07-22 0 99999 7 -1
pwd-demo-lea : [!]
```

### Poser une politique sur un compte : `chage -M`, `-m`, `-W`

Les trois options se posent en une seule commande :

```bash
sudo chage -M 45 -m 3 -W 10 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: Sep 05, 2026
Password inactive					: never
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

- **`-M`** (maximum) : le mot de passe doit être changé au bout de tant de
  jours. La ligne `Password expires` n'est pas une valeur que vous saisissez :
  elle est **calculée**, c'est la date du dernier changement plus le maximum.
  Ici Jul 22 + 45 jours donne Sep 05.
- **`-m`** (minimum) : délai pendant lequel la personne ne peut **pas** changer
  son mot de passe une deuxième fois. Cela empêche de contourner un historique
  en enchaînant les changements pour revenir à l'ancien mot de passe.
- **`-W`** (warning) : nombre de jours d'avertissement avant l'échéance.

Ces trois réglages vivent dans `/etc/shadow`, aux champs 4, 5 et 6 :

```bash
sudo awk -F: '$1=="pwd-demo-lea"' /etc/shadow
```

```text
pwd-demo-lea:!:20656:3:45:10:::
```

Le troisième champ (`20656`) est la date du dernier changement, comptée en
**jours depuis le 1er janvier 1970**. C'est ce nombre que `chage -l` traduit en
date lisible, et vous pouvez faire la conversion vous-même :

```bash
date -u -d "@$((20656*86400))" +%F
```

```text
2026-07-22
```

Ne modifiez jamais cette ligne à la main : le guide rappelle
qu'un caractère de travers dans `/etc/shadow` peut empêcher toute connexion, y
compris celle de root, et que les outils (`chage`, `usermod`, `passwd`) posent
un verrou avant d'écrire.

### Ce que `-m` empêche réellement

Donnons un mot de passe au compte, puis regardons ce qui se passe si la
personne veut le changer tout de suite depuis sa propre session.

```bash
sudo passwd pwd-demo-lea
sudo passwd -S pwd-demo-lea
```

```text
New password: Retype new password: passwd: password updated successfully
pwd-demo-lea P 2026-07-22 3 45 10 -1
```

Le deuxième champ est passé de `L` à `P` : il y a maintenant un mot de passe
utilisable. La tentative de changement immédiat, elle, est refusée :

```bash
passwd                                     # dans la session de pwd-demo-lea
```

```text
Current password: New password: You must wait longer to change your password.
passwd: Authentication token manipulation error
passwd: password unchanged
```

`root`, en revanche, n'est pas soumis au délai minimal : la même opération
lancée avec `sudo passwd pwd-demo-lea` passe sans broncher.

```text
New password: Retype new password: passwd: password updated successfully
```

Retenez-en la conséquence pratique : un `-m` élevé n'est pas un mur, c'est une
gêne pour l'utilisateur et une non-contrainte pour l'administrateur. Si vous
devez laisser quelqu'un changer son mot de passe malgré le délai, remettez
temporairement le minimum à zéro (`sudo chage -m 0 <compte>`) plutôt que de
lui demander d'attendre.

### Les deux champs qu'on oublie : `-I` et `-E`

`chage -l` affiche sept lignes, et le challenge n'en couvre que trois. Les deux
autres réglages méritent d'être connus, ne serait-ce que pour ne pas les
confondre avec les premiers.

**`-I` (inactive)** ajoute un délai **après** l'expiration du mot de passe.
Son manuel le définit ainsi : *« Set the number of days of inactivity after a
password has expired before the account is locked »*, et précise qu'une fois
le compte verrouillé, la personne doit contacter l'administrateur pour
retrouver l'accès. C'est donc un sursis, pas un avertissement.

```bash
sudo chage -I 5 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: Sep 05, 2026
Password inactive					: Sep 10, 2026
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

`Password inactive` est là encore **calculée** : Sep 05 plus 5 jours.

**`-E` (expire)** ferme le **compte**, ce qui n'a rien à voir avec l'expiration
du mot de passe :

```bash
sudo chage -E 2026-11-30 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jul 22, 2026
Password expires					: Sep 05, 2026
Password inactive					: Sep 10, 2026
Account expires						: Nov 30, 2026
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

> **`Password expires` et `Account expires` sont deux choses différentes.**
> Un mot de passe expiré se répare en en saisissant un nouveau. Un compte
> expiré refuse **toutes** les connexions, y compris par clé SSH : c'est le
> seul moyen, dit le guide, de couper réellement un accès, là où un
> `passwd -l` laisse la clé SSH fonctionner. C'est aussi le geste qui a sa
> place dans une fiche de départ, pas dans une politique d'expiration.

La valeur `-1` remet ces deux champs à `never` :

```bash
sudo chage -I -1 -E -1 pwd-demo-lea
```

### Un mot de passe déjà trop vieux

Poser un `-M` sur un compte dont le mot de passe date ne repousse rien : la
date d'échéance est recalculée depuis le **dernier changement**, et elle peut
donc tomber dans le passé.

```bash
sudo chage -d 2026-01-10 pwd-demo-lea     # simule un mot de passe ancien
sudo chage -l pwd-demo-lea
```

```text
Last password change					: Jan 10, 2026
Password expires					: Feb 24, 2026
Password inactive					: never
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

C'est le comportement attendu : durcir la politique sur un parc existant expire
d'un coup tous les mots de passe plus vieux que le nouveau maximum. Prévenez
avant, ou étalez avec `chage -d`.

Le cas limite de cette mécanique est le geste recommandé par le guide pour un
mot de passe initial, qui ne doit pas survivre à la première session :

```bash
sudo chage -d 0 pwd-demo-lea
sudo chage -l pwd-demo-lea
```

```text
Last password change					: password must be changed
Password expires					: password must be changed
Password inactive					: password must be changed
Account expires						: never
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
Number of days of warning before password expires	: 10
```

Une date de dernier changement à zéro rend le mot de passe expiré d'office :
le système demandera à la personne d'en choisir un nouveau à sa prochaine
connexion.

### Le défaut système : `/etc/login.defs`

`chage` traite un compte à la fois. Pour que les **prochains** comptes naissent
avec la bonne politique, on règle `/etc/login.defs`.

```bash
grep -E '^PASS_(MAX|MIN)_DAYS' /etc/login.defs
```

```text
PASS_MAX_DAYS	99999
PASS_MIN_DAYS	0
```

Trois directives font le lien avec les trois options de `chage` :

| Directive de `login.defs` | Option `chage` équivalente |
|---|---|
| `PASS_MAX_DAYS` | `-M` |
| `PASS_MIN_DAYS` | `-m` |
| `PASS_WARN_AGE` | `-W` |

Sauvegardez avant d'éditer, c'est un fichier système lu par `useradd` :

```bash
sudo cp -a /etc/login.defs /etc/login.defs.bak
```

Après modification, le fichier annonce les nouveaux défauts :

```text
PASS_MAX_DAYS	90
PASS_MIN_DAYS	2
```

Et c'est là que se joue toute la section. Le compte **déjà existant** n'a pas
bougé d'un jour :

```bash
sudo chage -l pwd-demo-lea | grep -iE 'minimum|maximum'
```

```text
Minimum number of days between password change		: 3
Maximum number of days between password change		: 45
```

Alors qu'un compte créé **après** hérite des nouvelles valeurs :

```bash
sudo useradd -m pwd-demo-tom
sudo chage -l pwd-demo-tom | grep -iE 'minimum|maximum'
```

```text
Minimum number of days between password change		: 2
Maximum number of days between password change		: 90
```

Mieux : remettez `/etc/login.defs` dans son état d'origine, et `pwd-demo-tom`
garde `2` et `90`. Ces valeurs ne sont pas relues à chaque connexion, elles ont
été **gravées dans `/etc/shadow`** au moment du `useradd`. Le manuel est net
sur ce point :

```bash
man login.defs
```

```text
PASS_MAX_DAYS, PASS_MIN_DAYS and PASS_WARN_AGE are only used at the
time of account creation. Any changes to these settings won't affect
existing accounts.
```

> **Une politique posée uniquement dans `login.defs` ne durcit rien
> aujourd'hui.** Sur un serveur en production, tous les comptes sont déjà
> créés : ils continueront avec leurs anciens délais jusqu'à ce qu'une boucle
> `chage` passe dessus. C'est exactement le constat d'audit que le fichier
> était censé éviter.

Un détail qui trompe : `/etc/login.defs` contient aussi une directive
`PASS_MIN_LEN`, et on croit volontiers que c'est elle qui impose la longueur
minimale. Elle n'apparaît déjà **pas** dans le manuel du fichier
(`man login.defs | grep -c PASS_MIN_LEN` renvoie `0`), et la machine tranche :

```bash
grep -E '^PASS_MIN_LEN' /etc/login.defs
grep -vE '^\s*#|^\s*$' /etc/security/pwquality.conf
echo 'Zk4-tR9' | pwscore                  # 7 caractères, hors dictionnaire
```

```text
PASS_MIN_LEN	8
minlen = 6
57
```

Un mot de passe de sept caractères est accepté alors que `PASS_MIN_LEN` en
exige huit, parce que c'est le `minlen` de `pwquality` qui décide. La
vérification par `passwd`, depuis la session du compte, confirme :

```text
Current password: New password: Retype new password: passwd: password updated successfully
```

C'est donc `pwquality` qui porte la longueur minimale, objet de la section
suivante.

### La complexité : `/etc/security/pwquality.conf`

Ce fichier ne parle plus de durée mais de **contenu**. Il est lu par la
bibliothèque `libpwquality`, elle-même appelée par le module PAM
`pam_pwquality` :

```bash
grep -n pam_pwquality /etc/pam.d/system-auth /etc/pam.d/password-auth
```

```text
/etc/pam.d/system-auth:13:password    requisite                                    pam_pwquality.so
/etc/pam.d/password-auth:13:password    requisite                                    pam_pwquality.so
```

Le mot-clé `requisite` a son importance. `man pam.conf` le définit ainsi : en
cas d'échec du module, *« control is directly returned to the application »*,
sans exécuter la suite de la pile. Un mot de passe refusé par `pwquality`
n'atteint donc jamais `/etc/shadow`.

Pour tester sans rien changer, la commande `pwscore` (paquet `libpwquality`)
lit la même configuration et note un mot de passe de 0 à 100 :

```bash
echo 'azerty'      | pwscore
echo 'motdepasse'  | pwscore
echo 'Sel-Marin-9' | pwscore
```

```text
Password quality check failed:
 The password fails the dictionary check - it is based on a dictionary word
Password quality check failed:
 The password fails the dictionary check - it is based on a dictionary word
100
```

`minlen` n'est donc pas la seule règle : un mot du dictionnaire est rejeté quelle
que soit sa longueur. Passons maintenant l'exigence de longueur à 14, après
sauvegarde :

```bash
sudo cp -a /etc/security/pwquality.conf /etc/security/pwquality.conf.bak
sudo sed -i 's/^minlen = .*/minlen = 14/' /etc/security/pwquality.conf
grep -vE '^\s*#|^\s*$' /etc/security/pwquality.conf
```

```text
minlen = 14
```

Le même mot de passe de onze caractères, qui obtenait 100, est désormais
refusé, tandis qu'un mot de passe de vingt-et-un caractères passe :

```bash
echo 'Sel-Marin-9'           | pwscore
echo 'Mer-Rouge-Profonde-42' | pwscore
```

```text
Password quality check failed:
 The password is shorter than 14 characters
86
```

Deux remarques sur ce score. Il n'est **pas** une note de sécurité absolue :
`Sel-Marin-9` valait 100 avec une exigence de 6 et ne passe plus avec une
exigence de 14. Et un score plus bas (86) peut correspondre à un mot de passe
bien meilleur : c'est la règle en vigueur qui décide, pas le chiffre.

L'effet réel se voit sur `passwd`. Depuis la session du compte concerné, le
changement est **refusé** :

```bash
passwd                                     # dans la session de pwd-demo-lea
```

```text
Current password: New password: BAD PASSWORD: The password is shorter than 14 characters
passwd: Authentication token manipulation error
passwd: password unchanged
```

Alors que `root` n'est qu'**averti**, et obtient tout de même le changement :

```bash
sudo passwd pwd-demo-lea
```

```text
New password: BAD PASSWORD: The password is shorter than 14 characters
Retype new password: passwd: password updated successfully
```

(Les invites `Current password:` et `New password:` apparaissent ici sur la
même ligne parce que la saisie a été envoyée par un tube pour les besoins de
la capture ; au clavier, elles s'affichent l'une après l'autre.)

> **Vérifiez toujours avec un compte non privilégié.** Un administrateur qui
> teste sa politique avec `sudo passwd <compte>` voit le message `BAD PASSWORD`
> et en conclut que la règle s'applique, alors que le mot de passe faible vient
> d'être accepté. Seule la tentative faite **par** l'utilisateur prouve que la
> règle mord.

### Le piège du répertoire `pwquality.conf.d`

Le manuel annonce un répertoire de fragments :

```bash
man pwquality.conf
```

```text
The libpwquality library also first reads all *.conf files from the
/etc/security/pwquality.conf.d directory in ASCII sorted order. The
values of the same settings are overridden in the order the files are
parsed.
```

Lisez bien le **first**. Contrairement à l'habitude prise avec systemd ou
`sysctl.d`, où le fragment l'emporte sur le fichier principal, ici les
fragments sont lus **en premier** et le fichier principal, parsé ensuite,
écrase ce qu'ils ont posé. Vérification, avec `minlen = 6` dans le fichier
principal et `minlen = 30` dans un fragment :

```bash
echo 'minlen = 30' | sudo tee /etc/security/pwquality.conf.d/99-demo.conf
echo 'Mer-Rouge-Profonde-42' | pwscore
```

```text
100
```

Le fragment est ignoré : 21 caractères passent alors qu'on en exigeait 30.
Commentons la ligne du fichier principal, sans rien changer d'autre :

```bash
sudo sed -i 's/^minlen = 6$/# minlen = 6/' /etc/security/pwquality.conf
echo 'Mer-Rouge-Profonde-42' | pwscore
```

```text
Password quality check failed:
 The password is shorter than 30 characters
```

Le fragment était donc bien lu, mais perdait l'arbitrage. Conclusion : un
réglage déposé dans `pwquality.conf.d/` ne prend effet que si la même directive
est **absente ou commentée** du fichier principal. Un audit qui trouve un
`minlen` conforme dans un fragment et un `minlen` laxiste dans
`pwquality.conf` doit conclure que c'est le laxiste qui s'applique.

### Vérifier et auditer

Trois commandes suffisent, et elles ne disent pas la même chose.

`chage -l <compte>` donne le détail lisible d'un compte. Un utilisateur peut
l'exécuter sur **lui-même** sans privilège, mais pas sur un autre :

```bash
chage -l pwd-demo-tom     # depuis la session de pwd-demo-tom
```

```text
Last password change					: Jul 22, 2026
...
```

```bash
chage -l pwd-demo-lea     # depuis la même session, sur un autre compte
chage -M 30 pwd-demo-tom  # toute modification, même sur soi-même
```

```text
chage: Permission denied.
chage: Permission denied.
```

`passwd -S` donne la même information sur une ligne, et `passwd -Sa` la donne
pour tous les comptes, ce qui en fait l'outil d'inventaire :

```bash
sudo passwd -Sa | grep '^pwd-demo'
```

```text
pwd-demo-lea P 2026-07-22 3 45 10 -1
pwd-demo-tom L 2026-07-22 3 45 10 -1
```

Les champs, dans l'ordre : compte, état du mot de passe, date du dernier
changement, minimum, maximum, avertissement, inactivité. L'état vaut `P` (mot
de passe utilisable), `L` (verrouillé, ou jamais défini) ou `NP` (aucun mot de
passe, à corriger d'urgence).

`passwd -S` ne dit rien de l'expiration du **compte** : le guide insiste sur ce
point, c'est `chage -l` qui fait foi pour savoir si un accès est réellement
fermé.

Enfin, appliquer la même politique à plusieurs comptes tient en une boucle :

```bash
for u in pwd-demo-lea pwd-demo-tom; do
  sudo chage -M 45 -m 3 -W 10 "$u"
done
sudo passwd -Sa | grep '^pwd-demo'
```

```text
pwd-demo-lea P 2026-07-22 3 45 10 -1
pwd-demo-tom L 2026-07-22 3 45 10 -1
```

C'est ce genre de boucle qui rattrape les comptes existants après un
changement de `/etc/login.defs`.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Les comptes existants gardent `99999` après édition de `login.defs` | normal : le fichier ne sert qu'à la création. Repasser avec `chage` sur chaque compte |
| `You must wait longer to change your password.` | le délai minimal (`-m`) n'est pas écoulé. `sudo chage -m 0 <compte>` le lève |
| `chage: Permission denied.` | `chage` sur un autre compte, ou une modification, exige `sudo` |
| `Password expires` ne correspond pas au calcul attendu | la date est calculée depuis `Last password change`, pas depuis le jour où vous avez posé le `-M` |
| Le mot de passe faible est accepté alors que `minlen` est posé | le test a été fait en root : root n'est qu'averti. Refaire le test avec le compte concerné |
| `minlen` posé dans `pwquality.conf.d/` sans effet | le fichier principal est parsé après les fragments et l'emporte : commenter la directive dans `pwquality.conf` |
| Tous les mots de passe expirent d'un coup après un `chage -M` | les mots de passe étaient plus vieux que le nouveau maximum. Étaler avec `chage -d` |
| `passwd -S` affiche `P` sur un compte qu'on croyait fermé | `passwd -S` ignore l'expiration du compte : lire `Account expires` dans `chage -l` |

Pour tout défaire et repartir de zéro :

```bash
sudo userdel -r pwd-demo-lea
sudo userdel -r pwd-demo-tom
sudo cp -a /etc/login.defs.bak /etc/login.defs
sudo cp -a /etc/security/pwquality.conf.bak /etc/security/pwquality.conf
sudo rm -f /etc/security/pwquality.conf.d/99-demo.conf
```

Ces deux restaurations ne sont pas facultatives. Un `minlen` oublié à une
valeur élevée empêchera le prochain `passwd` de la machine, et un
`PASS_MAX_DAYS` oublié se retrouvera gravé dans tous les comptes créés
ensuite, longtemps après que les fichiers de démonstration ont disparu.
Contrôlez plutôt deux fois :

```bash
grep -E '^PASS_(MAX|MIN)_DAYS' /etc/login.defs
grep -vE '^\s*#|^\s*$' /etc/security/pwquality.conf
```
