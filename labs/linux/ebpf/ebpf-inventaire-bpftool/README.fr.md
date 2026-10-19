# Lab : inventorier les programmes eBPF chargés et retrouver ce qui les porte

## Rappel

[**La surface d'attaque d'eBPF sur le guide compagnon**](https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/surface-attaque-bpf/)

eBPF permet de charger de petits programmes dans le noyau Linux. Ils s'y
exécutent avec des droits étendus, ce qui en fait un outil précieux pour
l'observabilité et un lieu de choix pour se cacher. La bonne nouvelle est que
**tout programme chargé se voit** : la commande `bpftool` en dresse la liste, quel
que soit l'outil qui l'a posé. Ce lab apprend les quatre gestes d'un inventaire :
**lister** les programmes, **retrouver le processus** qui tient l'un d'eux,
**remonter à l'unité systemd** qui lance ce processus, puis **arrêter** cette
unité pour qu'elle ne revienne pas. Le piège classique n'est pas de trouver le
programme, c'est de croire qu'il est parti parce qu'on a tué son processus.

## Le cours

Les exemples ci-dessous utilisent des sondes et des services de démonstration
(`demo-sonde`, `demo-horloge`, `demo-veilleur`) que vous créez puis supprimez
vous-même : le challenge pose un problème différent, à vous de transférer ce que
vous aurez vu. Les sorties reproduites ici ont été obtenues sur AlmaLinux 10.2
(noyau 6.12, `bpftool` 7.7) et sur Ubuntu 24.04 (noyau 6.8, `bpftool` 7.4), sur
une machine fraîche. Sur la machine du lab, la liste du premier exemple comptera
une ligne de plus que ci-dessous : c'est ce que le challenge vous demande
d'élucider, n'y touchez pas avant d'avoir fini le cours. Les numéros de
programme et de processus changent à chaque essai.

Les deux outils sont déjà installés par la préparation du lab. Pour le vérifier,
et connaître la version qui répond :

```bash
command -v bpftool bpftrace
sudo bpftool version
```

```text
/usr/sbin/bpftool
/usr/bin/bpftrace
bpftool v7.7.0
using libbpf v1.7
features: llvm, skeletons
```

La sortie vient d'AlmaLinux ; Ubuntu 24.04 rend `bpftool v7.4.0` et `libbpf
v1.4`. Lister les programmes demande les droits root, d'où le `sudo` partout
dans ce lab.

### Lister les programmes chargés : `bpftool prog show`

Le noyau tient un registre de tous les programmes eBPF qu'il porte, et
`bpftool prog show` l'affiche. Chaque programme occupe un bloc : une première
ligne d'identité, puis des lignes de détail en retrait. La commande suivante ne
garde que les premières lignes et compte les programmes **par type**, le
deuxième champ :

```bash
sudo bpftool prog show | grep -E '^[0-9]+:' | awk '{print $2}' | sort | uniq -c | sort -rn
```

```text
     12 cgroup_skb
      7 cgroup_device
      1 socket_filter
      1 lsm
```

Voici ce que rend Ubuntu 24.04 :

```text
      6 cgroup_skb
      6 cgroup_device
      1 tracing
```

Le **type** d'un programme dit à quel endroit du noyau il est accroché et ce
qu'il a le droit de faire : `cgroup_skb` filtre les paquets réseau d'un groupe de
processus, `cgroup_device` contrôle l'accès aux périphériques, `lsm` s'insère
dans les décisions de sécurité, `kprobe` s'accroche à une fonction du noyau,
`perf_event` se déclenche sur un événement de performance. La liste d'une
machine saine au repos est donc **courte et explicable**, et tout ce qui s'en
écarte mérite une enquête. Pour lire une ligne en détail, ajoutez un
identifiant :

```bash
sudo bpftool prog show id 47
```

```text
47: lsm  name restrict_filesystems  tag 7673068478f99ef8  gpl
	loaded_at 2026-10-17T05:44:08+0000  uid 0
	xlated 520B  jited 297B  memlock 4096B  map_ids 22
	btf_id 48
	pids systemd(1)
```

La première ligne donne dans l'ordre l'**identifiant** (`47`), le **type**
(`lsm`), le **nom** du programme, son **empreinte** (`tag`) et sa licence (`gpl`).
Les lignes suivantes donnent la date de chargement, l'utilisateur qui l'a
chargé (`uid 0`, c'est root), la taille du code et, selon la version de
l'outil, la ligne `pids`. Sur AlmaLinux, elle nomme le processus qui tient le
programme : ici `systemd`, de PID 1. Sur Ubuntu 24.04, cette ligne n'existe pas.
Les programmes `sd_fw_egress`, `sd_fw_ingress` et `sd_devices` ont un nom qui
commence par `sd_` : ce sont ceux de systemd, qui les charge pour filtrer le
réseau et les périphériques de ses services.

### Charger deux sondes jetables pour voir un programme « étranger »

Pour voir à quoi ressemble un programme que personne n'a déployé, on en charge
deux avec `bpftrace`, un outil qui compile une sonde d'une ligne en programme
eBPF et la charge. La commande `systemd-run` les lance chacune dans une unité
**temporaire** nommée par nos soins :

```bash
sudo systemd-run --unit=demo-sonde bpftrace -e 'kprobe:vfs_read { @n = count(); }'
sudo systemd-run --unit=demo-horloge bpftrace -e 'profile:hz:19 { @n = count(); }'
```

```text
Running as unit: demo-sonde.service; invocation ID: 0272031155e8484ea48befef263010a3
Running as unit: demo-horloge.service; invocation ID: a58728f60e2145659cab0afcc47aebba
```

La première sonde compte les appels à la fonction `vfs_read` du noyau ; la
seconde se déclenche 19 fois par seconde sur l'horloge. Relistons, en écartant
le bruit connu de systemd :

```bash
sudo bpftool prog show | grep -E '^[0-9]+:' | grep -vE 'cgroup_(skb|device)'
```

```text
47: lsm  name restrict_filesystems  tag 7673068478f99ef8  gpl
69: socket_filter  tag 6418a962837b40fa
260: perf_event  name profile_hz_19_1  tag 3037f536e6e8b280  gpl
268: kprobe  name kprobe_vfs_read_1  tag 3037f536e6e8b280  gpl
```

Deux programmes sont apparus : un de type `perf_event` et un de type `kprobe`.
Remarquez que **le type ne dépend pas du service** : il dépend de la sorte de
sonde que `bpftrace` a compilée. Sur Ubuntu 24.04, la version 0.20 de `bpftrace`
nomme les programmes autrement, mais les types sont les mêmes :

```text
2: tracing  name hid_tail_call  tag 7cc47bbf07148bfe  gpl
64: perf_event  name 19  tag 8c75940e7e21306d  gpl
68: kprobe  name vfs_read  tag 8c75940e7e21306d  gpl
```

### Retrouver le processus qui tient un programme

Sur AlmaLinux, la ligne `pids` du détail répond directement :

```bash
sudo bpftool prog show id 268
```

```text
268: kprobe  name kprobe_vfs_read_1  tag 3037f536e6e8b280  gpl
	loaded_at 2026-10-17T05:51:41+0000  uid 0
	xlated 512B  jited 296B  memlock 4096B  map_ids 119,120,122,123
	btf_id 316
	pids bpftrace(19797)
```

Sur Ubuntu 24.04, le même détail n'a pas de ligne `pids`. Il faut alors une
autre entrée de l'outil, `bpftool perf show`, qui liste les **processus qui
tiennent une sonde** accrochée par le mécanisme des événements de performance
(les kprobes, les uprobes et les tracepoints) :

```bash
sudo bpftool perf show
```

```text
pid 4408  fd 7: prog_id 68  kprobe  func vfs_read  offset 0
```

La ligne donne le **PID** du processus, le numéro de descripteur de fichier
(`fd`), l'**identifiant du programme** (`prog_id`) et ce à quoi la sonde est
accrochée. Mais cette commande ne voit pas tout : la sonde `profile`, de type
`perf_event`, n'apparaît pas dans sa liste. Elle ne se voit pas non plus dans
`bpftool link show` sur Ubuntu. Sur AlmaLinux, ce `link show` liste en revanche
les liens avec leurs processus, et il rappelle qu'**un lien a son propre type** :

```bash
sudo bpftool link show | grep -A3 'prog 268'
```

```text
25: perf_event  prog 268  
	kprobe ffffffff87116ee4 vfs_read  
	bpf_cookie 0
	pids bpftrace(19797)
```

Le programme `268` est de type `kprobe`, mais le lien qui l'accroche est de type
`perf_event`. Quand on demande « le type d'un programme », c'est la première
ligne de `bpftool prog show` qui fait foi, pas celle d'un lien.

Reste la méthode qui marche partout, quelle que soit la version : un processus
qui tient un programme eBPF garde ouvert un descripteur de fichier dont la cible
s'appelle `anon_inode:bpf-prog`. Le répertoire `/proc/<pid>/fd` les expose, et
`find` les trouve tous d'un coup :

```bash
sudo find /proc -maxdepth 3 -path '/proc/[0-9]*/fd/*' -lname 'anon_inode:bpf-prog' 2>/dev/null
```

```text
/proc/1/fd/14
/proc/1/fd/61
/proc/1/fd/63
...
/proc/19797/fd/8
/proc/19801/fd/8
```

Le PID 1 est `systemd`, qui tient les nombreux programmes du système ; il n'est
pas surprenant. Les deux autres PID sont ceux de nos sondes. Un PID que ni
`systemd` ni vous-même n'expliquez est celui à examiner.

Enfin, tout `bpftool` sait rendre du JSON avec l'option `--json` (ou `-j`), plus
facile à filtrer qu'une sortie en colonnes. Avec `jq`, présent sur les deux
machines du lab, on écarte le bruit de systemd :

```bash
sudo bpftool prog show --json | jq -c '.[] | select(.type | startswith("cgroup") | not) | {id,type,name,pids}'
```

```text
{"id":47,"type":"lsm","name":"restrict_filesystems","pids":[{"pid":1,"comm":"systemd"}]}
{"id":69,"type":"socket_filter","name":null,"pids":null}
{"id":260,"type":"perf_event","name":"profile_hz_19_1","pids":[{"pid":19801,"comm":"bpftrace"}]}
{"id":268,"type":"kprobe","name":"kprobe_vfs_read_1","pids":[{"pid":19797,"comm":"bpftrace"}]}
```

Sur Ubuntu 24.04, le champ `pids` vaut `null`, et c'est `bpftool perf show` ou
`/proc/<pid>/fd` qui fournissent le PID.

### Du processus à l'unité systemd

Un PID ne dit pas qui a lancé le processus. Sous systemd, chaque service tourne
dans son propre **cgroup**, et le nom de l'unité en est le dernier élément.
Trois façons de la lire, avec le PID `19797` de l'exemple :

```bash
cat /proc/19797/cgroup
ps -o unit= -p 19797
systemctl status 19797 --no-pager | head -4
```

```text
0::/system.slice/demo-sonde.service
demo-sonde.service
● demo-sonde.service - [systemd-run] /bin/bpftrace -e "kprobe:vfs_read { @n = count(); }"
     Loaded: loaded (/run/systemd/transient/demo-sonde.service; transient)
  Transient: yes
     Active: active (running) since Sat 2026-10-17 05:51:41 UTC; 4s ago
```

La commande `systemctl status` accepte directement un PID à la place d'un nom
d'unité : c'est la plus courte. Elle donne aussi le fichier de l'unité (`Loaded`)
et sa ligne de commande, de quoi savoir ce qui a été lancé.

### Arrêter une unité, ce que cela décharge

Le noyau libère un programme eBPF quand plus aucun processus ni aucun point d'épinglage ne le tient. Arrêter
l'unité tue son processus, donc décharge le programme :

```bash
sudo systemctl stop demo-sonde demo-horloge
sudo bpftool prog show | grep -E '^[0-9]+:' | grep -vE 'cgroup_(skb|device)'
sudo bpftool perf show
```

```text
47: lsm  name restrict_filesystems  tag 7673068478f99ef8  gpl
69: socket_filter  tag 6418a962837b40fa
```

Les deux sondes ont disparu de la liste, et `bpftool perf show` ne rend plus
rien. Les unités créées par `systemd-run` sont temporaires : une fois arrêtées,
elles n'existent plus nulle part, ce qui ne les rend pas représentatives d'un
vrai service. C'est ce qu'on regarde maintenant.

### Empêcher un service de revenir

Un vrai service vit dans un fichier d'unité, souvent avec `Restart=always` et un
démarrage automatique. Créons-en un de démonstration qui ne fait rien d'utile :

```bash
sudo tee /etc/systemd/system/demo-veilleur.service >/dev/null <<'EOF'
[Unit]
Description=Veilleur de demonstration

[Service]
ExecStart=/usr/bin/sleep infinity
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now demo-veilleur.service
systemctl is-enabled demo-veilleur
systemctl is-active demo-veilleur
```

```text
Created symlink '/etc/systemd/system/multi-user.target.wants/demo-veilleur.service' → '/etc/systemd/system/demo-veilleur.service'.
enabled
active
```

L'unité a **deux états indépendants** : elle est *active* (elle tourne
maintenant) et *enabled* (elle démarrera au prochain boot, par le lien créé dans
`multi-user.target.wants`). Les deux se règlent séparément. Tuer le processus ne
sert à rien, à cause de `Restart=always` :

```bash
ancien=$(systemctl show -p MainPID --value demo-veilleur)
sudo kill "$ancien"; sleep 1
echo "ancien $ancien, nouveau $(systemctl show -p MainPID --value demo-veilleur)"
```

```text
ancien 19970, nouveau 19979
```

Systemd a relancé un nouveau processus en une fraction de seconde. Il faut
arrêter **l'unité**, pas son processus. Mais un arrêt seul laisse l'unité
démarrer au prochain boot :

```bash
sudo systemctl stop demo-veilleur
systemctl is-active demo-veilleur
systemctl is-enabled demo-veilleur
```

```text
inactive
enabled
```

Elle est arrêtée mais toujours `enabled` : elle reviendra au redémarrage. La
commande `systemctl disable` retire le lien, et son option `--now` fait l'arrêt
et la désactivation d'un seul coup :

```bash
sudo systemctl disable demo-veilleur
systemctl is-enabled demo-veilleur
```

```text
Removed '/etc/systemd/system/multi-user.target.wants/demo-veilleur.service'.
disabled
```

L'état `disabled` signifie que l'unité existe mais ne démarre plus toute seule.
Un troisième état, `masked`, interdit même son démarrage à la main : un
masquage remplace l'unité par un lien vers `/dev/null`. Mais `systemctl mask`
**refuse d'écraser un vrai fichier d'unité** :

```bash
sudo systemctl mask demo-veilleur
```

```text
Failed to mask unit: File '/etc/systemd/system/demo-veilleur.service' already exists
```

Le masquage ne s'applique donc qu'à une unité qui n'a pas de fichier dans
`/etc/systemd/system`, par exemple celle d'un paquet (fichier sous
`/usr/lib/systemd/system`), ou après retrait du fichier. Le **retrait** est
l'autre voie, et il cache un piège. Relançons l'unité, puis supprimons son
fichier **sans l'avoir arrêtée** :

```bash
sudo systemctl start demo-veilleur
sudo rm /etc/systemd/system/demo-veilleur.service
sudo systemctl daemon-reload
systemctl is-active demo-veilleur
systemctl is-enabled demo-veilleur
pgrep -a sleep
```

```text
active
not-found
21088 /usr/bin/sleep infinity
```

Le fichier a disparu (`not-found`), mais le processus tourne toujours : retirer
l'unité ne tue pas ce qui est déjà lancé. D'où l'ordre sûr : **arrêter d'abord**,
désactiver ensuite, retirer en dernier si besoin. Terminons proprement la démo.
Le processus orphelin s'arrête par son nom d'unité, qui est encore chargé :

```bash
sudo systemctl stop demo-veilleur
sudo systemctl mask demo-veilleur
systemctl is-enabled demo-veilleur
sudo systemctl unmask demo-veilleur
ls /etc/systemd/system | grep demo
```

```text
Created symlink '/etc/systemd/system/demo-veilleur.service' → '/dev/null'.
masked
Removed '/etc/systemd/system/demo-veilleur.service'.
Removed '/etc/systemd/system/multi-user.target.wants/demo-veilleur.service'.
```

Le fichier ayant été supprimé, le masquage devient possible (état `masked`), et
`unmask` retire à la fois le lien vers `/dev/null` et le lien de démarrage
resté orphelin dans `multi-user.target.wants`. La machine est revenue à son état
d'avant la démonstration.

### Ce qu'un inventaire ne doit pas casser

Un inventaire sert à décider, pas à tout arrêter. Les programmes `sd_*` et ceux
du noyau sont **légitimes** : si vous les déchargez, les services de la machine
perdent leur filtrage réseau ou leur contrôle des périphériques. Pour cette
raison, on isole le coupable avant d'agir : un programme, un PID, une unité. Et
on revérifie ensuite que la liste ne s'est pas vidée de ce que le système charge
lui-même.
