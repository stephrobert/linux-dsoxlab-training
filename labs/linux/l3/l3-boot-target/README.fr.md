# Lab — cible de démarrage par défaut

## Rappel

[**Démarrage et reboot sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/)

systemd démarre le système dans une **cible** (target), c'est-à-dire un ensemble
d'unités à activer. `systemctl get-default` affiche la cible retenue au
démarrage, `systemctl set-default <cible>` la change de façon persistante (c'est
un lien symbolique), et `systemctl isolate <cible>` bascule l'état courant sans
rien inscrire sur le disque.

## Le cours

Les commandes ci-dessous ont été jouées sur une AlmaLinux 10 de travail, et les
sorties collées sont les siennes. L'exemple support va dans le sens inverse du
challenge : on y **installe** une cible graphique par défaut sur un serveur qui
n'en a pas besoin, pour voir le mécanisme complet et le prouver par un
redémarrage. À vous de transposer.

### Une cible n'est pas un niveau d'exécution

Les **runlevels** viennent de SysVinit : des niveaux numériques (`0` arrêt, `1`
mono-utilisateur, `3` multi-utilisateur avec réseau, `5` interface graphique,
`6` redémarrage). systemd ne les utilise plus, mais garde une couche de
compatibilité, et ces deux vérités cohabitent sur la même machine.

La preuve est dans le répertoire des unités : les `runlevelN.target` ne sont pas
des unités, ce sont des **liens** vers les vraies cibles.

```bash
ls -l /usr/lib/systemd/system/runlevel*.target
```

```text
runlevel0.target -> poweroff.target
runlevel1.target -> rescue.target
runlevel2.target -> multi-user.target
runlevel3.target -> multi-user.target
runlevel4.target -> multi-user.target
runlevel5.target -> graphical.target
runlevel6.target -> reboot.target
```

Trois niveaux SysV (`2`, `3`, `4`) tombent sur la même cible : la correspondance
n'est pas bijective, elle est **historique**. Un runlevel était un numéro, une
cible est un nom d'unité avec ses dépendances.

La commande `runlevel` répond encore, et elle affiche deux champs : le niveau
**précédent** puis le niveau **courant**, `N` signifiant « aucun précédent
depuis le démarrage ».

```bash
runlevel        # → N 3
who -r          # →          run-level 3  2026-07-22 16:18
```

Ne raisonnez pas sur ce chiffre : c'est une traduction approximative de l'état
systemd, pas la source de vérité.

### La cible par défaut est un lien symbolique

C'est le point qui change la compréhension : la cible par défaut n'est pas une
ligne dans un fichier de configuration, c'est un lien.

```bash
systemctl get-default
ls -l /etc/systemd/system/default.target
```

```text
multi-user.target
lrwxrwxrwx. 1 root root 41 May 26 15:21 /etc/systemd/system/default.target -> /usr/lib/systemd/system/multi-user.target
```

`get-default` ne fait rien d'autre que lire ce lien : `readlink -f` donne la
même réponse. Et `set-default` ne fait rien d'autre que le réécrire, il le dit
lui-même :

```bash
sudo systemctl set-default graphical.target
```

```text
Removed '/etc/systemd/system/default.target'.
Created symlink '/etc/systemd/system/default.target' → '/usr/lib/systemd/system/graphical.target'.
```

Le lien vit dans `/etc/systemd/system/`, il survit donc à une mise à jour des
unités livrées par les paquets dans `/usr/lib/systemd/system/`. C'est aussi pour
cela qu'il est persistant : il est écrit sur le disque, pas en mémoire.

La cible visée doit exister, sinon la commande refuse et ne touche à rien :

```bash
sudo systemctl set-default toto.target
# → Failed to set default target: Unit toto.target does not exist
# echo $?  →  1
systemctl get-default          # → graphical.target, inchangée
```

### Basculer maintenant, ou au prochain démarrage

Ce sont deux gestes différents, et c'est la confusion la plus fréquente :

| Commande | Effet immédiat | Effet au prochain démarrage |
|---|---|---|
| `systemctl isolate <cible>` | oui | aucun |
| `systemctl set-default <cible>` | aucun | oui |

`isolate` démarre les unités de la cible demandée et **arrête toutes celles qui
n'en font pas partie**. Depuis une machine en mode texte, passer à la cible
graphique n'arrête rien (elle contient tout le reste), et le lien par défaut
n'est pas touché :

```bash
systemctl is-active graphical.target    # → inactive
sudo systemctl isolate graphical.target
systemctl is-active graphical.target    # → active
systemctl get-default                   # → multi-user.target, inchangée !
runlevel                                # → 3 5  (on venait de 3, on est en 5)
```

La machine tourne alors dans une cible **différente** de sa cible par défaut.
C'est un état parfaitement normal et parfaitement volatile : un redémarrage le
perd.

Toutes les cibles ne sont pas isolables. Il faut `AllowIsolate=yes` dans
l'unité, sinon systemd refuse :

```bash
sudo systemctl isolate basic.target
# → Failed to start basic.target: Operation refused, unit may not be isolated.
```

> **Prudence sur une machine distante.** `isolate` arrête les unités absentes de
> la cible visée. Basculer vers une cible plus pauvre que celle en cours peut
> couper le réseau, donc votre propre session SSH, sans possibilité de revenir.
> Sur une machine dont vous n'avez pas la console, n'isolez que vers une cible
> qui contient au moins tout ce dont vous dépendez.

### Prouver la persistance par un redémarrage

Poser le lien ne prouve rien : seul un démarrage réel prouve qu'il est lu. Après
le `set-default graphical.target` ci-dessus, redémarrage puis constat :

```bash
sudo systemctl reboot
# ... reconnexion ...
systemctl get-default        # → graphical.target
runlevel                     # → N 5   (aucun précédent : c'est bien un boot)
who -r                       # →          run-level 5  2026-07-22 17:10
systemctl is-active graphical.target multi-user.target
# → active
# → active
```

Les deux cibles sont actives parce que la cible graphique **contient** la cible
multi-utilisateur (voir la sous-section suivante). Le `N` de `runlevel` confirme
qu'on sort d'un démarrage et non d'un `isolate`.

Deux réflexes autour d'un redémarrage, repris du guide :

```bash
systemctl list-units --failed    # avant : un service déjà en échec le restera
systemctl is-system-running      # après : doit répondre « running »
```

Sur la machine d'essai, ces deux commandes donnent `0 loaded units listed.` et
`running` : le démarrage en cible graphique n'a rien cassé, alors même qu'aucune
interface graphique n'est installée.

### Une cible est un ensemble d'unités, et cela se lit

Les cibles actives se listent :

```bash
systemctl list-units --type=target
```

```text
UNIT                     LOAD   ACTIVE SUB    DESCRIPTION
basic.target             loaded active active Basic System
[...]
multi-user.target        loaded active active Multi-User System
network-online.target    loaded active active Network is Online
[...]
27 loaded units listed.
```

Elles sont nombreuses parce qu'elles s'emboîtent : `sysinit.target`, puis
`basic.target`, puis la cible finale. `list-dependencies` déroule cet arbre :

```bash
systemctl list-dependencies multi-user.target
```

```text
multi-user.target
● ├─auditd.service
● ├─chronyd.service
● ├─firewalld.service
● ├─NetworkManager.service
● ├─sshd.service
[...]
● ├─basic.target
● │ ├─paths.target
[...]
```

Sur cette machine l'arbre complet fait 119 lignes. Le rond plein signale une
unité active, le rond vide une unité inactive.

Deux relations différentes peuplent cet arbre, et la distinction est la question
piège classique :

- **`Requires=`** : dépendance **forte**. Si l'unité requise échoue, la cible
  échoue avec elle.
- **`Wants=`** : dépendance **souple**. L'unité est démarrée si elle existe ;
  son absence ou son échec n'empêche pas la cible d'aboutir.

Lisons ces relations sur la cible graphique :

```bash
systemctl show -p Requires -p Wants -p AllowIsolate graphical.target
```

```text
Requires=multi-user.target
Wants=systemd-update-utmp-runlevel.service display-manager.service
AllowIsolate=yes
```

Tout est là. La cible graphique **exige** la cible multi-utilisateur (d'où les
deux actives en même temps plus haut) et **souhaite** en plus un gestionnaire
d'affichage. C'est son seul apport réel.

Or sur cette image serveur, ce gestionnaire n'existe pas :

```bash
systemctl status display-manager.service
# → Unit display-manager.service could not be found.
```

Comme il est en `Wants=` et non en `Requires=`, la cible graphique démarre quand
même, sans rien afficher : la machine a bien redémarré en `run-level 5` avec
zéro unité en échec. Voilà pourquoi une cible graphique par défaut sur un
serveur n'est pas une panne bruyante, mais un réglage silencieusement inutile.

### Rescue et emergency : comprendre sans les déclencher

Deux cibles de dépannage existent, et il faut savoir ce qui les sépare :

| Cible | Ce qu'elle exige | État obtenu |
|---|---|---|
| `rescue.target` | `Requires=rescue.service sysinit.target` | initialisation faite, systèmes de fichiers locaux montés, un shell root, ni services applicatifs ni réseau |
| `emergency.target` | `Requires=emergency.service` | rien d'autre qu'un shell root, la racine montée en lecture seule |

La différence tient en une ligne de leurs unités : `rescue.target` demande
`sysinit.target`, `emergency.target` ne demande rien. C'est le mode de dernier
recours, celui qui sert quand même le mode de secours ne démarre plus (une
erreur dans `/etc/fstab`, par exemple). Pour y réparer quoi que ce soit, il faut
d'abord remonter la racine en écriture :

```bash
mount -o remount,rw /
```

Ces deux cibles ne s'atteignent pas raisonnablement à distance, et la raison est
écrite dans leurs services :

```bash
systemctl cat rescue.service | grep -E 'ExecStart=|StandardInput'
```

```text
ExecStart=-/usr/lib/systemd/systemd-sulogin-shell rescue
StandardInput=tty-force
```

`StandardInput=tty-force` : le shell de secours est **attaché à un terminal**.
Ni le réseau ni `sshd` ne font partie de ces deux cibles, donc un
`systemctl isolate rescue.target` lancé par SSH coupe la session qui l'a lancé
et rend la main à une console à laquelle personne n'est assis.

D'où l'accès par le chargeur d'amorçage : au menu GRUB, touche `e`, on ajoute en
fin de ligne `linux` l'un de ces paramètres, puis `Ctrl+X` pour démarrer une
seule fois avec :

```text
systemd.unit=rescue.target
systemd.unit=emergency.target
```

Ce paramètre ne modifie pas le lien `default.target` : il ne vaut que pour ce
démarrage. Inversement, un `systemd.unit=` oublié dans la configuration
permanente de GRUB fait mentir `get-default` à chaque boot.

> **Ces deux cibles n'ont volontairement pas été exécutées** pendant la
> rédaction de ce cours, ni par `isolate` ni au démarrage : la machine d'essai
> n'est joignable que par SSH, et l'une comme l'autre l'auraient rendue
> injoignable. Ce qui précède vient de la lecture des unités (`systemctl cat`,
> `systemctl show`), pas d'une bascule réelle. Même règle pour vous : ne posez
> jamais `rescue.target`, `emergency.target` ni `poweroff.target` comme cible
> **par défaut** sur une machine distante, vous ne la reverriez pas.

### Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `set-default` accepté mais le démarrage ne change pas | on a lu `runlevel` au lieu du lien | `systemctl get-default` et `ls -l /etc/systemd/system/default.target` font foi |
| `Unit X.target does not exist` | nom mal orthographié, suffixe `.target` oublié | `systemctl list-unit-files --type=target` pour le nom exact |
| `Operation refused, unit may not be isolated` | la cible n'a pas `AllowIsolate=yes` | n'isoler que vers une cible prévue pour |
| La session SSH tombe après un `isolate` | la cible visée ne contient ni réseau ni `sshd` | seule la console permet de revenir : à éviter à distance |
| La cible change au démarrage sans qu'on ait rien fait | un `systemd.unit=` traîne dans les paramètres du noyau | `cat /proc/cmdline`, puis la configuration de GRUB |
| `journalctl -b -1` répond « no persistent journal was found » | le journal n'est pas persistant sur cette image | pas de trace du démarrage précédent : se rabattre sur `systemctl list-units --failed` du démarrage courant |
