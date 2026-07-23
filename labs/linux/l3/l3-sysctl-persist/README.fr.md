# Lab — durcissement noyau persistant avec sysctl

## Rappel

[**Durcissement sysctl sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/)

`sysctl -w clé=valeur` change un paramètre noyau maintenant (perdu au reboot). Un
fichier dans `/etc/sysctl.d/*.conf` (`clé = valeur` par ligne) le rend
persistant ; `sysctl --system` recharge tous les fichiers de config.
`sysctl -n <clé>` lit la valeur active.

## Le cours

Les exemples ci-dessous travaillent sur `kernel.pid_max` et
`net.core.somaxconn`, deux paramètres de confort sans effet sur la sécurité :
le challenge, lui, vous demandera d'autres paramètres, avec d'autres valeurs.
Le but est d'apprendre la méthode et les pièges, pas de recopier une ligne.

Toutes les sorties de ce cours ont été relevées sur une VM AlmaLinux 10.2,
noyau `6.12.0-211.7.3.el10_2.x86_64`, avec `sysctl` de `procps-ng 4.0.4`. Les
valeurs par défaut varient d'une distribution et d'un noyau à l'autre : relevez
toujours l'existant avant de le changer.

### Un paramètre noyau est un fichier

`sysctl` ne fait qu'une chose : lire et écrire les variables du noyau exposées
sous `/proc/sys/`. Le nom hiérarchique et le chemin de fichier sont la **même
adresse**, les points remplaçant les slashs. Les deux lectures sont donc
strictement équivalentes :

```console
$ sysctl -n net.core.somaxconn
4096
$ cat /proc/sys/net/core/somaxconn
4096
```

L'écriture aussi, dans les deux sens :

```console
$ echo 2048 | sudo tee /proc/sys/net/core/somaxconn
2048
$ sysctl -n net.core.somaxconn
2048
$ sudo sysctl -w net.core.somaxconn=4096
net.core.somaxconn = 4096
```

Préférez `sysctl` : il valide la clé et vous le dit quand elle n'existe pas,
là où un `echo` dans un chemin fautif crée simplement un fichier ordinaire.

```console
$ sudo sysctl -w kernel.parametre_inexistant=1
sysctl: cannot stat /proc/sys/kernel/parametre_inexistant: No such file or directory
$ echo $?
1
```

Retenez la commande de recherche : la machine expose ici 1090 paramètres
(`sysctl -a | wc -l`), et vous n'en connaîtrez jamais le nom exact de mémoire.

```console
$ sysctl -a --pattern 'vm.swappiness|kernel.pid_max'
kernel.pid_max = 4194304
vm.swappiness = 30
```

### Poser une valeur : maintenant, ou durablement

Trois gestes à ne pas confondre.

| Geste | Commande | Portée |
|---|---|---|
| Lire | `sysctl -n <clé>` | sans objet |
| Écrire à chaud | `sudo sysctl -w <clé>=<valeur>` | **perdu au reboot** |
| Rendre durable | ligne dans `/etc/sysctl.d/*.conf` | relu à chaque démarrage |
| Appliquer sans reboot | `sudo sysctl --system` | relit **tous** les fichiers |

Le couple gagnant est donc toujours le même : **on écrit le fichier**, puis
**on applique avec `sysctl --system`**. Le `-w` seul sert à essayer une valeur,
jamais à configurer une machine.

Le format du fichier est minimal, une affectation par ligne, les espaces autour
du `=` sont libres, `#` commente :

```ini
# /etc/sysctl.d/99-atelier.conf
kernel.pid_max = 65536
```

### L'ordre de lecture, qui décide qui gagne

`sysctl --system` ne lit pas un répertoire mais quatre sources, dans cet ordre :
`/usr/lib/sysctl.d/` (les fichiers du système et des paquets), `/run/sysctl.d/`
(le volatile), `/etc/sysctl.d/` (l'administrateur), puis `/etc/sysctl.conf` tout
à la fin. Il annonce chaque fichier qu'il applique, ce qui en fait le meilleur
outil de diagnostic :

```console
$ sudo sysctl --system
* Applying /etc/sysctl.d/10-atelier.conf ...
* Applying /usr/lib/sysctl.d/10-default-yama-scope.conf ...
* Applying /usr/lib/sysctl.d/10-map-count.conf ...
* Applying /usr/lib/sysctl.d/50-coredump.conf ...
* Applying /usr/lib/sysctl.d/50-default.conf ...
* Applying /usr/lib/sysctl.d/50-libkcapi-optmem_max.conf ...
* Applying /usr/lib/sysctl.d/50-pid-max.conf ...
* Applying /usr/lib/sysctl.d/50-redhat.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
* Applying /etc/sysctl.conf ...
[...]
kernel.pid_max = 131072
[...]
kernel.pid_max = 4194304
```

Lisez bien cette liste : les fichiers **ne sont pas groupés par répertoire**,
ils sont triés par **nom**, tous répertoires confondus. Et comme la dernière
affectation appliquée l'emporte, un `10-` de `/etc/` perd contre un `50-` de
`/usr/lib/`. C'est exactement ce que montre la sortie ci-dessus : notre
`/etc/sysctl.d/10-atelier.conf` demandait `131072`, mais
`/usr/lib/sysctl.d/50-pid-max.conf`, appliqué après lui, a reposé `4194304`.

```console
$ sysctl -n kernel.pid_max
4194304
```

Renommez le même fichier en `99-atelier.conf` et il passe en dernier :

```console
$ sudo sysctl --system
[...]
* Applying /usr/lib/sysctl.d/50-pid-max.conf ...
* Applying /usr/lib/sysctl.d/50-redhat.conf ...
* Applying /etc/sysctl.d/99-atelier.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
[...]
kernel.pid_max = 4194304
kernel.pid_max = 65536
$ sysctl -n kernel.pid_max
65536
```

> **La règle qui vaut d'être retenue.** À noms différents, c'est l'ordre
> lexical du **nom de fichier** qui tranche, pas le répertoire. D'où la
> convention `99-` pour un réglage d'administrateur : il est lu en dernier et
> écrase tout le reste.

Le répertoire ne compte que dans un seul cas : **à nom identique**, le fichier
de `/etc/` masque complètement celui de `/usr/lib/`, qui n'est même plus lu.

```console
$ sudo sysctl --system | grep pid-max
* Applying /etc/sysctl.d/50-pid-max.conf ...
```

Ne vous en servez pas pour un réglage : c'est le mécanisme prévu pour
neutraliser un fichier fourni par un paquet, pas pour poser une valeur.

### Prouver la persistance : le reboot

Un réglage sysctl ne vaut que s'il revient au démarrage. La démonstration tient
en une seule expérience : on pose une valeur par fichier, une autre par `-w`
seul, et on redémarre.

```console
$ cat /etc/sysctl.d/99-atelier.conf
kernel.pid_max = 65536
$ sudo sysctl -w net.core.somaxconn=8192
net.core.somaxconn = 8192
$ sysctl kernel.pid_max net.core.somaxconn
kernel.pid_max = 65536
net.core.somaxconn = 8192
$ sudo systemctl reboot
```

Après redémarrage :

```console
$ sysctl kernel.pid_max net.core.somaxconn
kernel.pid_max = 65536
net.core.somaxconn = 4096
```

Le fichier a rejoué, le `-w` a disparu. C'est le service `systemd-sysctl` qui
relit les mêmes répertoires très tôt au boot :

```console
$ journalctl -b -u systemd-sysctl --no-pager | tail -2
systemd[1]: Starting systemd-sysctl.service - Apply Kernel Variables...
systemd[1]: Finished systemd-sysctl.service - Apply Kernel Variables.
```

### Le piège : supprimer le fichier ne restaure rien

C'est l'erreur qui coûte le plus cher, parce qu'elle ne produit aucun message.
Un fichier de `/etc/sysctl.d/` décrit ce que le noyau doit **poser** au
démarrage ; il ne décrit pas d'état à défaire. Une fois la valeur écrite en
mémoire, elle y reste, et `sysctl --system` n'a rien qui puisse l'annuler.

```console
$ sysctl -n net.core.somaxconn
1024
$ sudo rm /etc/sysctl.d/99-atelier.conf
$ sudo sysctl --system > /dev/null
$ sysctl -n net.core.somaxconn
1024
```

La valeur d'origine était `4096`. Deux façons de la retrouver, et deux
seulement : redémarrer, ou la reposer explicitement.

```console
$ sudo sysctl -w net.core.somaxconn=4096
net.core.somaxconn = 4096
```

> **D'où la règle de méthode.** Relevez la valeur d'origine de chaque paramètre
> **avant** de le changer (`sysctl -n <clé>` dans un fichier à part). Sans ce
> relevé, revenir en arrière suppose un redémarrage, ce qui n'est pas toujours
> possible en production.

Une nuance utile, mesurée sur la même machine : le piège ne se referme que si
**aucun autre fichier** ne déclare le paramètre. `kernel.pid_max` est posé par
`/usr/lib/sysctl.d/50-pid-max.conf`, donc supprimer notre fichier suffit bien à
le ramener à `4194304` dès le `sysctl --system` suivant. `net.core.somaxconn`,
lui, n'est déclaré nulle part : rien ne le repose. Le réflexe pour trancher :

```console
$ grep -rn somaxconn /etc/sysctl.d/ /usr/lib/sysctl.d/ /etc/sysctl.conf
$ echo $?
1
```

### Quand une valeur ne vient pas de sysctl.d

Deux comportements surprennent, mieux vaut les avoir vus une fois.

**Une clé inconnue passe en silence avec `--system`.** Un fichier contenant un
paramètre absent de ce noyau n'a produit ici **aucun message** et un code retour
`0`, parce que `sysctl --system` implique l'option `-e` (ignorer les erreurs).
La même ligne, relue fichier par fichier, se plaint :

```console
$ sudo sysctl -p /etc/sysctl.d/98-test.conf
net.core.somaxconn = 8192
sysctl: cannot stat /proc/sys/kernel/parametre_inexistant: No such file or directory
$ echo $?
1
```

Ne comptez donc pas sur `sysctl --system` pour valider vos fichiers : relisez
chaque fichier avec `sysctl -p <fichier>` après l'avoir écrit.

**Un autre outil peut avoir posé la valeur.** Sur cette VM, `vm.swappiness`
vaut `30` alors qu'aucun fichier sysctl ne le mentionne : c'est `tuned`, actif
par défaut sur AlmaLinux, qui l'impose via son profil.

```console
$ sysctl -n vm.swappiness
30
$ grep -rn swappiness /etc/sysctl.d/ /usr/lib/sysctl.d/ /etc/sysctl.conf
$ tuned-adm active
Current active profile: virtual-guest
$ grep -n swappiness /usr/lib/tuned/profiles/virtual-guest/tuned.conf
23:vm.swappiness = 30
```

`tuned` s'exécute **après** `systemd-sysctl` au démarrage : sur les paramètres
qu'il gère, c'est lui qui a le dernier mot, même contre un fichier `99-`. Quand
un réglage refuse de tenir, cherchez donc au-delà de `/etc/sysctl.d/`.

### Dépannage

| Symptôme | Cause probable | Ce qu'il faut faire |
|---|---|---|
| La valeur revient à l'ancienne après reboot | Posée avec `-w`, sans fichier | Écrire dans `/etc/sysctl.d/` puis `sysctl --system` |
| Le fichier existe mais la valeur ne s'applique pas | Un fichier au nom lexicalement plus grand la réécrit | Lire l'ordre dans la sortie de `sysctl --system`, renommer en `99-` |
| La valeur reste changée après suppression du fichier | Rien ne repose la valeur d'origine | `sysctl -w <clé>=<valeur d'origine>` ou redémarrer |
| Aucune erreur, mais rien ne bouge | Clé mal orthographiée, ignorée par `--system` | Relire le fichier avec `sysctl -p <fichier>` |
| `cannot stat /proc/sys/...` | Le paramètre n'existe pas sur ce noyau | Vérifier le nom avec `sysctl -a --pattern <motif>` |
| Le réglage tient au boot puis change | Un gestionnaire (`tuned`, NetworkManager) repasse derrière | Corriger côté gestionnaire, pas en empilant des fichiers sysctl |

Sur les valeurs de durcissement elles-mêmes, leur justification et les réglages
réseau qui peuvent vous couper l'accès à la machine, le guide compagnon lié
plus haut est la référence : il détaille le jeu complet aligné CIS et ANSSI.
