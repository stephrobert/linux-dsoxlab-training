# Lab — planification récurrente avec un timer systemd

## Rappel

[**Les timers systemd sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/)

Une unité `.timer` déclenche un `.service` selon un planning. Le service est
souvent `Type=oneshot` ; le `[Timer]` a `OnCalendar=` et son `[Install]` a
`WantedBy=timers.target`. `systemctl daemon-reload` prend en compte les nouvelles
unités ; `enable --now` le démarre et le rend persistant. `systemctl list-timers`
montre la prochaine exécution.

## Le cours

Les exemples ci-dessous montent un timer nommé `releve-charge`, qui écrit la
charge système dans `/var/tmp/releve-charge.log` : le challenge, lui, vous
demandera un autre nom d'unité, un autre travail et un autre planning. Le but est
d'apprendre la méthode et de savoir prouver que le timer tourne, pas de recopier
une ligne. Toutes les sorties viennent d'une VM **AlmaLinux 10** en
**systemd 257**.

### Vérifier le planning avant d'écrire l'unité

`systemd-analyze calendar` prend une expression `OnCalendar=`, la normalise et
calcule la **prochaine occurrence**. C'est le premier geste, avant même de créer
un fichier d'unité.

```bash
systemd-analyze calendar 'Mon..Fri *-*-* 08:00'
```

```text
  Original form: Mon..Fri *-*-* 08:00
Normalized form: Mon..Fri *-*-* 08:00:00
    Next elapse: Thu 2026-07-23 08:00:00 UTC
       From now: 16h left
```

L'option `--iterations=3` ajoute les occurrences suivantes, ce qui vérifie le
**rythme** et pas seulement le premier déclenchement. Quelques expressions
utiles, toutes passées par l'outil :

| Expression | Forme normalisée | Sens |
|---|---|---|
| `daily` | `*-*-* 00:00:00` | chaque jour à minuit |
| `hourly` | `*-*-* *:00:00` | au début de chaque heure |
| `Sat *-*-* 22:00:00` | identique | chaque samedi à 22 h |
| `*:*:0/30` | `*-*-* *:*:00/30` | toutes les 30 secondes |

**Le fuseau horaire n'est pas un détail** : `Next elapse` est exprimé dans le
fuseau de la machine, pas dans le vôtre. `timedatectl` répond ici
`Time zone: UTC (UTC, +0000)` : un `OnCalendar=*-*-* 03:00:00` se déclenche donc
à 3 h UTC, soit 5 h du matin en heure française d'été. Le guide, écrit sur une
machine en `CEST`, montre une ligne `(in UTC):` supplémentaire dans la sortie de
`systemd-analyze calendar` : elle n'apparaît **pas** ici, précisément parce que
l'heure locale est déjà l'heure UTC. Si le fuseau de la machine ne convient pas,
`OnCalendar` en accepte un explicite en fin d'expression, et le calcul suit :

```text
$ systemd-analyze calendar '*-*-* 03:00:00 Europe/Paris'
Normalized form: *-*-* 03:00:00 Europe/Paris
    Next elapse: Thu 2026-07-23 01:00:00 UTC
```

Enfin, l'outil **refuse** ce qu'il ne comprend pas, et c'est tout son intérêt. Le
piège classique est d'écrire du cron dans un `OnCalendar` :

```text
$ systemd-analyze calendar '*/15 * * * *'
Failed to parse calendar specification '*/15 * * * *': Invalid argument
```

Le code de retour vaut alors `1`. Même refus pour un jour de semaine écrit en
français (`Lun *-*-* 06:00:00`) ou une heure impossible (`*-*-* 25:00:00`).

### Le couple `.service` + `.timer`

Deux fichiers dans `/etc/systemd/system/`. D'abord le **travail à faire**, un
service `oneshot` : il démarre, fait sa tâche, se termine.

```ini
# /etc/systemd/system/releve-charge.service
[Unit]
Description=Releve de la charge systeme

[Service]
Type=oneshot
ExecStart=/usr/local/bin/releve-charge.sh
```

Le script, en `0755` :

```bash
#!/usr/bin/bash
set -euo pipefail
printf "%s charge=%s\n" "$(date -Is)" "$(cut -d' ' -f1-3 /proc/loadavg)" >> /var/tmp/releve-charge.log
echo "releve ajoute a /var/tmp/releve-charge.log"
```

Puis le **planning**, dans une unité de même nom de base :

```ini
# /etc/systemd/system/releve-charge.timer
[Unit]
Description=Declenche le releve de charge toutes les 30 secondes

[Timer]
OnCalendar=*:*:0/30

[Install]
WantedBy=timers.target
```

`releve-charge.timer` déclenche `releve-charge.service` par simple **convention
de nommage** : rien d'autre ne les relie. Pour rompre cette convention, il faut
une directive `Unit=` dans la section `[Timer]`.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now releve-charge.timer
```

```text
Created symlink '/etc/systemd/system/timers.target.wants/releve-charge.timer' → '/etc/systemd/system/releve-charge.timer'.
```

C'est le **timer** qu'on active, jamais le service. Le service n'a pas de section
`[Install]`, donc rien à activer :

```text
$ systemctl is-enabled releve-charge.service releve-charge.timer
static
enabled
```

`static` veut dire « chargeable, mais pas activable ». Tenter
`systemctl enable releve-charge.service` renvoie un long avertissement
(`The unit files have no installation config...`) sans rien faire. Ce n'est pas
un défaut de configuration : c'est le fonctionnement normal d'un service piloté
par un timer.

### Le voir se déclencher

Un timer déclaré n'a rien prouvé. `systemctl list-timers` donne la prochaine et
la dernière exécution :

```text
$ systemctl list-timers releve-charge.timer
NEXT                        LEFT LAST                        PASSED UNIT                ACTIVATES
Wed 2026-07-22 15:14:00 UTC  18s Wed 2026-07-22 15:13:34 UTC 7s ago releve-charge.timer releve-charge.service
```

> Sans argument, `systemctl list-timers` ne montre que les timers **actifs**.
> Ajoutez `--all` pour voir aussi ceux qui sont chargés mais inactifs : c'est là
> qu'on retrouve un timer qui refuse de démarrer.

Le journal du **service** montre chaque déclenchement. `-o short-precise` affiche
les millisecondes, ce qui servira à la section suivante :

```text
$ journalctl -u releve-charge.service --since '-3min' -o short-precise
Jul 22 15:12:32.142488 atelier systemd[1]: Starting releve-charge.service...
Jul 22 15:12:32.154136 atelier releve-charge.sh[20009]: releve ajoute a /var/tmp/releve-charge.log
Jul 22 15:12:32.155840 atelier systemd[1]: Finished releve-charge.service...
[...]
Jul 22 15:13:34.504436 atelier systemd[1]: Starting releve-charge.service...
Jul 22 15:13:34.513676 atelier releve-charge.sh[20030]: releve ajoute a /var/tmp/releve-charge.log
```

Le `echo` du script atterrit dans le journal sans qu'on ait rien redirigé : la
sortie standard d'un service part dans journald. C'est ce que cron ne fait pas.
Et le résultat produit, la seule preuve qui compte vraiment :

```text
2026-07-22T15:12:32+00:00 charge=0.00 0.00 0.00
2026-07-22T15:13:06+00:00 charge=0.00 0.00 0.00
2026-07-22T15:13:34+00:00 charge=0.00 0.00 0.00
```

### Ce que cron ne sait pas faire

**`AccuracySec`, ou pourquoi le timer part en retard.** Relisez les horodatages
ci-dessus : le planning demandait 15:12:30, 15:13:00 et 15:13:30, le service est
parti à 15:12:32, 15:13:06 et 15:13:34. Entre 2 et 6 secondes de retard, jamais
le même. Ce n'est pas une dérive d'horloge, c'est un réglage :

```text
$ systemctl show releve-charge.timer -p AccuracyUSec -p RandomizedDelayUSec -p Persistent
AccuracyUSec=1min
RandomizedDelayUSec=0
Persistent=no
```

Par défaut, systemd s'accorde **une minute** de latitude pour regrouper les
réveils et économiser le processeur. En ajoutant `AccuracySec=1s` au `[Timer]`,
puis `daemon-reload` et `restart`, les déclenchements retombent sur la seconde
(15:14:00.226, 15:14:30.226, 15:15:00.226). C'est ce qui déroute quand on vient
de cron, qui part à la minute pile.

**`RandomizedDelaySec`, pour étaler les déclenchements.** Avec
`RandomizedDelaySec=5s` sur le même timer, trois passages prévus à 15:16:30,
15:17:00 et 15:17:30 sont partis à 15:16:31.2, 15:17:02.0 et 15:17:34.2 : un
décalage aléatoire, différent à chaque fois. Sur un parc de machines qui se
réveillent toutes à 3 h, c'est ce qui évite d'écrouler le serveur de sauvegarde.

**`Persistent=true`, pour rattraper une occurrence manquée.** Le mécanisme repose
sur un fichier d'horodatage sous `/var/lib/systemd/timers/`, créé dès que le
timer démarre :

```text
$ sudo ls -l /var/lib/systemd/timers/
-rw-r--r--. 1 root root 0 Jul 22 13:50 stamp-logrotate.timer
-rw-r--r--. 1 root root 0 Jul 22 15:16 stamp-releve-charge.timer
```

Le fichier fait **0 octet** : la date du dernier déclenchement est portée par sa
`mtime`, pas par son contenu. Au démarrage du timer, systemd compare cette date
au planning ; s'il manque une occurrence, il déclenche immédiatement. On peut
l'observer sans redémarrer la machine, en reculant l'horodatage. Avec un timer en
`OnCalendar=daily` et `Persistent=true` :

```bash
sudo systemctl stop releve-charge.timer
sudo touch -d '2 days ago' /var/lib/systemd/timers/stamp-releve-charge.timer
sudo systemctl start releve-charge.timer      # il est 15:20:31
```

```text
Jul 22 15:20:31.118653 atelier systemd[1]: Starting releve-charge.service...
Jul 22 15:20:31.124488 atelier systemd[1]: Finished releve-charge.service...
```

Le service part **à l'instant même du `start`**, alors que la prochaine
occurrence prévue est minuit. Sans `Persistent=true`, la même manipulation ne
déclenche rien et l'horodatage n'est même pas relu : sa `mtime` reste à deux
jours en arrière, et le service attend sagement minuit.

> Le rattrapage **au démarrage de la machine** n'a pas été observé ici, faute de
> pouvoir redémarrer la VM d'atelier. Ce qui est vérifié, c'est le mécanisme :
> l'horodatage sur disque, sa comparaison au planning à l'activation du timer, et
> le déclenchement immédiat qui en découle. Au boot, systemd applique cette même
> logique.

### Quand le service échoue

Cassons le script pour qu'il écrive dans un répertoire inexistant. Résultat
inattendu :

```text
     Active: inactive (dead) since Wed 2026-07-22 15:18:31 UTC
    Process: 20373 ExecStart=/usr/local/bin/releve-charge.sh (code=exited, status=0/SUCCESS)

Jul 22 15:18:31 atelier releve-charge.sh[20373]: /usr/local/bin/releve-charge.sh: line 2: /srv/archives/releve-charge.log: No such file or directory
Jul 22 15:18:31 atelier systemd[1]: Finished releve-charge.service...
```

**`SUCCESS`, alors que rien n'a été écrit.** systemd ne juge que le code de
retour du processus, et un script shell renvoie celui de sa **dernière**
commande : ici le `echo`, qui a réussi. Avec `set -euo pipefail` en tête du
script, la première commande en échec arrête tout et le verdict change :

```text
× releve-charge.service - Releve de la charge systeme
     Active: failed (Result: exit-code) since Wed 2026-07-22 15:19:33 UTC
    Process: 20423 ExecStart=/usr/local/bin/releve-charge.sh (code=exited, status=1/FAILURE)
```

L'unité reste marquée en échec jusqu'à ce qu'on le lui dise, et se retrouve donc
dans un inventaire consultable :

```text
$ systemctl list-units --failed
● releve-charge.service loaded failed failed Releve de la charge systeme
```

C'est toute la différence avec cron, qui poste un courriel que personne ne lit.
Une fois la cause corrigée, `sudo systemctl reset-failed releve-charge.service`
efface la marque.

**Le planning invalide, lui, ne se comporte pas comme le dit la théorie.** Sur
systemd 257, un `OnCalendar` fautif n'est pas silencieux : `enable --now` échoue
et le timer refuse de démarrer.

```text
Failed to start essai-syntaxe.timer: Unit essai-syntaxe.timer has a bad unit file setting.
     Loaded: bad-setting (Reason: Unit essai-syntaxe.timer has a bad unit file setting.)
    Trigger: n/a
```

Le silence revient en revanche dès qu'il reste **au moins un** planning valide :
la ligne fautive est ignorée, le timer démarre normalement, et seul
`systemd-analyze verify` le signale.

```text
$ systemd-analyze verify essai-syntaxe.timer
/etc/systemd/system/essai-syntaxe.timer:6: Failed to parse calendar specification, ignoring: Lun *-*-* 06:00:00
```

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Le timer n'apparaît pas dans `list-timers` | il n'est pas actif ; le chercher avec `--all` |
| `Loaded: bad-setting` | le seul `OnCalendar` du timer est invalide, systemd refuse l'unité |
| Le timer tourne mais un planning semble ignoré | une ligne `OnCalendar` fautive parmi d'autres : `systemd-analyze verify` |
| L'unité n'existe pas après création du fichier | `systemctl daemon-reload` oublié |
| Le service part quelques secondes en retard | `AccuracySec` (une minute par défaut) ou `RandomizedDelaySec` |
| Le service part à une heure inattendue | fuseau de la machine : `timedatectl`, ou fuseau explicite dans `OnCalendar` |
| `status=0/SUCCESS` alors que le travail a échoué | le script masque l'erreur ; ajouter `set -euo pipefail` |
| `Active: failed` | lire `journalctl -u <nom>.service`, corriger, puis `systemctl reset-failed` |
| Rien n'est rattrapé après un arrêt machine | `Persistent=true` absent du `[Timer]` |
| `systemctl enable <nom>.service` proteste | normal : le service est `static`, on active le **timer** |

Pour tester le travail sans attendre l'heure, `sudo systemctl start
releve-charge.service` démarre le service directement, sans passer par le timer.

### Tout défaire

Un timer oublié continue de se déclencher. Le retrait complet tient en quatre
gestes, dans cet ordre :

```bash
sudo systemctl disable --now releve-charge.timer
sudo rm -f /etc/systemd/system/releve-charge.timer /etc/systemd/system/releve-charge.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

`disable --now` arrête le timer **et** retire le lien symbolique dans
`timers.target.wants/`, ce qu'un `rm` seul ne ferait pas. Restent deux
vérifications, qu'il faut vraiment faire : `systemctl list-timers --all` et
`systemctl list-units --failed`. Le fichier `stamp-<nom>.timer` sous
`/var/lib/systemd/timers/`, lui, survit à la suppression de l'unité : il ne gêne
rien, mais autant le retirer pour repartir d'un état propre.
