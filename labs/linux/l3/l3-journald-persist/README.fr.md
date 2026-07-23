# Lab — journald persistant

## Rappel

[**Journaux systemd sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/)

`systemd-journald` écrit soit dans `/run/log/journal` (en mémoire, perdu au
redémarrage), soit sous `/var/log/journal` (sur disque). Le régime dépend de la
directive `Storage=` de la configuration de journald **et** de l'existence du
répertoire de destination. `journalctl --list-boots` et `journalctl -b -1`
disent immédiatement dans lequel des deux vous êtes : sans journal persistant,
la machine ne connaît qu'un seul démarrage, le sien.

## Le cours

Les mesures ci-dessous ont été faites sur une machine d'atelier AlmaLinux 10.2
(systemd 257), avec un drop-in nommé `99-atelier.conf` et des tailles choisies
pour la démonstration (64 Mio, 16 Mio, 1 semaine). Le challenge vous demandera
un autre réglage : l'objectif ici est de comprendre **ce qui déclenche quoi**,
pas de recopier une ligne.

### Où journald écrit, et comment le lire

Quelques commandes suffisent à établir le régime en cours : les emplacements,
l'espace occupé, l'historique connu.

```bash
ls -ld /run/log/journal /var/log/journal
journalctl --disk-usage
journalctl --list-boots
journalctl -b -1
```

```text
drwxr-sr-x+ 3 root systemd-journal 60 Jul 22 13:29 /run/log/journal
ls: cannot access '/var/log/journal': No such file or directory
Archived and active journals take up 12M in the file system.
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
  0 8bad63d36f3c4974a4d73a72649a4d20 Wed 2026-07-22 13:29:55 UTC Wed 2026-07-22 15:30:58 UTC
Specifying boot ID or boot offset has no effect, no persistent journal was found.
```

Un seul démarrage listé, et une demande de démarrage précédent qui échoue avec
un diagnostic sans ambiguïté. journald, lui, annonce son choix à chaque
démarrage : c'est la ligne la plus utile de tout le lab.

```bash
journalctl -u systemd-journald | tail -2
```

```text
systemd-journald[2085]: Journal started
systemd-journald[2085]: Runtime Journal (/run/log/journal/0848e893...) is 2.3M, max 18.9M, 16.6M free.
```

`Runtime Journal` veut dire mémoire, `System Journal` veut dire disque. Aucune
autre commande ne donne l'information aussi directement.

### La preuve par le redémarrage

Le reste du cours ne vaut que si l'on a vu la perte se produire. On dépose un
repère, on redémarre, on le cherche :

```bash
logger -t atelier "REPERE-AVANT-REBOOT"     # Jul 22 15:30:58 atelier[22856]: REPERE-AVANT-REBOOT
sudo systemctl reboot
```

Après le redémarrage, sur cette machine au journal volatil :

```text
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
  0 23936a39b031438a85852d0580cb2752 Wed 2026-07-22 15:31:07 UTC Wed 2026-07-22 15:31:18 UTC
```

```bash
journalctl -t atelier      # -- No entries --
journalctl --disk-usage    # Archived and active journals take up 3M in the file system.
```

Le repère a disparu, l'identifiant de démarrage a changé, l'occupation est
retombée. C'est la situation d'un serveur qui redémarre seul la nuit : au matin,
la cause n'existe plus.

### Ce qui déclenche la persistance : trois valeurs et un répertoire

Sur AlmaLinux 10, **`/etc/systemd/journald.conf` n'existe pas** : le fichier
livré par le paquet est en `/usr/lib/systemd/journald.conf` et ne contient que
des valeurs commentées, qui documentent les défauts.

```bash
ls /etc/systemd/journald.conf
grep -E '^#(Storage|SystemMaxUse|SystemKeepFree)' /usr/lib/systemd/journald.conf
```

```text
ls: cannot access '/etc/systemd/journald.conf': No such file or directory
#Storage=auto
#SystemMaxUse=
#SystemKeepFree=
```

On ne modifie donc pas un fichier existant : on ajoute un drop-in sous
`/etc/systemd/journald.conf.d/`, qui se superpose au fichier livré. Le tableau
suivant résume ce que chaque valeur de `Storage=` produit, mesuré sur la
machine :

| `Storage=` | Comportement observé |
|---|---|
| `volatile` | `Runtime Journal (/run/...)`, **même si `/var/log/journal` existe et contient des fichiers** |
| `auto` (défaut) | disque **si et seulement si** `/var/log/journal` existe ; journald ne le crée jamais |
| `persistent` | journald crée `/var/log/journal` lui-même à la vidange (pas au simple redémarrage du service), mais avec des droits qui ne sont pas ceux de la distribution (voir plus bas) |

Première conséquence : sous le défaut `auto`, créer le répertoire suffit,
aucune directive n'est nécessaire. Seconde conséquence, sur la commande que tout
le monde recopie :

```bash
sudo systemd-tmpfiles --create --prefix /var/log/journal
echo "rc=$?" ; ls -ld /var/log/journal
```

```text
rc=0
ls: cannot access '/var/log/journal': No such file or directory
```

**`systemd-tmpfiles` ne crée pas ce répertoire.** Elle sort en succès et ne fait
rien, parce que la règle qui le concerne est un `z` (ajuster) et non un `d`
(créer) :

```bash
grep 'var/log/journal' /usr/lib/tmpfiles.d/systemd.conf
```

```text
z /var/log/journal 2755 root systemd-journal - -
a+ /var/log/journal - - - - d:group:adm:r-x,d:group:wheel:r-x,group:adm:r-x,group:wheel:r-x
```

Son rôle est de **corriger** les droits d'un répertoire déjà là, pas de le
fabriquer. Un `mkdir` ordinaire, lui, ne donne pas les bons attributs :

```bash
sudo mkdir -p /var/log/journal && ls -ld /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal && ls -ld /var/log/journal
```

```text
drwxr-xr-x. 2 root root            6 Jul 22 15:31 /var/log/journal
drwxr-sr-x+ 2 root systemd-journal 6 Jul 22 15:31 /var/log/journal
```

Trois changements en une commande : le groupe passe à `systemd-journal`, le bit
**set-GID** apparaît (le `s` du groupe, mode `2755`, pour que tout ce qui est
créé dedans hérite du groupe), et le `+` final signale des ACL, celles qui
ouvrent la lecture aux groupes `adm` et `wheel`.

Ce n'est pas cosmétique. Un utilisateur qui n'appartient à aucun de ces groupes
se le voit dire par `journalctl` :

```text
Users in groups 'adm', 'systemd-journal', 'wheel' can see all messages.
No journal files were opened due to insufficient permissions.
```

Quand c'est journald qui crée le répertoire tout seul, le résultat est moins
bon : `drwxr-xr-x. 3 root root` et des fichiers `-rw-r----- root root`. Ni
set-GID, ni groupe `systemd-journal`, ni ACL. Le réflexe est donc de passer
`systemd-tmpfiles --create` après coup, quelle que soit la manière dont le
répertoire est apparu, et de vérifier avec `ls -ld` que le `s` et le `+` sont
là.

Reste la mesure la plus contre-intuitive du lab. Répertoire créé, droits
corrigés, service redémarré :

```bash
sudo systemctl restart systemd-journald
sudo find /var/log/journal -type f | wc -l
journalctl -u systemd-journald -n 1
```

```text
0
systemd-journald[2085]: Runtime Journal (/run/log/journal/0848e893...) is 2.3M, max 18.9M, 16.6M free.
```

Zéro fichier, et journald écrit toujours en mémoire. Ce qui déclenche la
bascule, c'est la demande explicite de vidange :

```text
# sudo journalctl --flush
systemd-journald[2085]: Received client request to flush runtime journal.
systemd-journald[2085]: Time spent on flushing to /var/log/journal/0848e893... is 3.327ms for 56 entries.
systemd-journald[2085]: System Journal (/var/log/journal/0848e893...) is 8M, max 894.9M, 886.8M free.
```

`Runtime Journal` est devenu `System Journal` : la bascule a eu lieu. Au
démarrage suivant, cette vidange sera automatique, c'est le rôle de l'unité
`systemd-journal-flush.service`, une fois `/var` monté. Elle n'est manuelle que
lorsqu'on active la persistance sur une machine déjà démarrée.

Le résultat, après un second redémarrage, se lit enfin comme espéré : deux
démarrages listés, et le repère du précédent toujours là.

```text
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
 -1 23936a39b031438a85852d0580cb2752 Wed 2026-07-22 15:31:07 UTC Wed 2026-07-22 15:32:05 UTC
  0 a6570b953d054a07a38240da3092b148 Wed 2026-07-22 15:32:08 UTC Wed 2026-07-22 15:32:17 UTC
# journalctl -b -1 -t atelier
Jul 22 15:32:03 atelier atelier[1376]: REPERE-AVANT-REBOOT-2
```

Un détail utile en dépannage : `journalctl` **lit** les deux emplacements. Après
un passage en `Storage=volatile`, les anciens fichiers de `/var/log/journal`
restent lisibles et continuent d'apparaître dans `--list-boots`, alors que
journald n'y écrit plus. Ne concluez donc pas du seul `--list-boots` que la
persistance est active : lisez la ligne `Journal started` du service.

### Les limites de taille, la partie qu'on saute

Un journal persistant sans limite est un incident de production en attente. Les
directives se lisent mal si l'on ne sait pas ce que « System » désigne. Le
manuel (`man journald.conf`) est explicite :

> Les options préfixées par `System` s'appliquent aux fichiers journaux stockés
> sur un système de fichiers persistant, plus précisément `/var/log/journal`.
> Celles préfixées par `Runtime` s'appliquent au stockage en mémoire,
> `/run/log/journal`.

Il ne s'agit donc pas des services système par opposition aux services
utilisateur : `SystemMaxUse` plafonne bien le journal d'un utilisateur, dès lors
qu'il est écrit sur disque.

Sans réglage, journald affiche à son démarrage un plafond calculé : **10 % du
système de fichiers**, soit ici 894,9 Mio pour une racine de 8,8 Gio. Un drop-in
suffit à le changer :

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nSystemMaxUse=64M\nSystemMaxFileSize=16M\nSystemKeepFree=1G\nMaxRetentionSec=1week\n' \
  | sudo tee /etc/systemd/journald.conf.d/99-atelier.conf
sudo systemctl restart systemd-journald
journalctl -u systemd-journald -n 1
# System Journal (/var/log/journal/0848e893...) is 16M, max 64M, 48M free.
```

| Directive | Ce qu'elle borne |
|---|---|
| `SystemMaxUse` | la taille totale de tous les fichiers journaux sur disque |
| `SystemKeepFree` | l'espace libre que journald s'interdit d'entamer sur le système de fichiers |
| `SystemMaxFileSize` | la taille d'un fichier avant rotation, donc la granularité de la purge |
| `MaxRetentionSec` | l'âge au-delà duquel un fichier archivé est supprimé |

Le piège est `SystemKeepFree`, parce que le plafond réellement appliqué est le
**plus contraignant des deux**. Sur cette machine de 8,8 Gio dont 7,7 Gio sont
libres, en portant `SystemKeepFree` à `7880M` :

```text
System Journal (/var/log/journal/0848e893...) is 16M, max 16M, 0B free.
```

`SystemMaxUse=64M` est resté écrit, mais le plafond effectif est tombé à 16 Mio
et il ne reste plus rien à écrire. Une valeur mal calibrée ici ne remplit pas le
disque : elle fait disparaître silencieusement l'historique que l'on croyait
garder. D'où le réflexe de relire la ligne `System Journal` après chaque
modification, plutôt que de faire confiance au fichier.

La purge manuelle, elle, agit tout de suite :

```bash
journalctl --disk-usage          # Archived and active journals take up 40.1M
sudo journalctl --vacuum-size=24M
```

```text
Deleted archived journal /var/log/journal/0848e893.../system@cfb8915f...journal (3.7M).
Deleted archived journal /var/log/journal/0848e893.../user-1001@cfb8915f...journal (8.2M).
[...]
Vacuuming done, freed 24.1M of archived journals from /var/log/journal/0848e893...
# journalctl --disk-usage : Archived and active journals take up 16M
```

Deux limites à connaître. `--vacuum-size` et `--vacuum-time` ne suppriment que
les fichiers **archivés** : les fichiers actifs ne sont jamais touchés, ce qui
explique qu'on n'atteigne pas toujours la cible demandée. Pour aller plus loin,
il faut d'abord forcer une rotation avec `sudo journalctl --rotate`. Et surtout,
une purge trop large détruit précisément ce que la persistance servait à
conserver : après un `--rotate` suivi d'un `--vacuum-size=8M`, `--list-boots` ne
connaissait plus qu'un seul démarrage, comme au premier jour.

### Vérifier sa configuration, avant et après

Il n'existe **pas** de validation préalable. `systemd-analyze cat-config
systemd/journald.conf` ne fait qu'assembler les fichiers : elle affiche sans
broncher une directive inventée (`Compresss=yes`) et sort en code 0. Le
rechargement à chaud n'est pas non plus une option :

```bash
sudo systemctl reload systemd-journald
# Failed to reload systemd-journald.service: Job type reload is not applicable for unit systemd-journald.service.
```

La seule vérification réelle a donc lieu **au redémarrage du service**, et elle
n'apparaît que dans le journal. Le service démarre quand même, `systemctl
restart` renvoie 0, et rien ne s'affiche sur le terminal :

```bash
sudo systemctl restart systemd-journald && journalctl -u systemd-journald -n 5
```

```text
systemd-journald[2021]: .../99-atelier.conf:4: Unknown key 'Compresss' in section [Journal], ignoring.
systemd-journald[1252]: .../99-atelier.conf:2: Failed to parse Storage=persistant, ignoring: Invalid argument
```

Le premier message signale une clé inconnue, le second une valeur invalide sur
une clé correcte. Dans les deux cas la ligne est **ignorée** et le défaut
s'applique. Une faute de frappe ne se voit donc pas : elle se traduit par un
réglage qui n'a jamais pris effet. Le contrôle à faire systématiquement après un
redémarrage du service est donc la paire message d'erreur / ligne
`Journal started` qui suit.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `no persistent journal was found` sur `journalctl -b -1` | journal en mémoire, le répertoire sur disque n'existe pas |
| `/var/log/journal` créé, mais journald dit toujours `Runtime Journal` | la vidange n'a pas été demandée, ou `Storage=volatile` la bloque |
| Répertoire créé, aucun fichier dedans après redémarrage du service | `restart` ne bascule pas, il faut `journalctl --flush` |
| `systemd-tmpfiles --create` sort en 0 et ne crée rien | la règle est un `z` (ajuster), le répertoire doit préexister |
| `No journal files were opened due to insufficient permissions` | utilisateur absent de `adm`, `systemd-journal` et `wheel` |
| Pas de `s` ni de `+` sur `ls -ld /var/log/journal` | répertoire créé à la main ou par journald, repasser `systemd-tmpfiles --create` |
| Directive sans effet, aucune erreur visible | clé ou valeur ignorée, lire `journalctl -u systemd-journald` après le redémarrage |
| Plafond bien plus bas que `SystemMaxUse` | `SystemKeepFree` est plus contraignant, lire la ligne `System Journal` |
| `--vacuum-size` n'atteint pas la cible | seuls les fichiers archivés sont purgés, faire `journalctl --rotate` d'abord |
| `--list-boots` montre un historique alors que le journal est volatil | `journalctl` lit aussi les anciens fichiers de `/var/log/journal` |

Pour revenir à l'état volatil et repartir de zéro :

```bash
sudo rm -rf /etc/systemd/journald.conf.d /var/log/journal
sudo systemctl restart systemd-journald
journalctl -u systemd-journald -n 1   # doit redire "Runtime Journal"
```
