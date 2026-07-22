# Lab — planification ponctuelle avec at

## Rappel

[**at sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/)

`at` met en file une commande à exécuter **une seule fois** plus tard, gérée par
`atd`. Passe la commande sur l'entrée standard : `echo 'cmd' | at <heure>`. `atq`
liste les tâches en attente, `at -c <n>` affiche le script d'une tâche, `atrm <n>`
la supprime. Contrairement à cron, elle ne se répète pas.

## Le cours

Les exemples ci-dessous travaillent dans `/tmp/atelier-at` et planifient des
horodatages ou un `uptime` : le challenge, lui, vous demandera une autre
commande et un autre chemin. Le but est d'apprendre la méthode, pas de recopier
une ligne. Toutes les sorties montrées viennent d'une AlmaLinux 10 fraîche, en
fuseau UTC.

### Le prérequis que tout le monde oublie : le paquet, puis le service

Sur une image AlmaLinux minimale, `at` n'est pas là :

```bash
rpm -q at
# package at is not installed
systemctl is-active atd
# inactive
systemctl is-enabled atd
# not-found
```

`not-found` ne veut pas dire « désactivé » : l'unité n'existe pas, parce que le
paquet qui la fournit est absent. Sans le binaire, la commande échoue avant même
de parler d'heure (`at: command not found`). On installe donc, et on regarde ce
que l'installation a fait exactement :

```bash
sudo dnf -y install at
```

```text
Installing       : at-3.2.5-14.el10_1.x86_64                              1/1
Running scriptlet: at-3.2.5-14.el10_1.x86_64                              1/1
Created symlink '/etc/systemd/system/multi-user.target.wants/atd.service' → '/usr/lib/systemd/system/atd.service'.
```

Le paquet a **activé** `atd` au démarrage, mais ne l'a **pas démarré** :

```bash
systemctl status atd --no-pager
```

```text
○ atd.service - Deferred execution scheduler
     Loaded: loaded (/usr/lib/systemd/system/atd.service; enabled; preset: enabled)
     Active: inactive (dead)
```

`enabled` et `inactive (dead)` en même temps : c'est exactement le cas de figure
qui fait perdre des points, parce qu'on lit `enabled` et qu'on passe à la suite.
Il faut les deux, d'où le `--now` :

```bash
sudo systemctl enable --now atd
systemctl is-active atd
# active
```

Le piège inverse existe aussi. Avec `atd` arrêté, `at` **accepte quand même** la
tâche, il prévient seulement qu'il n'a personne à réveiller :

```bash
sudo systemctl stop atd
echo '/bin/true' | at now + 2 minutes
```

```text
job 13 at Wed Jul 22 15:51:00 2026
Can't open /run/atd.pid to signal atd. No atd running?
```

La tâche apparaît bien dans `atq`, et pourtant elle ne partira jamais tant que
le service est arrêté. Une file non vide ne prouve donc rien à elle seule :
vérifiez toujours le service.

### Mettre une commande en file, et la voir partir

C'est ce qui distingue vraiment `at` de cron : on peut regarder la tâche
disparaître.

```bash
mkdir -p /tmp/atelier-at
cd /tmp/atelier-at
atq                                   # file vide : aucune sortie
echo 'date -Is >> /tmp/atelier-at/veille.log' | at now + 1 minute
```

```text
warning: commands will be executed using /bin/sh
job 1 at Wed Jul 22 15:47:00 2026
```

L'avertissement `commands will be executed using /bin/sh` est normal : il n'y a
rien à corriger. Le numéro `1` est l'identifiant de la tâche, c'est lui qu'on
donnera à `at -c` et à `atrm`.

```bash
atq
# 1	Wed Jul 22 15:47:00 2026 a ansible
```

Trois informations : l'identifiant, l'heure prévue, puis la lettre de file
(`a`) et le propriétaire. Une minute plus tard :

```bash
cat /tmp/atelier-at/veille.log
# 2026-07-22T15:47:00+00:00
atq
# (plus rien)
at -c 1
# Cannot find jobid 1
```

La tâche a tourné **à la seconde prévue**, puis a été retirée de la file. Une
tâche `at` est consommée par son exécution : il n'y a rien à nettoyer, et rien
ne se répètera. C'est toute la différence avec une entrée de crontab, qui reste
en place jusqu'à ce qu'on l'enlève.

Le journal de `atd` en garde la trace :

```bash
sudo journalctl -u atd --since '10 min ago' --no-pager
```

```text
Jul 22 15:45:55 systemd[1]: Started atd.service - Deferred execution scheduler.
Jul 22 15:47:00 atd[1787]: Starting job 1 (a0000101c5e1b3) for user 'ansible' (1001)
```

C'est le premier endroit où regarder quand une tâche « n'a rien fait » : si la
ligne `Starting job` est absente, la tâche n'a pas été lancée ; si elle est
présente, le problème est dans la commande.

### Ce que contient réellement une tâche : `at -c`

`at -c <numéro>` affiche le script complet que `atd` exécutera. Surprise à la
première lecture : la commande que vous avez tapée est tout en bas, précédée
d'une trentaine de lignes. En voici le début et la fin :

```text
#!/bin/sh
# atrun uid=1001 gid=1001
# mail ansible 0
umask 22
SHELL=/bin/bash; export SHELL
PWD=/tmp/atelier-at; export PWD
LOGNAME=ansible; export LOGNAME
HOME=/home/ansible; export HOME
[...]
cd /tmp/atelier\-at || {
	 echo 'Execution directory inaccessible' >&2
	 exit 1
}
${SHELL:-/bin/sh} << 'marcinDELIMITER52285d1c'
date -Is >> /tmp/atelier-at/veille.log
marcinDELIMITER52285d1c
```

Le script fait 34 lignes pour une commande d'une ligne. Retenez surtout le `cd`
en avant-dernière position : `at` a mémorisé le **répertoire courant** de la
soumission et s'y replace avant d'exécuter. Si ce répertoire a disparu entre
temps, la tâche s'arrête sur `Execution directory inaccessible` sans exécuter
votre commande.

C'est aussi `at -c` qui permet de prouver qu'une tâche en file planifie bien ce
qu'on croit, sans attendre son heure.

### L'environnement est figé à la soumission, pas à l'exécution

Toutes ces lignes `VAR=...; export VAR` en tête du script sont une copie de
votre environnement **au moment où vous avez tapé la commande**. Elles ne sont
pas relues plus tard. La démonstration tient en quatre lignes :

```bash
export ETIQUETTE=avant-soumission
echo 'echo $ETIQUETTE > /tmp/atelier-at/etiquette.txt' | at now + 1 minute
export ETIQUETTE=change-apres-coup
```

Une minute plus tard, la session dit `change-apres-coup`, et le fichier écrit
par la tâche dit :

```bash
cat /tmp/atelier-at/etiquette.txt
# avant-soumission
```

Une variable maison est donc bien transmise, ce que `at -c 12` confirme en tête
du script (`ETIQUETTE=avant-soumission; export ETIQUETTE`), à côté du
`PWD=/tmp/atelier-at` déjà vu. Conséquence pratique, valable dans les deux sens :

- ce que votre session voit, la tâche le verra (variables, `PATH`, `HOME`,
  répertoire courant) ;
- ce que votre session **ne** voit **pas** au moment du `at`, la tâche ne le
  verra jamais, même si vous le définissez trente secondes après.

Une tâche soumise depuis un environnement particulier (un `PATH` enrichi, un
`source` d'un fichier d'environnement) ne sera donc pas reproductible ailleurs.
D'où le réflexe du guide : **chemins absolus** dans la commande planifiée, et
un script testé à part plutôt qu'une ligne compliquée en direct.

### Écrire l'heure : ce qui passe, ce qui piège

Les formats acceptés se mesurent, ils ne se devinent pas. Toutes les lignes
ci-dessous ont été soumises un **mercredi 22 juillet à 15 h 46** :

| Ce qu'on tape | Ce que `at` répond |
|---|---|
| `now + 5 minutes` | `job 2 at Wed Jul 22 15:51:00 2026` |
| `teatime` | `job 3 at Wed Jul 22 16:00:00 2026` |
| `midnight` | `job 4 at Thu Jul 23 00:00:00 2026` |
| `9:00` | `job 5 at Thu Jul 23 09:00:00 2026` |
| `10:30 tomorrow` | `job 6 at Thu Jul 23 10:30:00 2026` |
| `10:30 08152026` | `job 8 at Sat Aug 15 10:30:00 2026` |

**`teatime` vaut 16:00**, et `midnight` bascule au lendemain. Ces mots-clés sont
pratiques en examen, mais lisez bien la date que `at` vous renvoie : c'est elle
qui fait foi, pas votre intuition.

**Une heure déjà passée aujourd'hui est reportée à demain, sans un mot.** Il
était 15 h 46, `at 9:00` a répondu `Thu Jul 23 09:00:00`. La tâche est acceptée,
elle part le lendemain. Personne ne vous prévient : si vous vouliez ce matin,
c'est raté et vous ne le saurez qu'après coup. Vérifiez systématiquement la date
retournée.

**Un instant réellement dans le passé, lui, est refusé** :

```bash
echo '/bin/true' | at now - 1 hour
# at: refusing to create job destined in the past
```

Quant aux dates, le format court à quatre chiffres ne fait pas ce qu'on croit :

```bash
echo '/bin/true' | at 0815
# job 7 at Thu Jul 23 08:15:00 2026
```

`0815` n'a pas été lu comme le 15 août mais comme **08 h 15**. Le format
jour/mois compact réclame l'année :

```bash
echo '/bin/true' | at 10:30 0815
# syntax error. Last token seen: 0815
# Garbled time
```

`Garbled time` est le message générique de refus, précédé d'une ligne qui
indique où l'analyse a échoué. Autre exemple avec une heure impossible :

```bash
echo '/bin/true' | at 25:00
# Problem in hours specification. Last token seen: 25:00
# Garbled time
```

Ces deux refus rendent un code de retour `1` et **ne créent aucune tâche**.
Les trois écritures suivantes désignent en revanche toutes le même instant :
`10:30 08152026`, `10:30 Aug 15` et `10:30 15.08.2026`.

Enfin, `at -f <fichier>` planifie le contenu d'un script au lieu de lire
l'entrée standard, ce que le guide recommande dès que la commande dépasse une
ligne :

```bash
printf '%s\n' '/usr/bin/uptime >> /tmp/atelier-at/uptime.log' > /tmp/atelier-at/tache.sh
at -f /tmp/atelier-at/tache.sh now + 5 minutes   # job 14 at Wed Jul 22 15:54:00 2026
```

### Inspecter la file et annuler : `atq` et `atrm`

`atq` et `at -l` sont la même commande, `atrm` et `at -r` aussi. La file est
**par utilisateur** : chacun ne voit que ses tâches, `root` les voit toutes.
Après avoir soumis une tâche en `sudo` :

```bash
atq | tail -2
# 13	Wed Jul 22 15:51:00 2026 a ansible
# 14	Wed Jul 22 15:54:00 2026 a ansible

sudo atq | tail -2
# 14	Wed Jul 22 15:54:00 2026 a ansible
# 15	Wed Jul 22 16:19:00 2026 a root
```

La tâche `15`, soumise en root, est invisible depuis le compte ordinaire. Si
vous cherchez une tâche que vous ne trouvez pas, demandez-vous d'abord sous
quel compte elle a été créée.

La suppression prend un ou plusieurs numéros (`atrm 4`). Pour vider toute sa
file d'un coup, on récupère la première colonne :

```bash
for j in $(atq | cut -f1); do atrm "$j"; done
atq                  # aucune sortie : la file est vide
```

Attention, la boucle ci-dessus ne vide que **votre** file. Les tâches de `root`
demandent `sudo atq` et `sudo atrm`.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `at: command not found` | paquet absent | `rpm -q at`, puis `sudo dnf -y install at` |
| `systemctl is-enabled atd` répond `not-found` | l'unité n'existe pas, le paquet manque | installer `at` |
| `Can't open /run/atd.pid to signal atd` | `atd` est arrêté (la tâche est quand même en file) | `sudo systemctl enable --now atd` |
| `atd` `enabled` mais tâche jamais lancée | activé au boot, pas démarré | `systemctl is-active atd` |
| `Garbled time` | format horaire non reconnu | lire le `Last token seen:` de la ligne précédente |
| `at: refusing to create job destined in the past` | instant antérieur à maintenant | viser le futur |
| Tâche partie un jour trop tard | heure déjà passée aujourd'hui, reportée en silence | relire la date renvoyée par `at` |
| `Cannot find jobid <n>` | tâche déjà exécutée ou supprimée | `atq` ; une tâche `at` ne survit pas à son exécution |
| `Execution directory inaccessible` | le répertoire courant de la soumission a disparu | `at -c <n>` pour voir le `cd` mémorisé |
| Tâche exécutée mais aucune sortie visible | la sortie part par courriel, pas dans un terminal | rediriger dans un fichier |
| `You do not have permission` | politique `at.allow` / `at.deny` | `sudo cat /etc/at.allow /etc/at.deny` |

L'avant-dernier point mérite une mesure. Une tâche qui écrit sur la sortie
standard voit ce texte envoyé par courriel à son propriétaire ; sur une machine
sans agent de transport, il est simplement perdu. Après
`echo 'echo bonjour-depuis-la-tache' | at now + 1 minute`, le journal donne :

```text
Jul 22 15:50:00 atd[2067]: Starting job 16 (a0001001c5e1b6) for user 'ansible' (1001)
Jul 22 15:50:00 atd[2070]: Exec failed for mail command: No such file or directory
```

La tâche a bien tourné, sa sortie n'existe plus nulle part. D'où la bonne
pratique du guide : journaliser explicitement, par exemple
`>> /tmp/atelier-at/tache.log 2>&1`, plutôt que compter sur le courriel.

Pour tout défaire et repartir de zéro :

```bash
for j in $(atq | cut -f1); do atrm "$j"; done
sudo sh -c 'for j in $(atq | cut -f1); do atrm "$j"; done'
rm -rf /tmp/atelier-at
```
