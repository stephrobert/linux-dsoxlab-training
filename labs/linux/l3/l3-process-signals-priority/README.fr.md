# Lab — priorité de processus avec Nice

## Rappel

[**Processus sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/)

Les valeurs de nice vont de `-20` (priorité max) à `19` (min). `nice -n N cmd`
démarre un processus à une priorité, `renice N -p PID` change celle d'un
processus en cours. Pour un service, `Nice=` dans l'unit (ou un drop-in
`systemctl edit`) le rend durable. Les signaux — `kill -TERM/-HUP/-9` — pilotent
les processus en cours. `ps -o ni -p <pid>` montre le nice courant.

## Le cours

Les exemples ci-dessous travaillent sur des processus de démonstration que vous
créez vous-même et sur un service nommé `atelier-veille` : le challenge, lui,
portera sur un autre service et une autre valeur. Le but est d'apprendre la
méthode et de savoir la vérifier, pas de recopier une ligne. Toutes les sorties
qui suivent proviennent d'une VM AlmaLinux à **un seul cœur**.

### Un signal est un message, et le processus peut y répondre

`kill` porte mal son nom : il **envoie un signal**, et c'est le processus qui
décide quoi en faire. Pour le voir, il faut un processus qui installe des
gestionnaires (`trap`) au lieu de subir les comportements par défaut :

```bash
mkdir -p ~/atelier-signaux
cat > ~/atelier-signaux/veilleur-atelier.sh <<'EOF'
#!/bin/bash
journal=/tmp/veilleur-atelier.log
trap 'echo "$(date +%T) TERM recu : je range et je sors" >> $journal; exit 0' TERM
trap 'echo "$(date +%T) HUP recu : je relis ma configuration" >> $journal' HUP
echo "$(date +%T) demarrage, PID $$" >> $journal
while true; do sleep 1; done
EOF
chmod +x ~/atelier-signaux/veilleur-atelier.sh
```

Lancez-le en arrière-plan et gardez son PID, que `$!` donne toujours :

```bash
~/atelier-signaux/veilleur-atelier.sh &
pid=$!
kill -HUP "$pid"; sleep 2; cat /tmp/veilleur-atelier.log
```

```text
15:33:01 demarrage, PID 21717
15:33:03 HUP recu : je relis ma configuration
```

`SIGHUP` n'a pas tué le processus : son gestionnaire s'est exécuté et la boucle
a repris. C'est le mécanisme derrière « recharger la configuration sans
redémarrer le service ». `ps -o pid,stat,comm -p "$pid"` le confirme, en
tronquant le nom à 15 caractères (`veilleur-atelie` n'est pas une coquille).

Au tour de `SIGTERM`, que le script intercepte pour sortir proprement :

```bash
kill -TERM "$pid"; sleep 2; cat /tmp/veilleur-atelier.log
ps -o pid,stat,comm -p "$pid" || echo "(ps ne trouve plus rien)"
```

```text
15:33:03 HUP recu : je relis ma configuration
15:33:05 TERM recu : je range et je sors
    PID STAT COMMAND
(ps ne trouve plus rien)
```

Relancez le veilleur et envoyez-lui cette fois `SIGKILL` : le processus
disparaît, mais le journal ne gagne aucune ligne.

```text
--- kill -KILL 21759
--- contenu du journal :
15:33:15 demarrage, PID 21759
--- processus encore la ? (disparu)
```

Voilà la distinction fondamentale du sujet : avec `-TERM` le processus **voit**
le signal et peut fermer ses fichiers, vider ses tampons, retirer son verrou ;
avec `-KILL` c'est le noyau qui le supprime, et aucun `trap` ne s'exécute. D'où
la règle : `TERM` d'abord, on attend, `KILL` seulement si rien ne bouge.
`man 7 signal` l'énonce ainsi :

```text
The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored.
```

Dernier point sur les signaux : **le nom est portable, le numéro non.**
`kill -l` liste les signaux de la machine et traduit dans les deux sens
(`kill -l TERM` répond `15`, `kill -l 9` répond `KILL`) :

```text
 1) SIGHUP	 2) SIGINT	 3) SIGQUIT	 4) SIGILL	 5) SIGTRAP
 6) SIGABRT	 7) SIGBUS	 8) SIGFPE	 9) SIGKILL	10) SIGUSR1
11) SIGSEGV	12) SIGUSR2	13) SIGPIPE	14) SIGALRM	15) SIGTERM
```

Ces numéros valent **pour cette architecture**. Extrait du tableau de
`man 7 signal`, dont les colonnes sont x86/ARM, Alpha/SPARC, MIPS et PARISC :

```text
SIGKILL          9           9       9       9
SIGUSR1         10          30      16      16
SIGTERM         15          15      15      15
```

`SIGUSR1` vaut 10 ici, 30 sur Alpha, 16 sur MIPS. Écrivez donc `kill -HUP`
plutôt que `kill -1` : le nom, lui, désigne toujours le même signal.

### Les états d'un processus, et comment en fabriquer un

`ps` résume l'état dans la colonne `STAT` : `R` en cours d'exécution, `S` en
sommeil réveillable, `T` stoppé, `Z` zombie, `D` bloqué sur une E/S non
interruptible. Deux d'entre eux se fabriquent facilement.

Un processus stoppé, avec `SIGSTOP` puis `SIGCONT` :

```bash
sleep 120 & p=$!
kill -STOP "$p"; sleep 1; ps -o pid,stat,comm -p "$p"
kill -CONT "$p"; sleep 1; ps -o pid,stat,comm -p "$p"
```

```text
-- apres kill -STOP
  22497 T    sleep
-- apres kill -CONT
  22497 S    sleep
```

Un zombie, en faisant mourir un enfant que son parent ne récupère pas :

```bash
bash -c 'sleep 1 & exec sleep 60' & z=$!
sleep 3; ps -o pid,ppid,stat,comm --ppid "$z"
```

```text
    PID    PPID STAT COMMAND
  22521   22506 Z    sleep
```

Un zombie ne consomme ni CPU ni mémoire : il ne reste de lui que son code de
retour, que le parent n'a pas lu. Il n'y a donc rien à tuer, et `kill` sur un
zombie ne fait rien. On agit sur le **parent** : `kill -TERM` sur le PID 22506
fait disparaître les deux, `systemd` adoptant puis récupérant l'orphelin.

L'état `D` ne se fabrique pas proprement : il faut une E/S qui ne revient pas
(disque défaillant, montage réseau injoignable). C'est le seul état où `kill -9`
lui-même reste sans effet, le processus ne pouvant être interrompu tant que le
noyau attend le périphérique. Un `D` qui dure est un symptôme matériel ou
réseau, pas un problème de processus.

### `nice` et `renice` : poser puis changer la priorité

`nice -n N commande` fixe la priorité au **lancement**, `renice -n N -p PID` la
change **en cours de route**. Un utilisateur ordinaire ne peut que baisser la
sienne, jamais la remonter :

```bash
sleep 300 & p=$!
renice -n 12 -p "$p"
renice -n 5 -p "$p"; echo "code retour = $?"
sudo renice -n 5 -p "$p"
```

```text
22089 (process ID) old priority 0, new priority 12
renice: failed to set priority for 22089 (process ID): Permission denied
code retour = 1
22089 (process ID) old priority 12, new priority 5
```

Même logique au lancement : `nice -n -5 sleep 2` affiche
`nice: cannot set niceness: Permission denied` et démarre malgré tout la
commande, à nice 0. Le plafond est celui de `ulimit -e`, qui vaut `0` pour un
compte ordinaire sur cette machine. La conséquence pratique : sans `sudo`,
baisser sa priorité est un aller simple.

Reste une colonne qui déroute, `PRI`, affichée à côté de `NI` :

```bash
for n in 0 5 19; do nice -n $n sleep 60 & done
sudo nice -n -5 sleep 60 &
ps -o pid,ni,pri,stat,comm -C sleep
```

```text
    PID  NI PRI STAT COMMAND
  22601   0  19 S    sleep
  22602   5  14 SN   sleep
  22603  19   0 SN   sleep
  22607  -5  24 S<   sleep
```

Dans l'affichage de `ps`, `PRI` vaut `19 - NI` : elle monte quand `NI` descend.
Les deux disent la même chose en sens inverse, et c'est `NI` que vous posez.
Notez au passage les drapeaux de `STAT` : `N` pour une priorité basse, `<` pour
une priorité haute.

### La priorité ne se voit que sous contrainte

Sur une machine au repos, le nice ne change **rien** de visible : il n'y a pas
de file d'attente à arbitrer. Une boucle de calcul seule, à la priorité la plus
basse possible, obtient quand même tout le processeur :

```text
--- seul sur la machine, a nice 19, pendant 5 s :
    PID  NI PRI STAT     TIME COMMAND
  22061  19   0 RN   00:00:04 boucle-atelier.
```

Quatre secondes de CPU en cinq secondes de temps réel, à nice 19. Pour observer
un effet, il faut plus de processus prêts à tourner que de cœurs. `nproc` donne
le nombre de cœurs ; ici il vaut `1`, donc deux boucles suffisent :

```bash
cat > ~/atelier-signaux/boucle-atelier.sh <<'EOF'
#!/bin/bash
while :; do :; done
EOF
chmod +x ~/atelier-signaux/boucle-atelier.sh
nice -n 0  ~/atelier-signaux/boucle-atelier.sh & a=$!
nice -n 19 ~/atelier-signaux/boucle-atelier.sh & b=$!
sleep 10
ps -o pid,ni,pri,stat,time,comm -p "$a" -p "$b"
kill -TERM "$a" "$b"
```

```text
    PID  NI PRI STAT     TIME COMMAND
  22030   0  19 R    00:00:09 boucle-atelier.
  22031  19   0 RN   00:00:00 boucle-atelier.
```

Neuf secondes de CPU contre zéro affichée : l'écart est maximal parce que
l'écart de nice l'est aussi. La valeur exacte dépend de la charge au moment du
test, et une VM partage son processeur avec son hôte : refaites la mesure
plutôt que de citer ce chiffre. Et **arrêtez toujours ces boucles**, elles ne
s'arrêtent pas seules ; quelques secondes suffisent.

### Priorité CPU et priorité d'entrées-sorties sont deux réglages distincts

`nice` arbitre le **temps processeur**. Une sauvegarde qui sature le disque sans
consommer de CPU ne sera donc pas calmée par un `nice` élevé. Le réglage
correspondant pour les E/S est `ionice`, avec ses propres classes :

```text
 -c, --class <class>    name or number of scheduling class,
                          0: none, 1: realtime, 2: best-effort, 3: idle
 -n, --classdata <num>  priority (0..7) in the specified scheduling class,
                          only for the realtime and best-effort classes
```

La classe est bien enregistrée par le noyau : après `ionice -c 3 sleep 30 &`,
la commande `ionice -p $!` répond `idle`.

En revanche, **vérifiez qu'elle produit un effet sur votre stockage avant de
compter dessus**. Sur cette VM, deux écritures concurrentes de 800 Mio en
`oflag=direct`, l'une en `best-effort` et l'autre en `idle`, donnent des débits
très dispersés ; et un essai témoin où les **deux** sont en `best-effort`
produit la même dispersion :

```text
essai   A[-c 2 -n 0] :  2.0 GB/s   B[-c 3]      :  1.5 GB/s
temoin  A[-c 2 -n 0] :  876 MB/s   B[-c 2 -n 0] :  2.2 GB/s
```

Le témoin invalide la mesure : sur un disque virtio servi par le cache de
l'hôte, avec l'ordonnanceur `mq-deadline` (`cat /sys/block/vda/queue/scheduler`),
rien ici ne permet d'affirmer que la classe `idle` ralentit quoi que ce soit.
Retenez la distinction CPU / E/S, qui est réelle, et mesurez sur votre propre
stockage avant d'en tirer une conclusion.

### Rendre la priorité durable pour un service

`renice` sur le processus d'un service ne survit pas au premier redémarrage :

```bash
sudo renice -n 3 -p "$(systemctl show -p MainPID --value atelier-veille)"
sudo systemctl restart atelier-veille
ps -o pid,ni,comm -p "$(systemctl show -p MainPID --value atelier-veille)"
```

```text
22768 (process ID) old priority 15, new priority 3
--- restart du service
  22803  15 sleep
```

La valeur durable se déclare dans l'unit, de préférence dans un drop-in créé par
`systemctl edit <service>`, qui laisse le fichier d'origine intact :

```bash
sudo systemctl edit atelier-veille     # ajouter [Service] puis Nice=15
sudo systemctl daemon-reload
sudo systemctl restart atelier-veille
```

`systemctl cat` montre ce que systemd a réellement assemblé :

```text
# /etc/systemd/system/atelier-veille.service.d/priorite.conf
[Service]
Nice=15
```

Voici le piège, et il vaut d'être vu en entier. Après `daemon-reload` seul, la
configuration annonce déjà la nouvelle valeur alors que le processus en cours
n'a pas bougé :

```text
--- daemon-reload seul :
Nice=15                      <- systemctl show -p Nice
  22685   0 sleep            <- ps -o ni sur le MainPID
```

Il faut **redémarrer** le service pour que son processus naisse avec la nouvelle
priorité :

```text
--- apres restart :
MainPID=22768
  22768  15   4 sleep        <- NI=15, PRI=4
```

D'où les deux vérifications à faire systématiquement, l'une sur la
configuration, l'autre sur l'état réel :

```bash
systemctl show -p Nice <service>
ps -o ni= -p "$(systemctl show -p MainPID --value <service>)"
```

### Dépannage

| Symptôme | Cause probable | Ce qu'il faut faire |
|---|---|---|
| `systemctl show -p Nice` donne la bonne valeur, `ps -o ni` non | Le processus tourne encore avec l'ancienne priorité | `systemctl restart` : la priorité est posée au démarrage du processus |
| Le drop-in est écrit mais `systemctl cat` ne le montre pas | `daemon-reload` non joué, ou fichier hors d'un répertoire `<service>.service.d/` | `sudo systemctl daemon-reload`, puis relire `systemctl cat` |
| `renice: failed to set priority ... Permission denied` | Un compte ordinaire ne peut pas remonter une priorité | Repasser par `sudo`, ou relancer le processus |
| `kill -TERM` reste sans effet | Le processus intercepte `SIGTERM` et prend son temps, ou il est en état `D` | Attendre quelques secondes puis `kill -KILL` ; si l'état est `D`, chercher du côté du disque ou du montage réseau |
| `MainPID` vaut `0` | Le service n'est pas actif | `systemctl status <service>` et lire les journaux avant de toucher à la priorité |
| Deux processus de nice différents avancent pareil | Aucune contention : moins de processus prêts que de cœurs | Comparer sous charge, avec au moins `nproc` + 1 processus actifs |
| `pkill motif` tue votre propre session | Le motif figure aussi dans la ligne de commande du shell courant | Cibler par PID, ou choisir un motif que la commande elle-même ne contient pas |
