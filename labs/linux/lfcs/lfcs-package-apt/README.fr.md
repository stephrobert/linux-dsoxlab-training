# Lab — gestion de paquets Debian (apt/dpkg)

## Rappel

[**apt sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/)

`apt-get install|remove` gère les paquets et leurs dépendances ; `apt-mark hold`
fige une version pour qu'`apt upgrade` l'ignore (`apt-mark showhold` liste les
holds) ; `dpkg -l <paquet>` montre l'état d'installation ; `dpkg -S <fichier>` dit
quel paquet possède un fichier. Ce sont les pendants Debian de `dnf` / `rpm -qf`.

## Le cours

Les exemples ci-dessous travaillent sur `cowsay`, `cowsay-off`, `sl` et `gzip` :
le challenge, lui, vous demandera un autre paquet. Apprenez la boucle installer
/ vérifier / marquer / défaire, ne recopiez pas une ligne.

### Où en est la machine

Trois questions avant de toucher à quoi que ce soit : quelles versions d'outils,
combien de paquets installés, et comment sont-ils marqués.

```bash
lsb_release -a | grep -E 'Description|Codename'
apt --version ; dpkg --version | head -1 ; dpkg -l | grep -c '^ii'
apt-mark showmanual | wc -l ; apt-mark showauto | wc -l ; apt-mark showhold
```

```text
Description:	Ubuntu 24.04.4 LTS
Codename:	noble
apt 2.8.3 (amd64)
Debian 'dpkg' package management program version 1.22.6 (amd64).
672
50
622
```

Annoncez toujours vos versions : le format des dépôts, les messages d'erreur et
jusqu'à l'existence de certaines sous-commandes changent d'une version d'APT à
l'autre. Toutes les sorties de ce cours viennent de cette machine.

`showhold` ne renvoie rien : aucun paquet n'est figé au départ. Retenez ces
trois nombres, ce sont vos points de comparaison : après une installation puis
son annulation, vous devez retomber exactement dessus, marquages compris.

### Trois outils, une hiérarchie : dpkg, apt-get, apt

`dpkg` installe **un fichier `.deb`** et rien d'autre : il ne connaît pas les
dépôts et ne va chercher aucune dépendance. Récupérez un paquet qui dépend d'un
autre, absent de la machine :

```bash
cd /tmp && apt-get download cowsay-off
sudo dpkg -i /tmp/cowsay-off_3.03+dfsg2-8_all.deb
```

```text
Unpacking cowsay-off (3.03+dfsg2-8) ...
dpkg: dependency problems prevent configuration of cowsay-off:
 cowsay-off depends on cowsay (>= 3.03+dfsg2-3); however:
  Package cowsay is not installed.
dpkg: error processing package cowsay-off (--install):
 dependency problems - leaving unconfigured
```

`dpkg` sort en erreur (code 1), mais le paquet est quand même **déballé** sur le
disque, simplement pas **configuré**. `dpkg -l cowsay-off` le dit dans sa
colonne d'état :

```text
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
||/ Name           Version      Architecture Description
+++-==============-============-============-==========================
iU  cowsay-off     3.03+dfsg2-8 all          configurable talking cow
```

Les deux lettres se lisent avec la légende affichée juste au-dessus : `i` = état
**souhaité** *Install*, `U` = état **réel** *Unpacked*. `iU` est un paquet à
moitié installé, et une majuscule en seconde colonne signale toujours un
problème. C'est `apt` qui sait réparer, parce que lui connaît les dépôts :

```bash
sudo apt-get install -f -y
```

```text
Correcting dependencies... Done
The following additional packages will be installed:
  cowsay
0 upgraded, 1 newly installed, 0 to remove and 44 not upgraded.
1 not fully installed or removed.
[...]
```

Reste la troisième commande. **`apt` et `apt-get` ne sont pas la même chose** :
`apt` est l'interface interactive, `apt-get` l'interface stable des scripts, et
APT le rappelle dès que sa sortie n'est plus un terminal.

```bash
apt policy bash              # dans un terminal : pas d'avertissement
apt policy bash | cat        # sortie redirigee
```

```text
WARNING: apt does not have a stable CLI interface. Use with caution in scripts.
[...]
```

L'avertissement n'apparaît que dans le second cas : APT détecte qu'il est lu par
un programme et prévient que son affichage peut changer sans préavis. Dans un
script, écrivez `apt-get install -y` et `apt-cache policy`, qui ne l'affichent
jamais.

### Le cache et les dépôts

`apt update` ne met à jour **aucun logiciel** : il télécharge les **index** des
dépôts. Sur une machine dont les index datent, un paquet parfaitement existant
devient introuvable :

```bash
ls -l --time-style=+%F /var/lib/apt/lists/*noble_main*Packages
sudo apt-get install -y sl
apt policy sl
```

```text
-rw-r--r-- 1 root root 7165069 2024-04-24 [...]noble_main_binary-amd64_Packages
E: Unable to locate package sl
```

`apt policy sl` ne renvoie rien du tout : APT n'a jamais entendu parler de ce
paquet. Le réflexe est le même dans les deux cas, rafraîchir les index :

```bash
sudo apt-get update
```

```text
Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease
Get:3 http://archive.ubuntu.com/ubuntu noble-updates InRelease [126 kB]
Get:12 http://archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages [1676 kB]
[...]
Fetched 7740 kB in 1s (6620 kB/s)
```

`Hit` signale un index inchangé, `Get` un téléchargement effectif. Les dépôts
interrogés sont déclarés dans `/etc/apt/sources.list.d/`. Sur Ubuntu 24.04, le
vieux fichier `/etc/apt/sources.list` ne contient plus qu'un renvoi : « *Ubuntu
sources have moved to the /etc/apt/sources.list.d/ubuntu.sources file, which
uses the deb822 format* ». Ce format remplace la ligne unique historique par un
bloc de champs nommés, dans un fichier `.sources` :

```text
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: noble noble-updates noble-backports
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

`Signed-By` est le champ de sécurité : il lie le dépôt à sa clé de signature et
remplace l'ancien `apt-key`, supprimé depuis Debian 12.

Une fois les index à jour, `apt-cache policy` répond à la question « d'où
viendrait ce paquet » :

```bash
apt-cache policy cowsay
```

```text
cowsay:
  Installed: 3.03+dfsg2-8
  Candidate: 3.03+dfsg2-8
  Version table:
 *** 3.03+dfsg2-8 500
        500 http://archive.ubuntu.com/ubuntu noble/universe amd64 Packages
        100 /var/lib/dpkg/status
```

`Installed` est la version présente, `Candidate` celle qui s'installerait, et la
table donne l'origine avec sa **priorité** (500 pour un dépôt, 100 pour la base
locale `dpkg`). Le paquet vient du composant `universe`, ce qui explique l'échec
précédent : l'index d'`universe` n'avait jamais été téléchargé.

Pour voir ce qui attend sans rien appliquer :

```bash
apt list --upgradable 2>/dev/null | tail -n +2 | wc -l
sudo apt-get -s upgrade | grep -E '^[0-9]+ upgraded'
sudo apt-get -s full-upgrade | grep -E '^[0-9]+ upgraded'
```

```text
44
40 upgraded, 0 newly installed, 0 to remove and 4 not upgraded.
44 upgraded, 6 newly installed, 0 to remove and 0 not upgraded.
```

`-s` est une simulation et ne modifie rien. `upgrade` laisse quatre paquets de
côté, listés sous `The following packages have been kept back` : ceux qui
exigeraient d'**ajouter** des paquets, ce qu'`upgrade` refuse. `full-upgrade`
accepte, et installe six paquets de plus.

### Interroger dpkg : contenu, propriétaire, état

`dpkg` répond aux questions **locales**. Trois options couvrent le quotidien.

```bash
dpkg -s cowsay | head -2        # etat et metadonnees
dpkg -L cowsay | sed -n '3,4p'  # fichiers livres par le paquet
dpkg -S /usr/games/cowsay       # quel paquet possede ce fichier
```

```text
Package: cowsay
Status: install ok installed
/usr/games
/usr/games/cowsay
cowsay: /usr/games/cowsay
```

`dpkg -S` répond à « d'où sort ce binaire ». Attention à sa limite : elle ne
connaît que les fichiers **livrés par un paquet**. Un fichier créé par le
système ou par vous n'a pas de propriétaire, et la commande sort en erreur :
`dpkg -S /etc/hostname` répond `dpkg-query: no path found matching pattern
/etc/hostname`.

### Manuel, automatique, gelé : les marquages d'APT

APT retient **pourquoi** chaque paquet est là. Reprenons l'installation faite
plus haut : `apt-mark showmanual cowsay cowsay-off` ne renvoie que `cowsay-off`,
posé à la main, et `apt-mark showauto cowsay cowsay-off` ne renvoie que
`cowsay`, arrivé en dépendance.

Cette distinction commande le comportement de la suppression, et c'est **la**
différence à connaître avec `dnf` :

```bash
sudo apt-get remove -y cowsay-off && dpkg -l cowsay | tail -1
```

```text
The following package was automatically installed and is no longer required:
  cowsay
Use 'sudo apt autoremove' to remove it.
[...]
Removing cowsay-off (3.03+dfsg2-8) ...
ii  cowsay         3.03+dfsg2-8 all          configurable talking cow
```

`cowsay` est resté. Contrairement à `dnf remove`, **`apt remove` ne nettoie pas
les dépendances devenues orphelines** : il le signale et attend une seconde
commande, `sudo apt-get autoremove --dry-run | grep '^Remv'` affichant alors
`Remv cowsay [3.03+dfsg2-8]`.

Le troisième marquage est le **gel** : `apt-mark hold` empêche qu'une mise à
jour touche un paquet.

```bash
sudo apt-mark hold sl && apt-mark showhold && dpkg -l sl | tail -1
```

```text
sl set on hold.
sl
hi  sl             5.02-1       amd64        Correct you if you type `sl' by mistake
```

`hi` remplace `ii` : l'état souhaité n'est plus *Install* mais *Hold*. Le gel se
lit aussi dans `dpkg --get-selections sl`, qui renvoie `sl hold`.

Un point que le guide ne précise pas : **le gel bloque la mise à jour
automatique, pas une demande explicite**. Sur un paquet gelé ayant une mise à
jour en attente, comparez les deux simulations :

```bash
sudo apt-get -s upgrade | grep -A1 'kept back'
sudo apt-get -s install gzip | grep -A1 'held packages'
```

```text
The following packages have been kept back:
  gzip [...]
The following held packages will be changed:
  gzip
```

`upgrade` met le paquet de côté ; `install <paquet>` avertit puis passe outre.
Un hold protège d'une mise à jour de masse, il ne protège pas de vous.
`sudo apt-mark unhold <paquet>` annule le gel.

### Ce qu'APT trace, et ce qu'il ne sait pas défaire

C'est l'écart le plus marquant avec RHEL : **il n'y a pas d'équivalent de
`dnf history undo`**. La sous-commande n'existe pas, `apt history` répond
`E: Invalid operation history`. Ce qui existe, ce sont deux journaux en texte
plat : `/var/log/apt/history.log` enregistre les transactions APT avec la
commande tapée et son auteur, `/var/log/dpkg.log` descend d'un cran et trace
chaque **changement d'état**.

```bash
sudo tail -5 /var/log/apt/history.log
sudo grep cowsay-off /var/log/dpkg.log | head -3
```

```text
Start-Date: 2026-07-22  17:37:29
Commandline: apt-get remove -y cowsay-off
Requested-By: ansible (1001)
Remove: cowsay-off:amd64 (3.03+dfsg2-8)
End-Date: 2026-07-22  17:37:29
2026-07-22 17:36:57 install cowsay-off:all <none> 3.03+dfsg2-8
2026-07-22 17:36:57 status half-installed cowsay-off:all 3.03+dfsg2-8
2026-07-22 17:36:57 status unpacked cowsay-off:all 3.03+dfsg2-8
```

Comparez les horodatages : le `dpkg -i` de 17:36:57 figure dans `dpkg.log` mais
**pas** dans `history.log`, dont la première entrée de la séance est
l'`apt-get install -f` de 17:37:05. Un audit mené sur le seul journal d'APT rate
donc tout ce qui a été posé à la main. Faute d'`undo`, la remise en état se fait
avec les marquages : `apt-mark showmanual` dit ce que vous avez demandé, `apt
autoremove` retire le reste.

### Dépannage et retour à l'état initial

| Symptôme | Cause probable | Solution |
|---|---|---|
| `E: Unable to locate package <p>`, ou `apt policy <p>` muet | Index absent ou périmé | `sudo apt-get update`, puis `apt-cache policy <p>` |
| `dependency problems - leaving unconfigured` | `dpkg -i` sans les dépendances | `sudo apt-get install -f` |
| État `iU` dans `dpkg -l` | Paquet déballé, non configuré | `sudo apt-get install -f` |
| `WARNING: apt does not have a stable CLI interface` | `apt` utilisé dans un script | `apt-get` / `apt-cache` |
| Un paquet reste après `apt remove` | Il est marqué *auto* et non demandé | `sudo apt autoremove` |
| Un paquet refuse de se mettre à jour | Il est gelé | `apt-mark showhold`, puis `unhold` |
| `dpkg was interrupted` (d'après le guide) | Installation coupée | `sudo dpkg --configure -a` |

Pour tout défaire, relevez vos trois nombres **avant** de commencer, puis :

```bash
sudo apt-mark unhold <paquet>          # d'abord degeler
sudo apt-get purge -y <paquet>         # purge = paquet + configuration
sudo apt-get autoremove --purge -y     # les orphelines
dpkg -l | grep -c '^ii' ; apt-mark showhold   # compte initial, holds vides
```

Plus sûr encore, comparez des listes plutôt que des comptes : gardez la sortie
de `dpkg -l | grep '^ii' | awk '{print $2}' | sort` avant et après, puis
`diff`. Deux comptes égaux peuvent cacher un paquet ajouté et un autre retiré.
