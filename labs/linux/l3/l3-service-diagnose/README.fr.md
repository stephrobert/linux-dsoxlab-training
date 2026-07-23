# Lab — Diagnostiquer un service systemd en crash loop

## Rappel

[**Dépanner un service Linux qui ne démarre pas avec systemd**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/service-ne-demarre-pas/)

Un service dont l'`ExecStart` échoue toujours pour la même raison, et qu'une
directive `Restart=` relance sans fin, part en boucle de redémarrage. Le guide
ramène le dépannage à cinq étapes : lire l'état, lire les journaux, vérifier la
configuration, corriger, relancer et contrôler. Deux commandes répondent à la
grande majorité des cas, `systemctl status` et `journalctl`. Le code de sortie
oriente le diagnostic : en dessous de 125 il vient du programme lui-même, à
partir de 200 c'est systemd qui n'a pas réussi à préparer l'environnement
d'exécution, et l'erreur est alors dans l'unité, pas dans le programme.

## Le cours

Les exemples ci-dessous portent sur un service de démonstration,
`releve-metriques`, fabriqué pour l'occasion sur une machine d'atelier : le
challenge, lui, vous confie un autre service, sous un autre nom, avec une autre
panne. Ce qui se transpose n'est pas une commande de réparation, c'est un ordre
de lecture.

### Trois lectures, toujours dans le même ordre

Ce lab enseigne une méthode. Elle tient en trois gestes, et l'ordre compte
autant que les commandes :

1. `systemctl status <unité>` donne l'état, le code de sortie et les dix
   dernières lignes de journal ;
2. `journalctl -u <unité> -b --no-pager` donne le journal complet de cette
   unité pour le démarrage courant ;
3. dans ce journal, on cherche le **premier** message d'erreur, pas le dernier.

Cette troisième règle est celle qui sépare le débutant du praticien. Voici
pourquoi, mesuré sur l'atelier. Le service `releve-metriques` boucle, et voici
la fin de son journal :

```text
Jul 22 15:47:16 atelier systemd[1]: releve-metriques.service: Scheduled restart job, restart counter is at 4.
Jul 22 15:47:18 atelier systemd[1]: releve-metriques.service: Scheduled restart job, restart counter is at 5.
Jul 22 15:47:18 atelier systemd[1]: releve-metriques.service: Start request repeated too quickly.
Jul 22 15:47:18 atelier systemd[1]: Failed to start releve-metriques.service - Releve de metriques (atelier).
```

Ces quatre lignes ne disent rien de la panne. Elles décrivent la fin d'une
boucle, c'est-à-dire un symptôme de la cinquième tentative. La cause est en
tête du même journal :

```text
Jul 22 15:47:12 atelier systemd[1]: Started releve-metriques.service - Releve de metriques (atelier).
Jul 22 15:47:12 atelier releve-metriques[1338]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
Jul 22 15:47:12 atelier systemd[1]: releve-metriques.service: Main process exited, code=exited, status=78/CONFIG
```

D'où le réflexe : `journalctl -u <unité> -b --no-pager | head -20`, jamais
`tail`.

> **Le journal n'est pas forcément conservé d'un démarrage à l'autre.** Sur
> l'atelier, `/var/log/journal` n'existe pas : le journal vit en mémoire et
> `journalctl --list-boots` ne connaît qu'un seul démarrage. Concrètement,
> redémarrer la machine efface les preuves. On diagnostique **avant** de
> redémarrer, et l'on vérifie l'état des lieux avec `ls -d /var/log/journal`.

### Signature 1 : le binaire n'a pas pu être lancé (`203/EXEC`)

Première panne : l'unité pointe vers un `ExecStart` qui n'existe pas.

```bash
systemctl status releve-metriques.service
```

```text
● releve-metriques.service - Releve de metriques (atelier)
     Loaded: loaded (/etc/systemd/system/releve-metriques.service; disabled; preset: disabled)
     Active: activating (auto-restart) (Result: exit-code) since Wed 2026-07-22 15:43:22 UTC; 809ms ago
    Process: 3530 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=203/EXEC)
   Main PID: 3530 (code=exited, status=203/EXEC)
```

Trois indices se lisent d'un coup : `activating (auto-restart)` (le service
n'est pas stable, systemd est entre deux tentatives), `Result: exit-code` (le
processus est mort de lui-même, il n'a pas été tué) et `status=203/EXEC`. Le
journal nomme la cause :

```text
(etriques)[3527]: releve-metriques.service: Unable to locate executable '/usr/local/sbin/releve-metriques': No such file or directory
(etriques)[3527]: releve-metriques.service: Failed at step EXEC spawning /usr/local/sbin/releve-metriques: No such file or directory
```

Attention au piège : le même code `203/EXEC` recouvre deux causes distinctes.
En déposant le script sans lui donner le bit d'exécution
(`-rw-r--r--`), le code ne change pas, mais le message oui :

```text
(etriques)[3720]: releve-metriques.service: Unable to locate executable '/usr/local/sbin/releve-metriques': Permission denied
```

`No such file or directory` renvoie au chemin, `Permission denied` au mode. Le
code seul ne suffit donc pas, c'est le couple code plus message qui tranche.

### Signature 2 : le programme refuse sa configuration

Le script rendu exécutable, la boucle continue, mais la signature change du
tout au tout :

```text
    Process: 3798 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=78)
   Main PID: 3798 (code=exited, status=78)
```

```text
releve-metriques[3795]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
systemd[1]: releve-metriques.service: Main process exited, code=exited, status=78/CONFIG
```

Ici le code est **inférieur à 125**, donc il vient du programme et non de
systemd. Le message qui l'accompagne est émis par le programme lui-même (notez
le préfixe `releve-metriques[3795]` au lieu de `systemd[1]`) : c'est lui qui
dit quel fichier lui manque. Nuance utile : `systemctl status` affiche `78`
brut, tandis que le journal traduit `78/CONFIG`, parce que systemd connaît la
convention `sysexits.h`.

Un fichier présent mais incorrect donne le même code et un autre message. Avec
une clé mal orthographiée dans `/etc/releve-metriques.conf` :

```text
releve-metriques[3835]: erreur: cle intervalle absente ou non numerique dans /etc/releve-metriques.conf (lu: '')
```

Autrement dit, dès que le code est applicatif, le journal du programme est la
seule source utile, et il faut aller lire ce que le programme attend
(`systemctl cat <unité>` donne le chemin de l'`ExecStart`, qu'on peut ensuite
ouvrir).

### Signature 3 : systemd n'a pas pu préparer l'exécution (`217/USER`, `200/CHDIR`)

Troisième famille : le programme n'a jamais démarré, systemd a échoué avant.
En ajoutant à l'unité un répertoire de travail qui n'existe pas :

```text
    Process: 3960 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=200/CHDIR)
```

```text
(etriques)[3957]: releve-metriques.service: Changing to the requested working directory failed: No such file or directory
(etriques)[3957]: releve-metriques.service: Failed at step CHDIR spawning /usr/local/sbin/releve-metriques: No such file or directory
```

En ajoutant en plus un `User=` qui n'existe pas sur la machine :

```text
    Process: 4066 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=217/USER)
```

```text
(etriques)[4064]: releve-metriques.service: Failed to determine user credentials: No such process
(etriques)[4064]: releve-metriques.service: Failed at step USER spawning /usr/local/sbin/releve-metriques: No such process
```

Deux enseignements. D'abord, le nom de l'étape (`Failed at step USER`,
`step CHDIR`, `step EXEC`) désigne directement la directive fautive : `User=`,
`WorkingDirectory=`, `ExecStart=`. Ensuite, sur l'atelier les deux fautes
étaient présentes en même temps et seul `217/USER` est remonté : systemd
s'arrête à la première étape qui échoue. Corriger une cause peut donc en
révéler une autre, il faut relire le statut après chaque correction.

Autre détail à connaître pour ne pas s'égarer : dans ces lignes, l'émetteur
n'est pas `systemd[1]` mais `(etriques)[3957]`. C'est le processus enfant que
systemd vient de forker, dont le nom est tronqué. Ce n'est pas un autre
programme.

### Deux outils qui font gagner du temps

**`systemctl show -p <propriété>` interroge l'état effectif**, pas le fichier
sur disque. La différence est loin d'être théorique : un fragment déposé dans
`/etc/systemd/system/<unité>.service.d/` change le comportement sans modifier
le fichier principal. Sur l'atelier, le fichier principal contient
`RestartSec=2s` et pourtant :

```bash
systemctl show releve-metriques.service -p Restart -p RestartUSec -p FragmentPath -p DropInPaths
```

```text
Restart=always
RestartUSec=1s
FragmentPath=/etc/systemd/system/releve-metriques.service
DropInPaths=/etc/systemd/system/releve-metriques.service.d/10-atelier.conf
```

Deux pièges dans cette sortie : la propriété interrogée ne porte pas toujours
le nom de la directive (`RestartSec=` dans le fichier devient `RestartUSec=`
dans `show`), et `DropInPaths` est la seule façon rapide de savoir qu'un
override existe. `systemctl cat <unité>` affiche les fragments à la suite,
`show` donne le résultat de leur fusion. L'option `--value` ne renvoie que la
valeur, ce qui rend l'appel scriptable :

```bash
for p in ActiveState SubState ExecMainStatus NRestarts; do
    printf "%-15s %s\n" "$p" "$(systemctl show releve-metriques.service -p "$p" --value)"
done
```

```text
ActiveState     failed
SubState        failed
ExecMainStatus  78
NRestarts       5
```

**`journalctl -u <unité> -b --no-pager -o short-precise` horodate à la
milliseconde**, ce qui rend la cadence de la boucle visible :

```text
15:47:15.696923 releve-metriques[1343]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
15:47:16.957531 releve-metriques[1345]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
15:47:18.208049 systemd[1]: releve-metriques.service: Scheduled restart job, restart counter is at 5.
15:47:18.208454 systemd[1]: releve-metriques.service: Start request repeated too quickly.
15:47:18.208506 systemd[1]: Failed to start releve-metriques.service - Releve de metriques (atelier).
```

Un cycle toutes les 1,25 seconde environ, et surtout une fin. Par défaut,
systemd tolère `StartLimitBurst=5` démarrages par tranche de
`StartLimitIntervalSec=10s` ; au delà, il abandonne, le dit explicitement
(`Start request repeated too quickly`) et bascule l'unité en `failed`. Un
service qui n'est plus en boucle n'est donc pas forcément réparé : il peut
simplement avoir renoncé. Vérifiez toujours `NRestarts` et l'état réel.

> **Une boucle trop lente n'atteint jamais la limite.** Avec le
> `RestartSec=2s` du fichier d'origine, l'atelier a compté 21 redémarrages
> sans jamais déclencher le garde-fou : un cycle de 2,25 seconde tient tout
> juste dans les 10 secondes de la fenêtre. Le service tourne alors en rond
> indéfiniment, sans jamais passer `failed`, et n'apparaît pas dans
> `systemctl list-units --failed`.

### `active` n'est pas `enabled` : la preuve par le redémarrage

Une correction n'est finie que si elle survit au redémarrage. Après avoir posé
la configuration attendue, le service repart :

```bash
systemctl is-active releve-metriques.service   # active
systemctl is-enabled releve-metriques.service  # disabled
```

Les deux réponses coexistent sans contradiction : `is-active` décrit
maintenant, `is-enabled` décrit le prochain démarrage. La ligne `Loaded:` de
`systemctl status` le dit d'ailleurs déjà, entre parenthèses après le chemin de
l'unité. Un `systemctl reboot` tranche :

```text
$ systemctl is-active releve-metriques.service
inactive
$ systemctl is-enabled releve-metriques.service
disabled
```

Le service réparé la veille est mort au réveil. `enable` crée le lien
symbolique qui manque, dans le répertoire désigné par la section `[Install]` de
l'unité :

```bash
sudo systemctl enable --now releve-metriques.service
```

```text
Created symlink '/etc/systemd/system/multi-user.target.wants/releve-metriques.service' → '/etc/systemd/system/releve-metriques.service'.
```

Second redémarrage, même vérification :

```text
$ systemctl is-active releve-metriques.service
active
$ systemctl is-enabled releve-metriques.service
enabled
```

`enable --now` combine `enable` et `start`. Notez enfin que `is-active` et
`is-enabled` renvoient aussi un code de retour exploitable en script : `0`
quand la réponse est positive, `3` pour `inactive` et `1` pour `disabled`.

### Dépannage

| Ce que vous voyez | Ce qu'il faut regarder |
|---|---|
| `Active: activating (auto-restart)` | la boucle est en cours, remontez au premier message du journal |
| `status=203/EXEC` + `No such file or directory` | le chemin d'`ExecStart=` est faux |
| `status=203/EXEC` + `Permission denied` | le bit d'exécution manque sur le binaire |
| `status=200/CHDIR` | `WorkingDirectory=` désigne un répertoire absent |
| `status=217/USER` | le `User=` de l'unité n'existe pas sur la machine |
| code inférieur à 125 | le programme s'est arrêté lui-même, lisez ses propres lignes de journal |
| `Start request repeated too quickly` | la limite de démarrages est atteinte, le service a renoncé |
| Le journal ne montre rien avant le reboot | journal volatil, `/var/log/journal` est absent |
| L'unité modifiée ne change rien | `daemon-reload` oublié, ou un drop-in l'emporte (`systemctl show -p DropInPaths`) |

Pour retirer un service de démonstration et repartir d'une machine propre :

```bash
sudo systemctl disable --now <unité>
sudo rm -f /etc/systemd/system/<unité>.service
sudo rm -rf /etc/systemd/system/<unité>.service.d
sudo systemctl daemon-reload
sudo systemctl reset-failed
systemctl list-units --failed        # doit lister 0 unité
```

`reset-failed` efface l'état `failed` et remet le compteur de redémarrages à
zéro. Sans lui, une unité corrigée peut rester affichée en échec.
