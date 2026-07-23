# Lab — limites de ressources par utilisateur

## Rappel

[**Limites de ressources sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/)

`ulimit` montre et règle les limites du shell courant ; la politique durable est
dans `/etc/security/limits.conf` et `/etc/security/limits.d/*.conf`, une règle
par ligne `<domaine> <type> <item> <valeur>`. `pam_limits` les applique à
l'ouverture de session. La limite **souple** est celle qui s'applique, la limite
**dure** est le plafond que l'utilisateur ne peut pas franchir.

## Le cours

Les exemples ci-dessous portent sur l'utilisateur `nodeops`, sur l'item `nproc`
et sur des unités systemd de démonstration : le challenge, lui, vous demandera
un autre compte, un autre item et d'autres valeurs. Le but est d'apprendre la
méthode et de savoir prouver le résultat, pas de recopier une ligne. Toutes les
sorties viennent d'une AlmaLinux 10.

### Souple, stricte, et qui dit la vérité

Chaque limite existe en deux valeurs : la **souple**, réellement appliquée et
que l'utilisateur peut relever jusqu'à la **dure**, plafond absolu qu'il ne peut
pas dépasser sans privilège. `ulimit -a` liste tout, `-S` et `-H` ciblent l'une
ou l'autre, `-n` désigne `nofile` (fichiers ouverts) et `-u` désigne `nproc`
(processus par utilisateur) :

```bash
ulimit -Sn ; ulimit -Hn     # 1024 puis 524288
ulimit -Su ; ulimit -Hu     # 3351 puis 3351
```

Ces valeurs sont celles de **votre session**. Pour un processus déjà lancé, la
seule source de vérité est le noyau, exposé dans `/proc/<pid>/limits`, que
`prlimit` sait lire proprement :

```bash
sudo prlimit --pid 1 --nofile
sudo grep -E "Max processes|Max open files" /proc/1/limits
```

```text
RESOURCE DESCRIPTION                    SOFT       HARD UNITS
NOFILE   max number of open files 1073741816 1073741816 files
Max processes             3351                 3351                 processes
Max open files            1073741816           1073741816           files
```

Retenez l'écart : votre shell est à 1024 fichiers ouverts, `systemd` (PID 1) est
à plus d'un milliard. Deux processus de la même machine n'ont pas les mêmes
plafonds, parce qu'ils ne les tiennent pas de la même source.

### Une limite durable par utilisateur : limits.d et pam_limits

Une valeur posée avec `ulimit` meurt avec le terminal. Pour qu'elle survive aux
reconnexions, on la déclare dans un fichier dédié sous `/etc/security/limits.d/`,
que le module `pam_limits` applique à l'ouverture de session. Quatre champs par
ligne : le domaine (un utilisateur, un groupe avec `@`, `*` pour tous), le type
(`soft` ou `hard`), l'item et la valeur.

```bash
sudo useradd -m nodeops
sudo tee /etc/security/limits.d/70-nodeops.conf <<'EOF'
nodeops  soft  nproc  30
nodeops  hard  nproc  60
EOF
sudo runuser -l nodeops -c 'ulimit -Su; ulimit -Hu'
```

```text
30
60
```

`runuser -l` (comme `su -`) ouvre une **vraie session** : c'est là que
`pam_limits` intervient. Sur cette AlmaLinux 10, `/etc/pam.d/su` et
`/etc/pam.d/sudo` incluent tous deux `system-auth`, qui charge `pam_limits.so` :
un `sudo -u nodeops bash -c 'ulimit -Su'` renvoie donc lui aussi `30`. Ne
comptez pas sur ce détail, il dépend de la pile PAM de la distribution ; testez
toujours dans une session de login, c'est le seul cas garanti.

En revanche, ce qui ne change jamais, c'est qu'un **processus déjà lancé garde
les limites qu'il avait au démarrage**. Modifions le fichier pendant qu'un
processus tourne :

```bash
sudo sed -i 's/nproc  30/nproc  45/' /etc/security/limits.d/70-nodeops.conf
sudo grep 'Max processes' /proc/$(pgrep -u nodeops -x sleep | head -1)/limits
sudo runuser -l nodeops -c 'ulimit -Su'
```

```text
Max processes             30                   60                   processes
45
```

Le processus vivant est resté à 30, la nouvelle session voit 45. C'est
exactement le motif du « j'ai pourtant changé le fichier » : il fallait
rouvrir une session.

Une limite qu'on n'a jamais vue mordre n'apprend rien. `nproc` vaut maintenant
45 pour `nodeops` : demandons lui 60 processus.

```bash
sudo runuser -l nodeops -c 'for i in $(seq 1 60); do sleep 20 & done; wait'
```

```text
-bash: fork: retry: Resource temporarily unavailable
[...]
-bash: fork: Resource temporarily unavailable
```

Le shell n'a pas planté, la machine non plus : le noyau a simplement refusé les
`fork()` au delà du plafond. C'est tout l'intérêt d'une limite, transformer un
effondrement global en refus local. Nettoyez ensuite avec
`sudo pkill -u nodeops sleep`.

### Trois familles de contraintes qu'on confond

Sur un service, « limiter » recouvre trois mécanismes différents, avec trois
symptômes différents quand ils mordent. Les mélanger, c'est chercher une panne
au mauvais endroit.

| Famille | Directives d'unité | Mécanisme | Symptôme du dépassement |
|---|---|---|---|
| Ressources par cgroup | `MemoryMax`, `CPUQuota`, `TasksMax` | cgroup v2, appliqué par le noyau au groupe | processus tué (`oom-kill`), ralenti, ou `fork` refusé |
| Limites héritées d'ulimit | `LimitNOFILE`, `LimitNPROC` | `rlimit` posée sur le processus au démarrage | appel système en erreur : `Too many open files` |
| Durcissement d'accès | `ProtectSystem`, `PrivateTmp`, `ReadOnlyPaths`, `NoNewPrivileges` | espaces de noms et montages dédiés | `Read-only file system`, fichier introuvable |

Point commun : aucune des trois ne lit `/etc/security/limits.conf`. Un service
lancé par systemd ne passe pas par la pile PAM, donc il ignore totalement
`limits.d`. Vérifions-le sur une unité qui tourne sous `nodeops` sans aucune
directive :

```bash
sudo tee /etc/systemd/system/atelier-fd.service <<'EOF'
[Unit]
Description=Atelier - service sans directive Limit*
[Service]
Type=simple
User=nodeops
ExecStart=/bin/sleep 600
EOF
sudo systemctl daemon-reload && sudo systemctl start atelier-fd.service
sudo grep 'Max processes' /proc/$(systemctl show -p MainPID --value atelier-fd.service)/limits
systemctl show --property=DefaultLimitNPROC
```

```text
Max processes             3351                 3351                 processes
DefaultLimitNPROC=3351
```

Le service tourne bien sous `nodeops`, et pourtant il est à 3351, pas à 45 : il
a hérité du **défaut du gestionnaire**, pas de `limits.d`. C'est l'erreur la
plus fréquente sur ce sujet.

### La famille ulimit dans une unité : LimitNOFILE

Pour un service, la limite se pose donc dans l'unité. Serrons volontairement le
plafond de fichiers ouverts pour le voir céder, avec un script qui ouvre des
fichiers jusqu'à l'échec et sort en code 24 :

```ini
[Service]
Type=oneshot
User=nodeops
LimitNOFILE=64
ExecStart=/usr/local/bin/atelier-ouvre-fd
```

```bash
sudo systemctl daemon-reload && sudo systemctl start atelier-fd.service
sudo journalctl -u atelier-fd.service -n 4 --no-pager -o short
```

```text
Job for atelier-fd.service failed because the control process exited with error code.
[...] atelier-ouvre-fd[23651]: stoppe apres 61 fichiers : [Errno 24] Too many open files: '/etc/hostname'
[...] systemd[1]: atelier-fd.service: Main process exited, code=exited, status=24/n/a
[...] systemd[1]: atelier-fd.service: Failed with result 'exit-code'.
```

Trois informations à lire : le message applicatif (`Too many open files`), le
**code de sortie** conservé par systemd (`status=24`), et le résultat
(`exit-code`). Le compte s'arrête à 61 et non 64, parce que l'entrée, la sortie
et l'erreur standard occupent déjà trois descripteurs.

Attention à la lecture des propriétés : `systemctl show` distingue la dure de la
souple. Ici `systemctl show -p LimitNOFILE -p LimitNOFILESoft atelier-fd.service`
répond `LimitNOFILE=64` et `LimitNOFILESoft=64`, alors que sans directive la même
paire donnait `524288` et `1024` : c'est le classique « soft 1024 » que voient
les serveurs bridés.

### La famille cgroup : MemoryMax, et ce que le noyau a vraiment retenu

`MemoryMax` plafonne la mémoire du **groupe de contrôle** de l'unité. Un
service de démonstration qui alloue 8 Mio toutes les 200 ms, sous 48 Mio :

```ini
[Service]
Type=simple
MemoryMax=48M
ExecStart=/usr/local/bin/atelier-mange-ram 0
```

Tant qu'il reste sous le plafond, l'arborescence cgroup montre la contrainte
acceptée et la consommation en cours :

```bash
sudo cat /sys/fs/cgroup/system.slice/atelier-ram.service/memory.max
systemctl show -p MemoryMax -p MemoryCurrent atelier-ram.service
systemd-cgls /system.slice/atelier-ram.service --no-pager
```

```text
50331648
MemoryCurrent=28487680
MemoryMax=50331648
CGroup /system.slice/atelier-ram.service:
└─23843 /usr/bin/python3 /usr/local/bin/atelier-mange-ram 24
```

`48M` s'écrit `50331648` octets côté noyau : la valeur affichée par
`systemctl show` est celle qui a réellement été posée dans le cgroup, pas le
texte de l'unité. Laissez maintenant le service dépasser :

```bash
systemctl status atelier-ram.service --no-pager
```

```text
Active: failed (Result: oom-kill) since Wed 2026-07-22 15:48:59 UTC; 2s ago
Process: 23969 ExecStart=/usr/local/bin/atelier-mange-ram 0 (code=killed, signal=KILL)
Mem peak: 48M
[...] systemd[1]: atelier-ram.service: A process of this unit has been killed by the OOM killer.
[...] systemd[1]: atelier-ram.service: Main process exited, code=killed, status=9/KILL
```

Le symptôme n'a rien à voir avec celui de `LimitNOFILE` : pas de code d'erreur
applicatif, un `SIGKILL` et un résultat `oom-kill`. Le tueur est celui du
**cgroup** : seul le service est mort, la machine n'a pas bronché. Les deux
autres directives de la famille se vérifient de la même façon :

```bash
systemctl show -p CPUQuotaPerSecUSec -p TasksMax atelier-cpu.service   # CPUQuota=20% TasksMax=25
sudo cat /sys/fs/cgroup/system.slice/atelier-cpu.service/cpu.max /sys/fs/cgroup/system.slice/atelier-cpu.service/pids.max
```

```text
CPUQuotaPerSecUSec=200ms
TasksMax=25
20000 100000
25
```

`systemd-cgtop --depth=2 -b -n 1 --order=memory` classe les cgroups par
consommation, pratique pour trouver qui pèse avant de poser un plafond.

### Le durcissement d'accès : PrivateTmp et ProtectSystem

Troisième famille : elle ne compte rien, elle **cache ou verrouille**.
`PrivateTmp=yes` donne au service un `/tmp` bien à lui. Faisons-lui y écrire un
fichier :

```ini
[Service]
Type=oneshot
PrivateTmp=yes
ExecStart=/bin/sh -c "echo trace-du-service > /tmp/marqueur-atelier.txt; ls -l /tmp"
```

```text
# vu par le service, dans le journal
-rw-r--r--. 1 root root 17 Jul 22 15:49 marqueur-atelier.txt

# vu du système, au même instant
$ ls -l /tmp/marqueur-atelier.txt
ls: cannot access '/tmp/marqueur-atelier.txt': No such file or directory
```

Le fichier existe, mais dans un montage privé dont le nom trahit l'unité :

```bash
sudo sh -c 'cat /tmp/systemd-private-*-atelier-tmp.service-*/tmp/marqueur-atelier.txt'
```

```text
trace-du-service
```

C'est ce qui déroute quand on cherche un fichier qu'un service prétend avoir
écrit. `ProtectSystem=strict`, lui, remonte tout le système de fichiers en
lecture seule sauf les chemins listés en `ReadWritePaths` :

```ini
[Service]
ProtectSystem=strict
ReadWritePaths=/var/log
ExecStart=/bin/sh -c "echo essai > /etc/atelier-marqueur.conf"
```

```text
sh[24181]: /bin/sh: line 1: /etc/atelier-marqueur.conf: Read-only file system
systemd[1]: atelier-lecture.service: Main process exited, code=exited, status=1/FAILURE
```

Le service tourne pourtant en `root` : le durcissement ne dépend pas de l'UID,
il agit plus bas. Le fichier n'existe nulle part après coup.

### Vérifier et dépanner

Une directive **écrite** n'est pas une directive **active**. Une clé mal
orthographiée est ignorée en silence dans le fichier, et systemd garde son
défaut :

```bash
sudo systemd-analyze verify /etc/systemd/system/atelier-typo.service
systemctl show -p MemoryMax atelier-typo.service
```

```text
/etc/systemd/system/atelier-typo.service:6: Unknown key 'MemoryMaximum' in section [Service], ignoring.
MemoryMax=infinity
```

Le réflexe est toujours le même : comparer le **configuré** au **réellement
appliqué**.

| Symptôme | Cause probable | Où regarder |
|---|---|---|
| Un service reste au défaut malgré `limits.d` | Les services ne passent pas par `pam_limits` | Poser `Limit*` dans l'unité, `daemon-reload`, redémarrer |
| Une nouvelle limite n'est pas prise en compte | Session ou processus ouverts avant le changement | Rouvrir une session ; `/proc/<pid>/limits` pour le processus vivant |
| Un compte ne peut pas relever sa limite | Il vise au dessus de sa limite dure | Relever la valeur `hard` (nécessite root) |
| La directive semble sans effet | Clé inconnue, ignorée au chargement | `systemd-analyze verify`, puis `systemctl show -p <propriété>` |

Trois commandes suffisent à trancher : `systemctl show -p <propriété> <unité>`
pour la valeur retenue par systemd, `/sys/fs/cgroup/system.slice/<unité>/` pour
ce que le noyau a inscrit, et `/proc/<pid>/limits` pour ce que subit le
processus. Enfin, quand un service de démonstration est en `failed`, il reste
listé par `systemctl list-units --failed` jusqu'à un `systemctl reset-failed` :
supprimer l'unité et faire `daemon-reload` ne suffit pas à effacer la trace.
