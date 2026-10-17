# Lab : tracer le noyau avec les outils eBPF

## Rappel

[**bpftrace sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/ebpf/tracer/bpftrace/)

eBPF permet de charger de petits programmes dans le noyau pour **observer** ce
qu'il fait : chaque fichier ouvert, chaque programme lancé, chaque connexion.
Rien n'est modifié sur la machine et rien n'est à installer côté application :
on regarde passer les appels système. Ce lab apprend à lire ces traces avec
deux familles d'outils : **BCC** (une collection de commandes prêtes à
l'emploi) et **bpftrace** (un langage de une ligne).

## Le cours

Les exemples ci-dessous observent des commandes jetables (`cat`, `ls`, `date`)
lancées à la main : le challenge vous posera un problème différent, où c'est à
vous de trouver quoi regarder. Toutes les sorties reproduites ici ont été
obtenues sur AlmaLinux 10.2 (noyau 6.12, `bcc-tools 0.35.0`, `bpftrace 0.24.2`)
et sur Ubuntu 24.04 (noyau 6.8, `bpfcc-tools 0.29.1`, `bpftrace 0.20.2`).

### Il faut être root, toujours

Un programme eBPF est chargé dans le noyau : seul `root` peut le faire. Sans
`sudo`, les deux familles refusent, chacune à sa façon :

```bash
bpftrace -e 'BEGIN { exit(); }'
```

```text
ERROR: bpftrace currently only supports running as the root user.
```

Les outils BCC, eux, échouent plus bruyamment : un `could not open bpf map:
infotmp, error: Operation not permitted` suivi d'une trace Python. Si vous voyez
une trace Python qui se termine par `Operation not permitted`, relancez avec
`sudo`, il n'y a rien d'autre à chercher. La valeur du réglage
`kernel.unprivileged_bpf_disabled` explique ce comportement : elle vaut `2` sur
les deux distributions, ce qui interdit l'eBPF aux utilisateurs ordinaires.

### Installer BCC, et où se trouvent les outils

Les noms de paquet et les noms de commande diffèrent selon la famille de
distribution. Sur AlmaLinux 10 :

```bash
sudo dnf install bcc-tools
rpm -ql bcc-tools | grep -E '/(open|exec)snoop$'
```

```text
/usr/share/bcc/tools/execsnoop
/usr/share/bcc/tools/opensnoop
```

Les outils sont rangés dans `/usr/share/bcc/tools/`, un répertoire **absent du
`PATH`** : `opensnoop` tout court répond `command not found`. On les appelle par
leur chemin complet, ou on ajoute le répertoire au `PATH` de la session.

Sur Ubuntu 24.04, le paquet s'appelle `bpfcc-tools` et chaque commande porte le
suffixe `-bpfcc`, dans un répertoire déjà dans le `PATH` : `opensnoop-bpfcc`,
`execsnoop-bpfcc`. Les options sont les mêmes, seul le nom change. Les pages de
manuel se nomment `bcc-opensnoop` sur AlmaLinux et `opensnoop-bpfcc` sur Ubuntu.

Un détail d'installation mérite d'être connu. Le paquet `bcc-tools` tire
`kernel-devel` en dépendance, et dnf installe la version **la plus récente**,
pas celle du noyau en cours. Au moment de préparer ce lab, le noyau actif était
le `6.12.0-211.64.1` alors que `kernel-devel` arrivait en `211.65.1` :

```bash
uname -r
rpm -q kernel-devel
ls -L /lib/modules/$(uname -r)/build
```

Dans ce cas, le lien `/lib/modules/<noyau actif>/build` pointe dans le vide.
Les outils ont pourtant fonctionné : BCC a reconstruit lui-même des en-têtes
dans `/tmp/kheaders-<noyau actif>` à partir du module noyau `kheaders`. Si un
outil se plaint de ne pas trouver les en-têtes du noyau, comparez d'abord
`uname -r` à `rpm -q kernel-devel` : un redémarrage sur le noyau le plus récent
règle l'écart.

### Les fichiers ouverts : `opensnoop`

`opensnoop` affiche chaque ouverture de fichier, au moment où elle a lieu, avec
le nom du programme qui l'a demandée. On l'isole sur la commande `cat` pour ne
pas noyer la lecture. Dans un terminal :

```bash
sudo /usr/share/bcc/tools/opensnoop -n cat
```

Dans un second terminal, lancez `cat /etc/hostname`. Le premier terminal affiche :

```text
PID    COMM               FD ERR PATH
25205  cat                 3   0 /etc/ld.so.cache
25205  cat                 3   0 /lib64/libc.so.6
25205  cat                 3   0 /etc/hostname
```

Chaque colonne a un sens précis :

- **PID** : le processus qui ouvre, utile pour le retrouver ensuite avec `ps`.
- **COMM** : le nom du programme (limité à 15 caractères par le noyau).
- **FD** : le descripteur obtenu, ou `-1` si l'ouverture a échoué.
- **ERR** : le code d'erreur associé (`2` pour fichier introuvable, par exemple).
- **PATH** : le chemin demandé, tel que le programme l'a écrit.

On y voit que `cat` ouvre d'abord deux bibliothèques pour démarrer, puis enfin
le fichier demandé : le bruit de démarrage entoure toujours l'information utile.
Trois options aident à le réduire. `-n cat` ne garde que les programmes dont le
nom **contient** `cat`. `-p 25205` suit un seul processus. `-d 10` arrête
la trace au bout de dix secondes, ce qui évite de devoir interrompre à la main.

Un piège de redirection : si vous envoyez la sortie dans un fichier, Python met
l'affichage en tampon et un arrêt par `timeout` perd tout ce qui n'avait pas été
écrit. Positionnez `PYTHONUNBUFFERED=1` devant la commande, ou préférez `-d`.

### Les programmes lancés : `execsnoop`

`execsnoop` fait la même chose pour les lancements de programmes : une ligne par
`execve`, avec le parent. Lancez-le dans un terminal, puis exécutez dans un
second `bash -c 'ls /etc > /dev/null; date > /dev/null'` :

```bash
sudo /usr/share/bcc/tools/execsnoop
```

```text
COMM             PID     PPID    RET ARGS
bash             25219   25190      0 /bin/bash -c ls /etc > /dev/null; date > /dev/null
ls               25220   25219      0 /bin/ls /etc
date             25221   25219      0 /bin/date
```

La colonne qui compte ici est **PPID** : le numéro du processus parent. Le `bash`
de PID 25219 a lancé deux enfants, `ls` et `date`, qui portent tous les deux
`PPID 25219`. La ligne de `bash` elle-même montre un parent différent
(25190, le shell de la session). Quand un programme lance régulièrement des
commandes, ses enfants défilent avec un PPID constant : ce nombre est le fil à
tirer. `RET` vaut `0` quand le lancement a réussi.

Pour passer d'un PID à un nom de programme, `ps` suffit :

```bash
ps -o pid,ppid,comm,args -p 25219
```

```text
    PID    PPID COMMAND         COMMAND
  25219   25190 bash            bash -c ls /etc > /dev/null; date > /dev/null
```

Sur une machine réelle, `execsnoop` montre beaucoup plus que votre commande :
les tâches du système lancent aussi des programmes en continu. Filtrez avec `-n`
(motif cherché dans la commande lancée) ou `-P` (PID du parent), sinon l'information se noie.

### bpftrace : la même chose en une ligne

`bpftrace` ne fournit pas d'outils tout faits : on décrit l'événement à observer
dans un mini-langage. Pour reproduire `opensnoop` sur `cat` en une ligne :

```bash
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat /comm == "cat"/ { printf("%s %s\n", comm, str(args->filename)); }'
```

```text
Attached 1 probe
cat /etc/ld.so.cache
cat /lib64/libc.so.6
cat /etc/hostname
```

Lisez la ligne de gauche à droite. `tracepoint:syscalls:sys_enter_openat` est la
**sonde** : elle se déclenche à chaque appel système `openat`. Le filtre entre
barres obliques (`/comm == "cat"/`) ne garde que les appels faits par `cat`.
Le bloc entre accolades dit quoi afficher : `comm` (le nom du programme) et
`str(args->filename)` (le chemin demandé, converti en texte). Sur Ubuntu 24.04,
bpftrace 0.20 affiche `Attaching 1 probe...` au lieu de `Attached 1 probe` :
seul l'habillage change.

Les deux familles se complètent. BCC répond tout de suite aux questions
courantes. bpftrace permet de poser une question qu'aucun outil ne couvre,
au prix d'un peu de syntaxe.

### Vérifier que l'outil fonctionne vraiment

Un outil installé n'est pas un outil qui marche : charger le programme eBPF
peut échouer pour une raison de droits ou d'en-têtes, et `--help` ne le montrera
pas, car il s'affiche avant tout chargement. Le test le plus court consiste à
lancer l'outil une seconde :

```bash
sudo /usr/share/bcc/tools/opensnoop -d 1 > /dev/null; echo $?
```

```text
0
```

Un code de retour `0` prouve que l'outil a compilé, chargé son programme dans le
noyau et s'est arrêté proprement. C'est ce même contrôle que le challenge
applique.
