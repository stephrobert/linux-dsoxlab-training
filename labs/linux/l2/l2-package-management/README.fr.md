# Lab — gestion de paquets avec dnf

## Rappel

[**dnf sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

`dnf install <pkg>` ajoute un paquet et ses dépendances ; `dnf remove <pkg>` le
retire ; `dnf list installed` et `rpm -q <pkg>` interrogent ce qui est présent.
`rpm -ql <pkg>` liste les fichiers d'un paquet.

## Le cours

Les exemples ci-dessous travaillent sur `httpd-tools`, `nano`, `bc` et `apr` :
le challenge, lui, vous demandera d'autres paquets. Le but est d'apprendre la
boucle installer / vérifier / interroger / défaire, pas de recopier une ligne.

Toutes les sorties de ce cours ont été relevées sur une **AlmaLinux 10.2**
(`dnf` 4.20.0), la même famille que la machine du lab.

### Où en est la machine

Avant de toucher à quoi que ce soit, trois questions : quelle version de DNF,
quels dépôts actifs, combien de paquets installés.

```bash
dnf --version | head -1
dnf repolist
rpm -qa | wc -l
```

Sur la machine de rédaction :

```text
4.20.0
repo id                          repo name
appstream                        AlmaLinux 10 - AppStream
baseos                           AlmaLinux 10 - BaseOS
crb                              AlmaLinux 10 - CRB
extras                           AlmaLinux 10 - Extras
415
```

Ce compte de départ est votre point de comparaison : après une installation
puis son annulation, vous devez retomber dessus. C'est la seule preuve
sérieuse qu'une manipulation n'a rien laissé derrière elle.

`dnf repolist` ne montre que les dépôts **actifs**. Un paquet « introuvable »
vient neuf fois sur dix d'un dépôt désactivé, et `dnf repolist all` ajoute la
colonne d'état :

```bash
dnf repolist all
```

```text
repo id                      repo name                                  status
appstream                    AlmaLinux 10 - AppStream                   enabled
appstream-debuginfo          AlmaLinux 10 - AppStream - Debug           disabled
baseos                       AlmaLinux 10 - BaseOS                      enabled
crb                          AlmaLinux 10 - CRB                         enabled
highavailability             AlmaLinux 10 - HighAvailability            disabled
```

> **Le guide présente `crb` comme un dépôt livré mais désactivé, à activer par
> `dnf config-manager --set-enabled crb`.** Sur l'AlmaLinux 10.2 de ce lab, il
> est **déjà actif** : `dnf repolist all` le donne `enabled` sans qu'on y
> touche. Vérifiez avant d'exécuter la commande d'activation, elle n'a rien à
> faire ici.

### Installer un paquet, et le prouver

`dnf` refait le calcul des dépendances à chaque fois et vous montre son plan
avant d'agir. L'option `--assumeno` répond « non » à la question finale :
vous lisez le récapitulatif sans rien modifier.

```bash
sudo dnf install --assumeno httpd-tools
```

```text
================================================================================
 Package               Arch        Version                 Repository      Size
================================================================================
Installing:
 httpd-tools           x86_64      2.4.63-13.el10_2.4      appstream       82 k
Installing dependencies:
 apr                   x86_64      1.7.5-3.el10            appstream      127 k
 apr-util              x86_64      1.6.3-23.el10_1         appstream       97 k
Installing weak dependencies:
 apr-util-lmdb         x86_64      1.6.3-23.el10_1         appstream       13 k
 apr-util-openssl      x86_64      1.6.3-23.el10_1         appstream       15 k

Transaction Summary
================================================================================
Install  5 Packages
Operation aborted.
```

Un paquet demandé, cinq installés : c'est là tout l'intérêt d'un gestionnaire
de paquets. Le récapitulatif distingue trois blocs qu'il faut savoir lire :
ce que vous avez demandé (`Installing:`), ce qui est **obligatoire** pour le
faire fonctionner (`Installing dependencies:`), et ce qui est **recommandé
sans être requis** (`Installing weak dependencies:`).

Puis pour de vrai :

```bash
sudo dnf install -y httpd-tools
```

```text
Installed:
  apr-1.7.5-3.el10.x86_64               apr-util-1.6.3-23.el10_1.x86_64
  apr-util-lmdb-1.6.3-23.el10_1.x86_64  apr-util-openssl-1.6.3-23.el10_1.x86_64
  httpd-tools-2.4.63-13.el10_2.4.x86_64

Complete!
```

> **`-y` se paie.** Le guide est net : l'option est indispensable en script et
> en CI, mais dangereuse en interactif, parce que vous ne lisez plus le
> récapitulatif et ne voyez donc pas qu'une opération va **supprimer** un
> paquet. Sur un serveur, lancez d'abord sans `-y` (ou avec `--assumeno`) et
> lisez la ligne `Removing`.

`Complete!` ne prouve rien : il dit que la transaction s'est déroulée, pas que
vous avez ce que vous vouliez. Les deux commandes de contrôle sont :

```bash
rpm -q httpd-tools
dnf list installed httpd-tools
```

```text
httpd-tools-2.4.63-13.el10_2.4.x86_64
Installed Packages
httpd-tools.x86_64                 2.4.63-13.el10_2.4                 @appstream
```

`rpm -q` interroge la base RPM locale et renvoie le **NEVRA** complet (nom,
version, release, architecture). `dnf list installed` ajoute la colonne de
droite : le **dépôt d'origine**, ici `@appstream`. Le `@` signale un paquet
installé, par opposition au nom nu d'un paquet seulement disponible.

Quand le paquet est absent, `rpm -q` le dit en clair et sort en erreur :

```bash
rpm -q httpd-tools
```

```text
package httpd-tools is not installed
```

### Retrouver le bon paquet

La moitié du travail consiste à trouver le **nom exact** du paquet. Le guide
insiste sur un point que la pratique confirme : `search` et `provides` ne
cherchent pas au même endroit.

`dnf search` fouille les **noms et les résumés** :

```bash
dnf search apache
```

```text
======================== Name & Summary Matched: apache ========================
ant-apache-bcel.noarch : Optional apache bcel tasks for ant
apache-commons-cli-javadoc.noarch : API documentation for apache-commons-cli
```

Cette commande a une limite qu'il faut mesurer soi-même une fois. Cherchez le
nom d'une **commande** avec `search` :

```bash
dnf search htpasswd
```

```text
No matches found.
```

Pourtant `htpasswd` existe bien et un paquet le livre. `search` ne voit pas le
**contenu** des paquets. C'est `provides` qui indexe les fichiers, et c'est la
commande qui vous sauve devant un `command not found` :

```bash
command -v htpasswd          # rien, code de retour 1
dnf provides "*/bin/htpasswd"
```

```text
httpd-tools-2.4.63-13.el10.x86_64 : Tools for use with the Apache HTTP Server
Repo        : appstream
Matched from:
Filename    : /usr/bin/htpasswd

httpd-tools-2.4.63-13.el10_2.1.x86_64 : Tools for use with the Apache HTTP Server
Repo        : appstream
Matched from:
Filename    : /usr/bin/htpasswd
```

Deux détails de la sortie méritent l'attention. D'abord elle liste **plusieurs
versions** du même paquet : le dépôt en garde l'historique, la plus haute sera
retenue. Ensuite, si le paquet est déjà installé, une des entrées porte
`Repo : @System`, qui désigne la base RPM locale et non un dépôt distant.

Le motif `*/bin/htpasswd` n'est pas un ornement. Avec un chemin partiel ou
inexact, `dnf` échoue et vous souffle lui-même la solution :

```text
Error: No matches found. If searching for a file, try specifying the full path
or using a wildcard prefix ("*/") at the beginning.
```

Une fois le nom trouvé, `dnf info` décrit le paquet **avant** de l'installer :
version, taille, dépôt, licence, description.

```bash
dnf info bc
```

```text
Size         : 125 k
Source       : bc-1.07.1-23.el10.src.rpm
Repository   : baseos
Summary      : GNU's bc (a numeric processing language) and dc (a calculator)
License      : GPL-3.0-or-later
```

Retenez les trois questions : `search` pour un mot-clé, `provides` pour un
fichier ou une commande, `info` pour un paquet déjà identifié.

### Interroger sans rien installer

`dnf repoquery` travaille sur les **métadonnées des dépôts**. Il ne touche
jamais au système, ce qui en fait l'outil d'enquête par excellence avant une
opération risquée.

```bash
dnf repoquery --requires httpd-tools
```

```text
libapr-1.so.0()(64bit)
libaprutil-1.so.0()(64bit)
libcrypt.so.2()(64bit)
libssl.so.3(OPENSSL_3.0.0)(64bit)
rtld(GNU_HASH)
```

Les dépendances ne sont pas exprimées en noms de paquets mais en **capacités**
(ici des bibliothèques partagées) : c'est DNF qui traduit ensuite chaque
capacité en paquet fournisseur. Cela explique le `apr` et le `apr-util` vus
dans le récapitulatif d'installation, qui n'apparaissaient nulle part dans la
commande tapée.

La question symétrique, à poser **avant** de supprimer une bibliothèque :

```bash
dnf repoquery --whatrequires apr-util
```

```text
apr-util-devel-0:1.6.3-23.el10_1.x86_64
apr-util-ldap-0:1.6.3-23.el10_1.x86_64
apr-util-openssl-0:1.6.3-23.el10_1.x86_64
```

Enfin, `dnf repoquery --userinstalled` sépare ce que **vous** avez demandé de
ce qui est arrivé en dépendance. Cette distinction n'est pas cosmétique : elle
change le comportement de `remove`, comme on va le voir.

### Ce que contient un paquet, et d'où vient un fichier

`rpm` répond aux questions locales, sur ce qui est déjà installé. Deux options
suffisent au quotidien.

`rpm -ql` liste les fichiers **livrés** par un paquet :

```bash
rpm -ql httpd-tools
```

```text
/usr/bin/ab
/usr/bin/htdbm
/usr/bin/htdigest
/usr/bin/htpasswd
/usr/bin/httxt2dbm
/usr/bin/logresolve
/usr/share/doc/httpd-tools/LICENSE
/usr/share/man/man1/htpasswd.1.gz
```

`rpm -qf` fait l'inverse : à partir d'un fichier présent sur le disque, il
nomme le paquet **propriétaire**.

```bash
rpm -qf /usr/bin/htpasswd
```

```text
httpd-tools-2.4.63-13.el10_2.4.x86_64
```

Ne confondez pas avec `dnf provides` : `rpm -qf` ne regarde que la machine et
exige que le fichier existe réellement ; `dnf provides` interroge les dépôts et
répond même pour un paquet jamais installé. Le premier sert à l'audit d'un
système, le second à préparer une installation.

`rpm -qi` complète avec les métadonnées, dont la **signature**, qui prouve
l'origine du paquet :

```bash
rpm -qi httpd-tools | head -12
```

```text
Name        : httpd-tools
Version     : 2.4.63
Release     : 13.el10_2.4
Architecture: x86_64
Install Date: Wed 22 Jul 2026 02:37:49 PM UTC
Signature   :
              RSA/SHA256, Wed 01 Jul 2026 11:37:13 AM UTC, Key ID dee5c11cc2a1e572
Source RPM  : httpd-2.4.63-13.el10_2.4.src.rpm
```

La ligne `Source RPM` est instructive : `httpd-tools` est construit à partir
du source `httpd`. Un même paquet source engendre souvent plusieurs paquets
binaires.

### `dnf list installed` ou `rpm -qa` ?

Les deux listent ce qui est installé, et on les croit interchangeables. Ils ne
le sont pas. Comptez :

```bash
dnf list installed | tail -n +2 | wc -l
rpm -qa | wc -l
```

```text
415
416
```

Un paquet d'écart. Il se trouve avec :

```bash
rpm -qa | grep gpg-pubkey
```

```text
gpg-pubkey-c2a1e572-668fe8ef
```

`gpg-pubkey` est un **pseudo-paquet** : la base RPM y range les clés GPG
importées, qui ne viennent d'aucun dépôt et ne contiennent aucun fichier.
`rpm -qa` les montre parce qu'il lit la base telle quelle ; `dnf list
installed` ne les montre pas parce qu'il raisonne en paquets de dépôts.

À retenir : `rpm -qa` est la vue brute de la base RPM, `dnf list installed` la
vue enrichie du dépôt d'origine. Pour un audit exhaustif, `rpm -qa`. Pour
savoir d'où vient un paquet, `dnf list installed`.

### Supprimer : ce que `dnf remove` fait, et ce qu'il ne fait pas

Sur RHEL et dérivées, `dnf remove` **nettoie les dépendances devenues
orphelines**, parce que `clean_requirements_on_remove` est actif par défaut.
On peut le lire dans la configuration :

```bash
cat /etc/dnf/dnf.conf
```

```text
[main]
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
best=True
skip_if_unavailable=False
```

Et le vérifier sur les cinq paquets installés plus haut :

```bash
sudo dnf remove -y httpd-tools
rpm -qa | wc -l
```

```text
Removed:
  apr-1.7.5-3.el10.x86_64                 apr-util-1.6.3-23.el10_1.x86_64
  apr-util-lmdb-1.6.3-23.el10_1.x86_64    apr-util-openssl-1.6.3-23.el10_1.x86_64
  httpd-tools-2.4.63-13.el10_2.4.x86_64

Complete!
415
```

Un paquet nommé, cinq retirés, et le compte revient à son point de départ.

Maintenant le piège, et il est bien réel. Reprenons la même installation, mais
en ayant **explicitement** demandé `apr` au préalable :

```bash
sudo dnf install -y apr
sudo dnf install -y httpd-tools     # n'installe plus que 4 paquets
sudo dnf remove -y httpd-tools
rpm -q apr
rpm -qa | wc -l
```

```text
Removed:
  apr-util-1.6.3-23.el10_1.x86_64          apr-util-lmdb-1.6.3-23.el10_1.x86_64
  apr-util-openssl-1.6.3-23.el10_1.x86_64  httpd-tools-2.4.63-13.el10_2.4.x86_64

apr-1.7.5-3.el10.x86_64
416
```

`apr` est resté, et la machine ne compte plus 415 paquets mais 416. DNF le
laisse en place parce qu'il est marqué comme **installé à la demande de
l'utilisateur** :

```bash
dnf repoquery --userinstalled | grep '^apr'
```

```text
apr-0:1.7.5-3.el10.x86_64
```

C'est la leçon de cette section : **`dnf remove` ne ramène pas forcément la
machine à son état antérieur**. Il retire ce que vous nommez et les orphelines,
mais jamais un paquet que vous aviez demandé vous-même. `dnf autoremove`
n'y changera rien non plus, pour la même raison :

```bash
sudo dnf autoremove --assumeno
```

```text
Dependencies resolved.
Nothing to do.
Complete!
```

### L'historique : inspecter, puis annuler

DNF enregistre **chaque transaction** et sait la rejouer à l'envers. C'est ce
qui le distingue d'un simple installateur, et c'est l'outil correct pour
défaire une manipulation.

```bash
sudo dnf history list
```

```text
ID     | Command line             | Date and time    | Action(s)      | Altered
-------------------------------------------------------------------------------
    13 | remove -y httpd-tools    | 2026-07-22 14:38 | Removed        |    4
    12 | install -y httpd-tools   | 2026-07-22 14:38 | Install        |    4
    11 | install -y apr           | 2026-07-22 14:38 | Install        |    1
    10 | history undo -y 8        | 2026-07-22 14:38 | Removed        |    1
     9 | remove -y nano           | 2026-07-22 14:38 | Removed        |    1
     8 | install -y nano bc       | 2026-07-22 14:38 | Install        |    2
```

Chaque ligne porte un identifiant, la **ligne de commande** telle qu'elle a été
tapée, la date et le nombre de paquets touchés. Notez que les annulations
elles-mêmes y figurent (ID 10) : l'historique n'est pas réécrit, il s'empile.

Avant d'annuler, **inspectez** :

```bash
sudo dnf history info 8
```

```text
Transaction ID : 8
Begin time     : Wed 22 Jul 2026 02:38:34 PM UTC
User           :  <ansible>
Return-Code    : Success
Command Line   : install -y nano bc
Packages Altered:
    Install bc-1.07.1-23.el10.x86_64 @baseos
    Install nano-8.1-3.el10.x86_64   @baseos
```

Vous savez maintenant **qui** a fait quoi, **quand**, avec quel code de retour
et sur quels paquets exactement. C'est ce que `dnf remove` ne vous dira jamais.

L'écart entre les deux approches se mesure sur cette transaction. Un `remove`
ne défait que ce que vous nommez :

```bash
sudo dnf remove -y nano
rpm -q nano bc
```

```text
package nano is not installed
bc-1.07.1-23.el10.x86_64
```

`bc` est toujours là : la transaction 8 n'est annulée qu'à moitié. Alors que
`undo` la reprend en entier :

```bash
sudo dnf history undo -y 8
```

```text
Removed:
  bc-1.07.1-23.el10.x86_64

Complete!
Warning, the following problems occurred while running a transaction:
  Package nevra "nano-8.1-3.el10.x86_64" not installed for action "Removed".
```

Deux enseignements dans cette seule sortie. `undo` a bien retiré `bc`, qu'on
avait oublié. Et il **avertit sans échouer** quand une partie de la transaction
a déjà été défaite : la commande reste jouable même sur un état partiellement
nettoyé.

`undo` ne se limite pas aux installations. Le guide précise que ce qui a été
**mis à jour est rétrogradé** à sa version précédente : c'est le filet de
sécurité après une mise à jour qui casse un service. (Ce cours n'a pas
exécuté de mise à jour, ce point vient du guide.)

> **Réflexe : `dnf history list` avant, `dnf history undo <ID>` après.**
> Relevez l'identifiant le plus haut avant votre première commande, vous
> saurez exactement quoi défaire, et jusqu'où.

### Regarder les mises à jour sans les appliquer

Une mise à jour complète est une opération à part, qui redémarre des services
et se planifie. On commence donc toujours par **lire** avant d'agir. Deux
commandes le font sans rien modifier :

```bash
dnf check-update
```

```text
almalinux-gpg-keys.x86_64              10.2-21.el10                    baseos
c-ares.x86_64                          1.34.6-2.el10_2                 baseos
cloud-init.noarch                      24.4-7.el10_2.1                 appstream
coreutils.x86_64                       9.5-8.el10_2                    baseos
dracut.x86_64                          107-8.el10_2                    baseos
```

```bash
dnf updateinfo summary
```

```text
Updates Information Summary: available
    31 Security notice(s)
         2 Critical Security notice(s)
        20 Important Security notice(s)
         6 Moderate Security notice(s)
         3 Low Security notice(s)
Security: kernel-core-6.12.0-211.34.1.el10_2.x86_64 is an installed security update
Security: kernel-core-6.12.0-211.7.3.el10_2.x86_64 is the currently running version
```

Les deux dernières lignes disent quelque chose d'important : un noyau corrigé
est **installé** mais la machine tourne encore sur l'ancien. Un correctif de
sécurité posé sur le disque n'est pas un correctif appliqué tant que le
redémarrage n'a pas eu lieu.

D'après le guide, la suite se joue en trois commandes que ce cours **n'exécute
pas** (elles modifient tout le système) : `sudo dnf upgrade` met tout à jour,
`sudo dnf upgrade --security` se limite aux correctifs de sécurité, et
`dnf needs-restarting -r` répond à la question « faut-il redémarrer ». Le guide
signale aussi que sur DNF, **`update` et `upgrade` sont deux noms de la même
commande**, contrairement à ce que la mémoire d'APT suggère.

### Où DNF écrit ses journaux

Erreur très répandue : chercher les traces de DNF dans `journalctl`. Il n'y en
a pas, et la commande ne le dit pas franchement.

```bash
journalctl -u dnf
```

```text
-- No entries --
```

Ce n'est pas « rien ne s'est passé », c'est « cette unité n'existe pas ». La
preuve :

```bash
systemctl list-unit-files | grep -i dnf
```

```text
dnf-makecache.service                        static          -
dnf-system-upgrade-cleanup.service           static          -
dnf-system-upgrade.service                   disabled        disabled
dnf-makecache.timer                          enabled         enabled
```

Aucun `dnf.service` : les seules unités concernent le cache des métadonnées et
la montée de version. DNF journalise dans des **fichiers plats** :

```bash
sudo ls -l /var/log/dnf*.log
```

```text
-rw-r--r--. 1 root root  25082 Jul 22 14:39 /var/log/dnf.librepo.log
-rw-r--r--. 1 root root 108238 Jul 22 14:39 /var/log/dnf.log
-rw-r--r--. 1 root root   8432 Jul 22 14:39 /var/log/dnf.rpm.log
```

| Fichier | Contenu | Quand le lire |
|---|---|---|
| `/var/log/dnf.log` | Déroulé de DNF, résolution des dépendances, plugins | Une commande échoue ou se comporte bizarrement |
| `/var/log/dnf.rpm.log` | Actions RPM réelles : `Install`, `Upgrade`, `Erase` | Savoir ce qui a **vraiment** changé sur le disque |
| `/var/log/dnf.librepo.log` | Téléchargements, miroirs, erreurs réseau | Un dépôt est injoignable ou lent |

`dnf.rpm.log` est le plus lisible pour un audit : une ligne horodatée par
paquet touché.

```bash
sudo tail -4 /var/log/dnf.rpm.log
```

```text
2026-07-22T14:38:59+0000 SUBDEBUG Erase: httpd-tools-2.4.63-13.el10_2.4.x86_64
2026-07-22T14:38:59+0000 SUBDEBUG Erase: apr-util-1.6.3-23.el10_1.x86_64
2026-07-22T14:38:59+0000 SUBDEBUG Erase: apr-util-lmdb-1.6.3-23.el10_1.x86_64
2026-07-22T14:38:59+0000 SUBDEBUG Erase: apr-util-openssl-1.6.3-23.el10_1.x86_64
```

### Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `No match for argument: <paquet>` alors que le paquet existe | Métadonnées périmées ou dépôt désactivé | `sudo dnf clean all && sudo dnf makecache`, puis `dnf repolist all` |
| `dnf search <commande>` ne trouve rien | `search` ne lit pas le contenu des paquets | `dnf provides "*/bin/<commande>"` |
| `Error: No matches found. ... using a wildcard prefix` | Chemin partiel donné à `provides` | Chemin complet, ou motif préfixé par `*/` |
| `No such command: config-manager` | Plugin absent (installation minimale) | `sudo dnf install dnf-plugins-core` |
| `journalctl -u dnf` ne renvoie rien | Aucune unité `dnf.service` n'existe | Lire `/var/log/dnf.log` et `/var/log/dnf.rpm.log` |
| Un paquet survit à `dnf remove` de ce qui l'avait tiré | Il est marqué *userinstalled* | `dnf repoquery --userinstalled` pour le confirmer, puis `dnf history undo <ID>` |
| `rpm -qa` et `dnf list installed` ne donnent pas le même nombre | Les pseudo-paquets `gpg-pubkey` | Attendu : `rpm -qa \| grep gpg-pubkey` |
| Une transaction a fait des dégâts | | `dnf history info <ID>` pour lire, `sudo dnf history undo <ID>` pour défaire |

### Pour tout défaire

Relevez l'identifiant courant **avant** de commencer, et annulez vos
transactions dans l'ordre inverse plutôt que d'enchaîner des `remove` :

```bash
sudo dnf history list | head -5      # avant : noter le plus haut ID
# ... vos manipulations ...
sudo dnf history undo -y <ID>        # une transaction, une annulation
rpm -qa | wc -l                      # doit retrouver le compte de départ
```

Le contrôle final est le compte de paquets. S'il ne revient pas à sa valeur
initiale, c'est qu'une transaction n'a pas été annulée, ou qu'un paquet
demandé explicitement est resté en place.
