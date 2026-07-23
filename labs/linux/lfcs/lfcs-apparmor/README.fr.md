# Lab — gérer un profil AppArmor

## Rappel

[**AppArmor sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/)

AppArmor confine les programmes avec des profils par binaire. `aa-status` liste les
profils chargés et leur mode ; `aa-complain <profil>` passe un profil en mode
apprentissage (journalise, ne bloque pas), `aa-enforce` le remet en enforce,
`aa-disable` le décharge. C'est le pendant Debian de SELinux, mais par profil.

## Le cours

Les exemples ci-dessous confinent un binaire jetable, `/usr/local/bin/atelier-lecteur`,
auquel on écrit un profil de toutes pièces : le challenge, lui, portera sur un profil
déjà livré par la distribution. Apprenez le cycle observer / ajuster / appliquer, ne
recopiez pas une ligne. Sorties réelles d'une Ubuntu 24.04.4 LTS, paquets `apparmor`
et `apparmor-utils` en `4.0.1really4.0.1-0ubuntu0.24.04.7`.

> **Ne passez jamais en `enforce` un profil qui garde votre accès.** Trop serré sur
> `sshd`, `dhclient`, `systemd` ou `netplan`, il vous enferme dehors, et il n'existe ici
> **aucun filet** : `student` passe par le même port 22, sans canal d'agent invité.

### Où en est AppArmor sur cette machine

`aa-status` (alias `apparmor_status`) est la **seule** source de vérité : ni `systemctl`
ni la présence d'un fichier dans `/etc/apparmor.d/` ne disent ce que le noyau applique.
Relevez l'état de départ, vous devrez savoir le rendre.

```bash
sudo aa-status
```

```text
apparmor module is loaded.
117 profiles are loaded.
23 profiles are in enforce mode.
   /usr/bin/man
   [...]
4 profiles are in complain mode.
   transmission-cli
   [...]
0 profiles are in prompt mode.
0 profiles are in kill mode.
90 profiles are in unconfined mode.   [...]
1 processes have profiles defined.
1 processes are in enforce mode.
   /usr/sbin/rsyslogd (710) rsyslogd
```

Retenez les six premiers nombres et le dernier bloc, ce sont vos repères de fin de
manipulation. Deux choses à comprendre tout de suite : la distribution **livre déjà**
des profils (117 chargés, dont quatre en complain qu'aucun administrateur n'a
demandés), et les profils sont comptés séparément des **processus**, un seul étant
confiné ici. Le module noyau, lui, se vérifie ailleurs, et le guide insiste : sur
Debian, Ubuntu et openSUSE, AppArmor est chargé **par défaut**, sans paramètre GRUB.

```bash
cat /sys/module/apparmor/parameters/enabled ; cat /sys/kernel/security/lsm
dpkg -l apparmor apparmor-utils | grep ^ii | awk '{print $2, $3}'
```

```text
Y
lockdown,capability,landlock,yama,apparmor
apparmor 4.0.1really4.0.1-0ubuntu0.24.04.7   [...]
```

Sans `apparmor-utils`, aucune commande `aa-*` : premier réflexe si `command not found`.

### Un profil, un chemin : la différence avec SELinux

Les profils vivent dans `/etc/apparmor.d/`, un fichier texte par programme
(109 entrées ici). Écrivons-en un pour un binaire jetable, une copie de `cat` :

```bash
sudo install -d /srv/atelier/donnees /srv/atelier/prive
printf 'temperature=21.4\n' | sudo tee /srv/atelier/donnees/mesures.txt
printf 'jeton=demo\n'       | sudo tee /srv/atelier/prive/secret.txt
sudo cp /usr/bin/cat /usr/local/bin/atelier-lecteur
sudo tee /etc/apparmor.d/usr.local.bin.atelier-lecteur <<'EOF'
abi <abi/4.0>,
include <tunables/global>

/usr/local/bin/atelier-lecteur {
  include <abstractions/base>

  /usr/local/bin/atelier-lecteur mr,
  /srv/atelier/donnees/** r,
}
EOF
```

Trois éléments à lire. Le **nom du fichier** est conventionnel (le chemin du binaire,
slashs remplacés par des points) mais sans importance : c'est la ligne d'ouverture
`/usr/local/bin/atelier-lecteur {` qui désigne le programme confiné. Chaque règle est
un **chemin** suivi de permissions (`r` lire, `w` écrire, `m` mapper) et d'une virgule.
`include <abstractions/base>` apporte le socle commun que tout programme réclame ;
sans lui, rien ne démarre.

Là est le partage des eaux avec SELinux, qui étiquette l'**inode** : le contexte voyage
avec le fichier, et un `mv` le conserve, ce que mesure le cours `l4-selinux-diagnose-avc`
(un fichier déplacé depuis `~` arrive dans `/etc` en `user_home_t` et casse le service).
AppArmor, lui, ne connaît que le **chemin**. Vérifions, profil chargé en enforce :

```bash
sudo cp -a /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-copie
sudo ln    /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-lien
stat -c '%i %n' /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-lien
/usr/local/bin/atelier-lien /srv/atelier/prive/secret.txt
```

```text
44963 /usr/local/bin/atelier-lecteur
44963 /usr/local/bin/atelier-lien
jeton=demo
```

Le lien dur porte le **même inode** (44963) et pointe donc sur le même binaire, mais
son chemin ne figure dans aucun profil : il s'exécute **non confiné** et lit un fichier
que le profil interdit. La copie fait de même. Sous SELinux, l'étiquette étant portée
par l'inode, un lien dur reste soumis à la politique. C'est la contrepartie annoncée
par le guide : AppArmor est plus simple, mais un lien dur, un bind mount ou un binaire
renommé peut échapper à une règle.

### Chargé, appliqué, confiné : trois états distincts

Cette distinction vaut celle d'`enabled` et `active` pour une unité systemd.

```bash
sudo aa-status | grep -c atelier-lecteur          # 0 : fichier present, rien de charge
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.atelier-lecteur
sudo aa-status | grep -E "^[0-9]+ profiles are (loaded|in enforce)"
```

```text
0
118 profiles are loaded.
24 profiles are in enforce mode.
```

Premier temps : un fichier posé dans `/etc/apparmor.d/` **n'est pas un profil actif**.
Tant que `apparmor_parser -r` ne l'a pas injecté dans le noyau, `aa-status` l'ignore.
Notez que le chargement se fait **en enforce**, pas en complain : sans mention
contraire, un profil fraîchement écrit bloque dès la première seconde. Deuxième temps :
chargé ne veut pas dire qu'un processus y est soumis. Lançons-en un qui dure :

```bash
setsid /usr/local/bin/atelier-lecteur > /dev/null < /dev/zero &
sudo aa-status | sed -n '/processes have profiles/,+3p'
cat /proc/$(pgrep -f atelier-lecteur | head -1)/attr/current
```

```text
2 processes have profiles defined.
2 processes are in enforce mode.
   /usr/local/bin/atelier-lecteur (3306)
   /usr/sbin/rsyslogd (707) rsyslogd
/usr/local/bin/atelier-lecteur (enforce)
```

`/proc/<pid>/attr/current` est l'équivalent AppArmor de `ps -Z` sous SELinux : il
donne le profil **effectivement porté** par un processus vivant, mode compris. Le
compteur retombe à 1 dès que le processus se termine, alors que le profil, lui, reste
chargé : il ne protège rien dans l'instant, mais s'appliquera au prochain démarrage.

### complain d'abord, enforce ensuite

C'est la méthode du sujet, et l'ordre inverse casse les services en production.
`aa-complain` bascule un profil en apprentissage :

```bash
sudo aa-complain /usr/local/bin/atelier-lecteur
sudo aa-status | grep -E "^[0-9]+ profiles are in (enforce|complain)"
grep flags /etc/apparmor.d/usr.local.bin.atelier-lecteur
```

```text
Setting /usr/local/bin/atelier-lecteur to complain mode.
23 profiles are in enforce mode.
5 profiles are in complain mode.
/usr/local/bin/atelier-lecteur flags=(complain) {
```

Regardez la dernière ligne : `aa-complain` **réécrit le fichier de profil** en y
ajoutant `flags=(complain)`. Différence de nature avec le `setenforce 0` de SELinux,
qui ne vit qu'en mémoire : ici le mode est **persistant** et traverse le redémarrage,
vérifié sur cette machine, `aa-status` affichant après un `systemctl reboot` les mêmes
cinq profils en complain. Le profil n'autorise que `/srv/atelier/donnees/**` ; en
complain, lisons quand même un fichier hors périmètre :

```bash
/usr/local/bin/atelier-lecteur /etc/hostname
sudo journalctl -k --since -2min | grep -i apparmor | tail -1
```

```text
atelier.lab
kernel: audit: type=1400 audit(1784745049.196:123): apparmor="ALLOWED"
 operation="open" class="file" profile="/usr/local/bin/atelier-lecteur"
 name="/etc/hostname" pid=2292 comm="atelier-lecteur" requested_mask="r"
 denied_mask="r" fsuid=1001 ouid=0
```

La lecture passe, et pourtant la trace porte `denied_mask="r"` : le noyau dit
« j'aurais refusé, j'ai laissé faire, et je le note ». Les champs à savoir lire sont
toujours les mêmes : `apparmor=` (le verdict), `operation=` (ce qui était tenté),
`profile=` (le coupable), `name=` (la ressource), `requested_mask` et `denied_mask`.
En enforce, la même ligne devient `apparmor="DENIED"` et l'appel échoue :

```text
apparmor="DENIED" operation="open" class="file" profile="/usr/local/bin/atelier-lecteur"
 name="/srv/atelier/prive/secret.txt" pid=2751 requested_mask="r" denied_mask="r"
```

Côté application, c'est un banal `Permission denied` alors que les droits Unix sont
bons : signature d'un refus MAC, comme un AVC SELinux.

> **Le piège du complain.** Complain n'est pas « sans protection » : une règle `deny`
> **explicite** continue de bloquer. Mesuré ici, un `deny /srv/atelier/prive/** r,`
> refuse la lecture en complain comme en enforce, et sans écrire **la moindre ligne**
> dans le journal. Un `deny` filtre en silence : quand un refus reste introuvable
> dans les traces, relisez le profil.

### aa-logprof : transformer les traces en règles

Une fois les traces accumulées, `aa-logprof` relit le journal et propose d'ajouter les
règles observées. Sur Ubuntu 24.04, `rsyslog` est présent et `/var/log/syslog` existe :
l'outil trouve son journal seul. Sur **Debian 12** il n'existe pas, et le guide donne
le contournement (`journalctl -b -k -e -f > /var/tmp/aa.log` puis `aa-logprof -f`).
Réduire le fichier à vos seuls événements évite en prime les propositions parasites :

```bash
sudo journalctl -k --since -20min | grep atelier-lecteur > /var/tmp/aa-atelier.log
sudo aa-logprof -f /var/tmp/aa-atelier.log
```

```text
Reading log entries from /var/tmp/aa-atelier.log.
Complain-mode changes:
Profile:  /usr/local/bin/atelier-lecteur
Path:     /etc/hostname
New Mode: r
 [1 - /etc/hostname r,]
(A)llow / [(D)eny] / (I)gnore / (G)lob / Glob with (E)xtension / (N)ew / ...
Adding /etc/hostname r, to profile.
= Changed Local Profiles =
(S)ave Changes / Save Selec(t)ed Profile / [(V)iew Changes] / ...
Writing updated profile for /usr/local/bin/atelier-lecteur.
```

Deux touches suffisent, `a` puis `s`, mais l'outil **exige un terminal** : lancé sans
TTY il s'écrase sur `termios.error: Inappropriate ioctl for device`. Triez ce qu'il
propose plutôt que de tout accepter, le guide signalant qu'il suggère souvent des
abstractions hors sujet. Le fichier ressort réécrit et trié, la ligne
`/etc/hostname r,` insérée. Reste à fermer la boucle : `aa-enforce` retire
`flags=(complain)` et recharge dans la foulée.

```bash
sudo aa-enforce /usr/local/bin/atelier-lecteur
sudo aa-status --json | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['profiles']['/usr/local/bin/atelier-lecteur'])"
```

```text
Setting /usr/local/bin/atelier-lecteur to enforce mode.
enforce
```

`aa-status --json` est la forme à préférer dès qu'un script doit décider : il rend un
dictionnaire `profiles` associant chaque profil à son mode, sans découper de texte.

### Recharger n'est pas désactiver

Deux gestes voisins que l'examen aime confondre. Après avoir **édité** un profil,
`apparmor_parser -r` (comme *replace*) le relit et remplace la version en mémoire.
Sans lui, le fichier a changé mais le noyau applique toujours l'ancienne politique :

```bash
# on ajoute la ligne « /srv/atelier/prive/** r, » au profil, puis :
/usr/local/bin/atelier-lecteur /srv/atelier/prive/secret.txt   # Permission denied
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.atelier-lecteur
/usr/local/bin/atelier-lecteur /srv/atelier/prive/secret.txt   # jeton=demo
```

`aa-disable`, lui, **décharge** le profil et pose un lien dans
`/etc/apparmor.d/disable/` pour qu'il ne revienne pas au démarrage :

```bash
sudo aa-disable /usr/local/bin/atelier-lecteur
ls -l /etc/apparmor.d/disable/ ; sudo aa-status | grep "profiles are loaded"
```

```text
Disabling /usr/local/bin/atelier-lecteur.
usr.local.bin.atelier-lecteur -> /etc/apparmor.d/usr.local.bin.atelier-lecteur
117 profiles are loaded.
```

Le compteur retombe de 118 à 117, le fichier de profil reste pourtant sur le disque,
et le binaire n'est plus médiatisé du tout. D'où le symptôme classique du guide : un
profil qu'on croit désactivé **réapparaît** parce qu'on a effacé le lien sans
recharger, ou reste inerte parce qu'on a oublié de l'effacer. Les deux gestes vont
ensemble :

```bash
sudo rm /etc/apparmor.d/disable/usr.local.bin.atelier-lecteur
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.atelier-lecteur
```

### Dépannage et retour à l'état initial

| Symptôme | Cause probable | Solution |
|---|---|---|
| `aa-complain: command not found` | `apparmor-utils` absent | `sudo apt-get install apparmor-utils` |
| Le profil édité n'a aucun effet | Fichier modifié, noyau pas rechargé | `sudo apparmor_parser -r /etc/apparmor.d/<profil>` |
| Un profil écrit à la main bloque tout de suite | `apparmor_parser -r` charge en **enforce** | `sudo aa-complain <binaire>` avant les tests |
| `Permission denied` avec des droits Unix corrects | Refus MAC | `sudo journalctl -k \| grep -i apparmor`, chercher `DENIED` |
| Un refus reste invisible dans le journal | Règle `deny` explicite, silencieuse | Relire le profil, pas seulement les traces |
| `aa-logprof` : `termios.error` | Lancé sans terminal | Le relancer dans un vrai TTY |
| `aa-logprof` : `Can't find system log` (guide) | Debian 12 sans `rsyslog` | `journalctl -b -k -e -f > /var/tmp/aa.log`, puis `-f` |
| Un profil désactivé réapparaît (guide) | Lien laissé dans `disable/` | `rm /etc/apparmor.d/disable/<profil>` puis `apparmor_parser -r` |

Pour tout défaire, **déchargez avant de supprimer** : effacer le fichier ne retire pas
le profil du noyau, qui confinerait jusqu'au redémarrage.

```bash
sudo apparmor_parser -R /etc/apparmor.d/usr.local.bin.atelier-lecteur   # R = remove
sudo rm /etc/apparmor.d/usr.local.bin.atelier-lecteur
sudo rm -f /usr/local/bin/atelier-lecteur /usr/local/bin/atelier-copie /usr/local/bin/atelier-lien
sudo rm -rf /srv/atelier
```

Puis comparez avec le relevé initial, les deux répertoires de contrôle compris :

```bash
sudo aa-status | grep -E "^[0-9]+ profiles"
ls -A /etc/apparmor.d/disable/ /etc/apparmor.d/force-complain/
```

```text
117 profiles are loaded.
23 profiles are in enforce mode.
4 profiles are in complain mode.   [...]
90 profiles are in unconfined mode.
```

Les six compteurs sont identiques au départ et `disable/` est vide : la machine est
rendue. Si l'un d'eux ne retombe pas, cherchez un `flags=(complain)` oublié dans un
fichier de `/etc/apparmor.d/`, puisque c'est là que le mode est écrit.
