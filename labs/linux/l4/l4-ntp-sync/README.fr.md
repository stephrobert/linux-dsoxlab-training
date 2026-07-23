# Lab — synchroniser l'horloge avec chrony

## Rappel

[**La synchronisation du temps avec chrony sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/reseau/chrony/)

`chronyd` est le client NTP sur les systèmes de la famille RHEL. `timedatectl`
affiche et règle le fuseau (`set-timezone`) et active le temps réseau
(`set-ntp`). Un service doit être `enabled` pour revenir après un reboot : qu'il
tourne ne suffit pas.

## Le cours

Les exemples ci-dessous règlent une machine d'atelier sur le fuseau
`Indian/Reunion` et lui ajoutent la source `time.google.com` : le challenge vous
demandera un autre fuseau. Le but est d'apprendre la méthode et de savoir lire
les sorties, pas de recopier une ligne. Toutes les sorties reproduites ici ont
été obtenues sur une AlmaLinux 10 avec `chrony 4.8`.

### Deux horloges, une convention d'affichage

Une machine ne porte pas une horloge mais deux, plus une convention pour les
afficher. `timedatectl` sans argument montre le tout d'un coup :

```bash
timedatectl
```

```text
               Local time: Wed 2026-07-22 15:52:47 UTC
           Universal time: Wed 2026-07-22 15:52:47 UTC
                 RTC time: Wed 2026-07-22 15:52:47
                Time zone: UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

- **Local time** et **Universal time** sont le même instant, la même horloge
  système, affichée deux fois : une fois dans le fuseau configuré, une fois en
  UTC.
- **RTC time** est l'horloge matérielle, celle de la carte mère, qui survit à
  l'extinction et donne l'heure au démarrage avant que le réseau soit disponible.
- **Time zone** n'est qu'une règle de conversion pour l'affichage.
- **System clock synchronized** est le seul champ qui dit si l'heure est tenue
  par une source externe. C'est lui qu'on regarde en premier.

L'horloge matérielle se lit aussi avec `hwclock`, mais sur cette machine
virtuelle KVM la lecture échoue, alors que `timedatectl` affiche pourtant
l'heure du RTC et que l'écriture (`sudo hwclock --systohc`) passe sans erreur :

```bash
sudo hwclock --show
```

```text
hwclock: select() to /dev/rtc0 to wait for clock tick timed out
```

Ne concluez donc pas d'un `hwclock --show` en échec que la machine n'a pas
d'horloge matérielle : fiez-vous à la ligne `RTC time` de `timedatectl`.

### Changer de fuseau ne change pas l'instant

C'est la confusion la plus fréquente. Le fuseau ne déplace pas le temps, il
change la façon de l'écrire. Preuve en trois commandes, avant et après :

```bash
date +"%F %T %Z (%z)"
date -u +"%F %T %Z (%z)"
date +%s
sudo timedatectl set-timezone Indian/Reunion
```

```text
2026-07-22 15:54:08 UTC (+0000)     <- date, avant
2026-07-22 15:54:08 UTC (+0000)     <- date -u, avant
1784735648                          <- secondes depuis l'epoch, avant

2026-07-22 19:54:08 +04 (+0400)     <- date, apres
2026-07-22 15:54:08 UTC (+0000)     <- date -u, apres
1784735648                          <- secondes depuis l'epoch, apres
```

`date` a changé de quatre heures, `date -u` n'a pas bougé d'une seconde, et
l'epoch est rigoureusement identique. Rien ne s'est passé sur l'horloge : seul
le lien `/etc/localtime` a été réécrit.

```bash
ls -l /etc/localtime
```

```text
lrwxrwxrwx. 1 root root 36 Jul 22 19:54 /etc/localtime -> ../usr/share/zoneinfo/Indian/Reunion
```

Le catalogue des fuseaux compte 598 entrées sur cette machine : filtrez-le au
lieu de le lire, avec `timedatectl list-timezones | grep -i reunion`.

Pour scripter une vérification, `timedatectl show` sort les mêmes informations
en `clé=valeur`, et `-p <clé> --value` isole une seule valeur, sans habillage :

```text
Timezone=Indian/Reunion
LocalRTC=no
CanNTP=yes
NTP=yes
NTPSynchronized=yes
[...]
```

Le champ `LocalRTC` mérite un mot. À `no`, l'horloge matérielle contient de
l'UTC ; à `yes`, elle contient l'heure locale. `timedatectl set-local-rtc 1`
bascule dans ce second mode, et `systemd` vous en dissuade lui-même :

```text
Warning: The system is now being configured to read the RTC time in the local time zone
         This mode cannot be fully supported. It will create various problems
         with time zone changes and daylight saving time adjustments. [...]
         If at all possible, use RTC in UTC
```

Sur un serveur, gardez `LocalRTC=no`. Un RTC en heure locale oblige à connaître
le fuseau et l'état de l'heure d'été pour interpréter l'heure du démarrage, ce
qui casse au changement d'heure et lors d'un déplacement de fuseau. Le retour se
fait avec `sudo timedatectl set-local-rtc 0`.

### Qui synchronise réellement, et ce que `set-ntp` pilote

`timedatectl set-ntp` est décrit partout comme « l'interrupteur NTP », mais son
effet dépend de ce qui est installé. Regardez d'abord :

```bash
systemctl list-unit-files --type=service | grep -Ei "chrony|timesync"
```

```text
chrony-wait.service                          disabled        disabled
chronyd-restricted.service                   disabled        disabled
chronyd.service                              enabled         enabled
```

Sur cette AlmaLinux 10, `systemd-timesyncd` n'existe même pas
(`Unit systemd-timesyncd.service could not be found.`) : l'interrupteur agit donc
sur `chronyd`. Et il agit fort. Avant :

```text
timedatectl show -p NTP --value  -> yes
systemctl is-active chronyd      -> active
systemctl is-enabled chronyd     -> enabled
```

Après un `sudo timedatectl set-ntp false` :

```text
timedatectl show -p NTP --value  -> no
systemctl is-active chronyd      -> inactive
systemctl is-enabled chronyd     -> disabled
```

Retenez ce point : cette commande ne se contente pas d'arrêter le service, elle
le **désactive** aussi, donc l'effet survit au reboot. Autre conséquence de ce
couplage : `timedatectl timesync-status`, souvent cité dans les tutoriels,
échoue sur une machine sous chrony (`Failed to query server: The name is not
activatable`), car il interroge `timesyncd`. Sur un système chrony, c'est
`chronyc` qui donne l'état, pas `timedatectl`.

### Lire l'état avec `chronyc`

Deux commandes suffisent. `chronyc sources -v` liste les serveurs interrogés,
avec une légende intégrée qui dispense de mémoriser les marqueurs :

```bash
chronyc sources -v
```

```text
  .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
 / .- Source state '*' = current best, '+' = combined, '-' = not combined,
| /             'x' = may be in error, '~' = too variable, '?' = unusable.
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* isere.sd.ysun.co              2   6   377    44  +2922us[+3431us] +/-   20ms
^+ 172-234-184-36.ip.linode>     2   6   357   175  -5219us[-6067us] +/-   47ms
^+ ciran28.fr                    3   6   377    46  -2182us[-1673us] +/-   46ms
```

Le premier caractère est le mode (`^` = serveur), le second l'état : `*` la
source retenue, `+` une source acceptable combinée à la précédente, `-` une
source écartée du calcul, `?` une source injoignable. **Reach** est un registre
octal des huit dernières sondes : `377` signifie huit réponses sur huit, `0`
aucune. **Stratum** dit la distance à l'horloge de référence, **Poll** le
logarithme en base 2 de l'intervalle d'interrogation (6 vaut 64 secondes).

`chronyc tracking` répond à l'autre question : de combien mon horloge est-elle
fausse, et dérive-t-elle ?

```bash
chronyc tracking
```

```text
Reference ID    : 17A16885 (isere.sd.ysun.co)
Stratum         : 3
System time     : 0.000176131 seconds slow of NTP time
Last offset     : +0.000508828 seconds
Frequency       : 74.489 ppm slow
Update interval : 65.3 seconds
Leap status     : Normal
```

`System time` est l'écart courant, ici 176 microsecondes : c'est ce chiffre qui
prouve une horloge saine. `Frequency` est la dérive propre du quartz, que chrony
mesure et compense en permanence, et qu'il enregistre dans son `driftfile` pour
la retrouver au démarrage suivant. `chronyc sourcestats` complète en donnant,
source par source, le nombre de mesures retenues et l'écart type.

### Dérégler l'horloge et la regarder se recaler

C'est la manipulation la plus parlante du lab. Tant que le temps réseau est
actif, le système refuse qu'on touche à l'heure : `sudo timedatectl set-time
"2020-01-01 00:00:00"` répond `Failed to set time: Automatic time
synchronization is enabled`.

Il faut donc d'abord couper la synchronisation, puis reculer l'horloge. **Restez
sur un décalage modeste**, quelques minutes : un saut de plusieurs heures ou de
plusieurs jours perturbe les journaux, déclenche les tâches planifiées et peut
faire expirer votre session SSH.

```bash
sudo timedatectl set-ntp false
sudo timedatectl set-time "$(date -d '-3 minutes' '+%Y-%m-%d %H:%M:%S')"
timedatectl
```

```text
               Local time: Wed 2026-07-22 19:51:41 +04
[...]
System clock synchronized: no
              NTP service: inactive
```

L'horloge est fausse de trois minutes et le système le sait. On rallume :

```bash
sudo timedatectl set-ntp true
sleep 8
date "+%F %T"
```

```text
2026-07-22 19:51:47     <- juste avant
2026-07-22 19:54:56     <- huit secondes plus tard
```

Le journal du service raconte l'opération, et montre au passage le prix d'un
saut d'horloge :

```bash
sudo journalctl -u chronyd --since "-3 min" --no-pager | tail -3
```

```text
Jul 22 19:51:53 atelier chronyd[2076]: Selected source 162.159.200.1 (2.almalinux.pool.ntp.org)
Jul 22 19:51:53 atelier chronyd[2076]: System clock wrong by 180.536616 seconds
Jul 22 19:54:53 atelier chronyd[2076]: System clock was stepped by 180.536616 seconds
```

Regardez les horodatages de ces trois lignes consécutives : elles passent de
19:51 à 19:54. Le journal contient désormais un trou de trois minutes. C'est
exactement ce qu'on cherche à éviter en production.

### Accélérer plutôt que sauter

Chrony dispose de deux façons de corriger une horloge. Le **slew** modifie
légèrement la vitesse de l'horloge jusqu'à rattraper l'écart : le temps reste
monotone, aucune seconde n'est répétée ni sautée. Le **step** repositionne
l'horloge d'un coup, avec le trou ou le recouvrement que l'on vient de voir.

Le choix est piloté par la directive `makestep 1.0 3` de `/etc/chrony.conf`.
Traduction : n'autoriser un saut que si l'écart dépasse 1 seconde, et seulement
pour les 3 premières mises à jour après le démarrage du service. Au-delà, tout
se corrige par accélération. Vérifions avec un décalage de seulement 0,5 seconde,
sous le seuil, en relevant `System time` toutes les cinq secondes :

```text
T+05s  System time     : 0.481129944 seconds fast of NTP time
T+10s  System time     : 0.000181024 seconds slow of NTP time
T+15s  System time     : 0.000000226 seconds fast of NTP time
```

L'écart fond progressivement et le journal, cette fois, ne contient **aucune**
ligne `System clock was stepped by`. La correction s'est faite en douceur.

C'est le comportement à privilégier sur un serveur en production : une base de
données, un cluster ou un système de fichiers distribué supporte mal qu'un
horodatage recule. Le saut reste utile au démarrage, quand l'écart est trop grand
pour être rattrapé en un temps raisonnable ; on peut le forcer à la main avec
`sudo chronyc makestep`, qui répond `200 OK`.

### Déclarer une source, et les pièges qui coûtent des points

Premier piège, le chemin du fichier. Sur cette AlmaLinux, la configuration est
dans `/etc/chrony.conf`, et le répertoire `/etc/chrony/` n'existe pas
(`ls: cannot access '/etc/chrony/': No such file or directory`). Le guide
compagnon, lui, cite `/etc/chrony/chrony.conf` : c'est l'emplacement Debian et
Ubuntu. Vérifiez toujours lequel des deux existe avant d'éditer.

Second piège, et c'est celui qui fait perdre du temps : **une source ajoutée
n'est pas prise en compte tant que le service n'a pas redémarré**. Après avoir
ajouté une ligne au fichier, `chronyc sources` compte toujours quatre sources et
ne connaît pas la nouvelle :

```bash
echo 'server time.google.com iburst' | sudo tee -a /etc/chrony.conf
chronyc sources | grep -c .    # inchangé
sudo chronyc reload sources    # 200 OK, mais sans effet ici
```

`chronyc reload sources` ne relit que les fichiers du répertoire `sourcedir`
(`/run/chrony-dhcp`), pas `chrony.conf`. Il faut redémarrer avec
`sudo systemctl restart chronyd` :

```text
^+ 27.ip-51-68-44.eu             4   6    17     1  -7934us[-8296us] +/-   43ms
^+ time.cloudflare.com           3   6    17     2   -883us[-1245us] +/-   15ms
^* time4.google.com              1   6    17     1   -678us[-1040us] +/-   12ms
```

La nouvelle source apparaît, en stratum 1, et chrony l'a même retenue (`^*`).
L'option `iburst` explique la rapidité : elle envoie une rafale de requêtes au
démarrage au lieu d'attendre l'intervalle normal.

Troisième piège, savoir reconnaître une source injoignable. En déclarant une
adresse non routable, la ligne apparaît bien mais avec `Reach` à 0 et le
marqueur `?` :

```text
^? 192.0.2.1                     0   7     0     -     +0ns[   +0ns] +/-    0ns
```

Une source listée n'est donc pas une source qui répond. `chronyc activity` résume
la situation (`5 sources online`), et une horloge saine affiche au moins un `^*`.

Enfin, gardez en tête la différence entre tourner et être activé. `systemctl
start` ne concerne que la session en cours, `systemctl enable` inscrit le
service au démarrage : les deux se contrôlent séparément, avec
`systemctl is-active chronyd` et `systemctl is-enabled chronyd`. Et la preuve
finale, celle qui ne se discute pas, tient en une ligne de `timedatectl` :
`System clock synchronized: yes`.
