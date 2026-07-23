# Lab — profil de performance tuned

## Rappel

[**tuned sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/)

`tuned` applique un lot nommé de réglages noyau/sysfs. `tuned-adm list` affiche
les profils disponibles, `tuned-adm active` le courant, `tuned-adm profile <nom>`
bascule. Le choix actif est sauvegardé dans `/etc/tuned/active_profile`, donc
persistant. Le service `tuned` doit tourner.

## Le cours

Les exemples ci-dessous basculent entre `balanced`, `powersave` et un profil
maison nommé `atelier-demo` : le challenge, lui, vous demandera un autre profil,
pour un autre usage. Le but est d'apprendre la méthode et de savoir prouver
qu'un profil est réellement en vigueur, pas de recopier une ligne. Toutes les
sorties viennent d'une VM AlmaLinux 10 avec `tuned-2.27.0`.

### Où vivent les profils, et lequel est actif

Un profil est un répertoire contenant un fichier `tuned.conf`. Deux
emplacements, et la règle de préséance qui va avec :

| Emplacement | Contenu |
|---|---|
| `/usr/lib/tuned/profiles/<nom>/tuned.conf` | les profils fournis par la distribution, à ne pas modifier |
| `/etc/tuned/profiles/<nom>/tuned.conf` | vos profils à vous |

Un profil local du même nom qu'un profil système le **remplace**. Vérifié : en
déposant un `/etc/tuned/profiles/powersave/tuned.conf` avec un simple
`summary=Version locale de powersave`, c'est cette description que `tuned-adm
list` affiche, et elle redevient celle du système dès que le répertoire local
est retiré.

L'état courant se lit à trois endroits, et il faut les connaître tous les trois
parce qu'ils ne disent pas la même chose :

```bash
tuned-adm active                  # ce que le démon applique en ce moment
cat /etc/tuned/active_profile     # ce qui sera réappliqué au prochain boot
cat /etc/tuned/profile_mode       # auto (recommandé) ou manual (choisi)
```

Sur la VM de démonstration, avant toute manipulation :

```text
Current active profile: virtual-guest
virtual-guest
auto
```

`auto` signifie que personne n'a choisi : `tuned` a demandé son avis à
`tuned-adm recommend`, qui inspecte le rôle de la machine et répond ici
`virtual-guest`. Dès qu'on fait un `tuned-adm profile <nom>`, le mode passe à
`manual` et la recommandation n'est plus consultée.

```bash
tuned-adm list
```

```text
Available profiles:
- balanced                    - General non-specialized tuned profile
- balanced-battery            - Balanced profile biased towards power savings changes for battery
- desktop                     - Optimize for the desktop use-case
- hpc-compute                 - Optimize for HPC compute workloads
- latency-performance         - Optimize for deterministic performance at the cost of increased power consumption
- network-latency             - ... focused on low latency network performance
- powersave                   - Optimize for low power consumption
[...]
Current active profile: virtual-guest
```

Le choix se fait sur l'**usage** de la machine : `latency-performance` ou
`network-latency` pour une charge sensible au temps de réponse, `powersave` sur
batterie, `virtual-guest` dans une VM, `balanced` en cas de doute. Le guide
compagnon donne le tableau complet. Un mauvais choix ne casse rien : au pire la
machine est sous-optimale, et un second `tuned-adm profile` corrige.

### Ce qu'un profil règle vraiment : des plugins, pas un fichier de sysctl

Ouvrir un `tuned.conf` dissipe l'idée qu'un profil ne serait qu'une liste de
`sysctl`. Chaque section entre crochets est un **plugin** :

```bash
sed -n '1,20p' /usr/lib/tuned/profiles/balanced/tuned.conf
```

```text
[main]
summary=General non-specialized tuned profile

[modules]
cpufreq_conservative=+r

[cpu]
governor=schedutil|ondemand|powersave
energy_perf_bias=normal
boost=1

[acpi]
platform_profile=balanced
[...]
[scsi_host]
alpm=med_power_with_dipm
```

`[cpu]` pilote le gouverneur de fréquence, `[modules]` charge ou décharge des
modules noyau, `[scsi_host]` écrit dans `/sys`, `[vm]` et `[sysctl]` posent des
paramètres noyau. C'est pour cela qu'un profil peut échouer partiellement dans
une VM : l'hyperviseur n'expose pas le matériel que certains plugins veulent
piloter.

Le mot-clé `include=` permet de **dériver** un profil existant plutôt que de le
recopier :

```bash
grep -rn '^include' /usr/lib/tuned/profiles/*/tuned.conf
```

```text
/usr/lib/tuned/profiles/balanced-battery/tuned.conf:7:include=balanced
/usr/lib/tuned/profiles/desktop/tuned.conf:7:include=balanced
/usr/lib/tuned/profiles/hpc-compute/tuned.conf:8:include=latency-performance
/usr/lib/tuned/profiles/network-latency/tuned.conf:7:include=latency-performance
[...]
```

Presque tous les profils fournis sont des dérivés : trois ou quatre profils de
base, et des variantes qui ajoutent leur touche.

### Écrire son propre profil

Le besoin réel est rarement « un des quinze profils fournis » : c'est « celui-ci,
plus deux réglages à moi ». On dérive, on ne recopie pas.

```bash
sudo mkdir -p /etc/tuned/profiles/atelier-demo
sudo tee /etc/tuned/profiles/atelier-demo/tuned.conf <<'EOF'
[main]
summary=Profil de demonstration derive de balanced
include=balanced

[sysctl]
vm.swappiness = 45
net.core.somaxconn = 2048
EOF
```

Il apparaît immédiatement dans la liste, sans redémarrer le service :

```text
- atelier-demo                - Profil de demonstration derive de balanced
```

On l'applique, et on mesure avant/après :

```bash
sysctl -n vm.swappiness net.core.somaxconn     # 30 et 4096
sudo tuned-adm profile atelier-demo
sysctl -n vm.swappiness net.core.somaxconn     # 45 et 2048
```

`tuned-adm profile_info` confirme au passage que le `summary` lu est bien celui
du fichier local.

### Vérifier avec `tuned-adm verify`, et lire le vrai journal

`tuned-adm verify` relit l'état réel du système et le compare aux réglages
attendus par le profil actif. C'est la commande qui répond à « mon profil est-il
encore appliqué ? ». Simulons une dérive :

```bash
sudo sysctl -w vm.swappiness=90
sudo tuned-adm verify
```

```text
Verification failed, current system settings differ from the preset profile.
You can mostly fix this by restarting the TuneD daemon, e.g.:
  systemctl restart tuned
```

Le message ne dit pas **quoi** a dérivé. Le détail est dans
`/var/log/tuned/tuned.log`, et nulle part ailleurs :

```text
ERROR  tuned.plugins.base: verify: failed: 'vm.swappiness' = '90', expected '45'
INFO   tuned.plugins.base: verify: passed: 'net.core.somaxconn' = '2048'
```

Un `sudo systemctl restart tuned` réapplique le profil et `vm.swappiness`
revient à 45.

Sur cette VM, `verify` échoue **même sans dérive**, avec ces lignes :

```text
ERROR  verify: failed: 'module 'cpufreq_conservative' is not loaded'
ERROR  verify: failed: device host0: 'alpm' = 'max_performance', expected 'med_power_with_dipm'
ERROR  verify: failed: device cpu0: 'boost' = 'None', expected '1'
```

Aucune de ces trois lignes ne vient du `tuned.conf` écrit plus haut : elles
viennent de `balanced`, dont le profil hérite. C'est la preuve concrète que
`include=` fonctionne. Et c'est aussi l'échec « normal » en machine virtuelle
signalé par le guide : le module `cpufreq_conservative` est intégré au noyau
(`modprobe: FATAL: Module cpufreq_conservative is builtin`), et les disques
virtuels refusent le pilotage d'énergie (`Errno 95 Operation not supported`).
Sur du matériel physique, `verify` doit passer.

> Piège à connaître : `journalctl -u tuned` ne sert à rien pour diagnostiquer un
> profil. Pendant un changement complet de profil, il n'a affiché que les cinq
> lignes `Starting`/`Started` de systemd. Tout le détail utile (plugin par
> plugin, valeur par valeur) va dans `/var/log/tuned/tuned.log`.

### Le piège qui fait perdre des heures : tuned et `/etc/sysctl.d/`

Sur cette VM, `vm.swappiness` vaut 30 alors que la valeur par défaut du noyau
est 60, et qu'**aucun** fichier ne la déclare :

```bash
grep -rn swappiness /etc/sysctl.conf /etc/sysctl.d/ /usr/lib/sysctl.d/
# (aucune correspondance)
grep -n swappiness /usr/lib/tuned/profiles/virtual-guest/tuned.conf
# 23:vm.swappiness = 30
```

Le coupable est donc le profil actif. Premier réflexe à acquérir : **avant de
chercher un fichier `sysctl` fantôme, regardez le profil tuned**.

Qui gagne quand les deux déclarent le même paramètre ? Le service part **après**
`systemd-sysctl` :

```bash
systemctl show tuned.service -p After --value | tr ' ' '\n' | grep sysctl
# systemd-sysctl.service
```

On pourrait en conclure que tuned écrase l'administrateur. La machine dit
l'inverse. En posant un fichier concurrent :

```bash
echo 'vm.swappiness = 60' | sudo tee /etc/sysctl.d/99-atelier.conf
sudo systemctl restart tuned
sysctl -n vm.swappiness       # 60
```

Et après un **reboot** complet, toujours 60. Le journal de tuned explique
pourquoi :

```text
INFO  tuned.plugins.plugin_sysctl: reapplying system sysctl
INFO  tuned.plugins.plugin_sysctl: Overriding sysctl parameter 'vm.swappiness' from '30' to '60'
```

C'est l'option `reapply_sysctl = 1` de `/etc/tuned/tuned-main.conf`, active par
défaut : après avoir appliqué son profil, tuned **relit** `/etc/sysctl.d/` et
lui laisse le dernier mot. Retenez donc l'ordre réel :

1. le profil tuned bat le défaut du noyau ;
2. un fichier de `/etc/sysctl.d/` bat le profil tuned.

Conséquence pratique : après une telle bataille, `tuned-adm verify` échoue, et
c'est légitime. Il signale `'vm.swappiness' = '60', expected '30'`, autrement
dit « le système ne correspond plus à son profil ». Ce n'est pas un bug, c'est
un arbitrage assumé.

### Ce qui revient en arrière, et ce qui reste

Deux mécanismes cohabitent, et ils ne se défont pas de la même façon.

`tuned` **restaure** ce qu'il a changé. En quittant un profil, il repose les
valeurs qu'il avait relevées avant de l'appliquer :

```bash
sudo tuned-adm profile atelier-demo     # swappiness 45, somaxconn 2048
sudo tuned-adm profile balanced         # swappiness 60, somaxconn 4096
```

`tuned-adm off` fait de même, en plus radical :

```bash
sudo tuned-adm off
tuned-adm active
```

```text
No current active profile.
```

Mesuré avant et après, sur le profil `virtual-guest` : `vm.swappiness` passe de
30 à 60 et `vm.dirty_ratio` de 30 à 20, soit les valeurs par défaut du noyau.
Le journal confirme (`terminating TuneD, rolling back all changes`). Deux effets
de bord à connaître : `/etc/tuned/active_profile` devient **vide**, et
`/etc/tuned/profile_mode` bascule sur `manual`. Le `off` est donc persistant lui
aussi. Pour revenir à la recommandation automatique :

```bash
sudo tuned-adm auto_profile
```

`/etc/sysctl.d/`, lui, ne restaure **rien**. Supprimer le fichier posé plus haut
laisse la valeur en place, et même un `sysctl --system` ne la ramène pas :

```bash
sudo rm -f /etc/sysctl.d/99-atelier.conf
sysctl -n vm.swappiness           # 60, toujours
sudo sysctl --system >/dev/null
sysctl -n vm.swappiness           # 60, encore
sudo systemctl restart tuned
sysctl -n vm.swappiness           # 30 : le profil reprend la main
```

Une valeur `sysctl` vit en mémoire jusqu'au reboot : retirer le fichier
supprime la consigne, pas son effet. Ici c'est tuned qui répare, parce que son
profil déclare explicitement le paramètre. Sans tuned, il aurait fallu la
reposer à la main avec `sysctl -w`.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `Cannot talk to TuneD daemon via DBus. Is TuneD daemon running?` | le service est arrêté : `sudo systemctl enable --now tuned` |
| `It seems that tuned daemon is not running, preset profile is not activated` | idem ; la ligne `Preset profile:` qui suit indique le profil qui sera appliqué au démarrage |
| `Unable to switch profile: Requested profile 'x' doesn't exist.` | faute de frappe ; le profil précédent reste actif, rien n'est cassé |
| `Verification failed, current system settings differ...` | lire `/var/log/tuned/tuned.log` : la ligne `verify: failed:` nomme le paramètre |
| `verify` échoue sur `alpm`, `boost` ou un module noyau | normal en VM : le matériel n'est pas pilotable, `systemctl restart tuned` réapplique ce qui peut l'être |
| Un paramètre ne prend pas la valeur du profil | un fichier de `/etc/sysctl.d/` le déclare aussi et gagne (`reapply_sysctl`) |
| Un paramètre est réglé sans qu'aucun fichier ne le déclare | c'est le profil tuned : `grep -n <param> /usr/lib/tuned/profiles/<profil>/tuned.conf` |
| Le profil n'est plus le bon après reboot | vérifier `/etc/tuned/active_profile` et `/etc/tuned/profile_mode` : en `auto`, c'est `tuned-adm recommend` qui décide |
| `journalctl -u tuned` ne montre rien d'utile | c'est attendu : le détail est dans `/var/log/tuned/tuned.log` |

Pour tout défaire et repartir de l'état initial :

```bash
sudo rm -rf /etc/tuned/profiles/atelier-demo
sudo rm -f /etc/sysctl.d/99-atelier.conf
sudo tuned-adm auto_profile
```
