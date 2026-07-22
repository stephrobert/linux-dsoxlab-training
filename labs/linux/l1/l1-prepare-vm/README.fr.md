# Lab — Identifier sa machine Linux

## Rappel

[**Installer Linux dans une machine virtuelle**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/)

Pour apprendre l'administration Linux, il faut un système sur lequel pratiquer.
Le guide retient la **machine virtuelle** installée sur votre poste : vous
obtenez un serveur complet, isolé, que vous pouvez casser et recréer à volonté
sans toucher à votre système principal. Il déroule le choix du logiciel de
virtualisation, le téléchargement de l'ISO, la création de la machine et
l'installation minimale. Ce lab ajoute ce que la lecture seule ne dit pas :
pourquoi les trois autres façons d'avoir un Linux sous la main ne se valent pas
pour ce métier, comment contrôler que la virtualisation matérielle est bien là
avant de perdre une heure, et ce qui fait qu'une machine d'étude est utile ou
pénible à vivre.

## Le cours

Les exemples ci-dessous ne portent pas sur le challenge : ils regardent le poste
qui héberge les machines de cette formation, pas la vôtre. Aucun n'écrit quoi
que ce soit.

Toutes les sorties reproduites ici ont été relevées sur le poste hôte du parc de
la formation, une **Ubuntu 24.04.2 LTS**, avec des commandes de **lecture
seule** et **sans un seul `sudo`** : le compte utilisé appartient aux groupes
`kvm` et `libvirt` (vérifié par `id -nG`), ce qui suffit à interroger
l'hyperviseur.

### Quatre façons d'avoir un Linux, et ce qu'elles vous laissent administrer

Le guide des fondamentaux le dit en une ligne : il vous faut « un terminal Linux
(VM, WSL, serveur cloud…) ». Ces voies existent toutes, mais elles ne donnent
pas la même machine entre les mains.

| Voie | Ce que vous obtenez | Ce qui manque pour apprendre l'administration |
|---|---|---|
| **VM locale** (VirtualBox, VMware, KVM/libvirt) | un système d'exploitation complet, avec son propre noyau | rien : c'est le choix du guide |
| **Conteneur** (Docker, Podman) | une application et ses dépendances, sur le noyau de l'hôte | le noyau n'est pas le vôtre, l'isolation est plus faible |
| **WSL2** (Windows) | un noyau Linux compilé par Microsoft, intégré à Windows | ce n'est ni votre noyau ni votre cycle de vie de machine |
| **Serveur distant** (hébergeur) | une machine joignable en SSH | pas de console si vous coupez le réseau |

Le premier réflexe du débutant est d'attraper le plus rapide à installer. C'est
souvent le conteneur, et c'est là que la déception arrive, plus tard.

Le guide sur les machines virtuelles est net sur ce point : **un conteneur n'est
pas une petite VM**. Une VM embarque un système d'exploitation complet, noyau
compris, quand un conteneur **partage le noyau de l'hôte** et n'embarque que
l'application et ses dépendances directes. D'où le tableau du guide :

| Question | VM | Conteneur |
|---|---|---|
| Combien ça pèse ? | plusieurs Go | quelques Mo |
| Temps de démarrage | minutes | secondes |
| Niveau d'isolation | fort (systèmes séparés) | moyen (noyau partagé) |
| Apprendre et expérimenter | **recommandé** | dans un second temps |

La conséquence est directe : puisqu'il n'y a **qu'un seul noyau**, celui de
l'hôte, tout ce qui relève du noyau échappe au conteneur. Or l'administration
système est faite pour beaucoup de cela : redémarrer et vérifier que la
configuration a survécu, partitionner et formater un disque, régler un pare-feu.
Notez au passage que les conteneurs ne tournent nativement que sur Linux :
Docker sur Windows ou sur macOS s'appuie sur une VM Linux cachée.

**WSL2** est un cas à part, et un bon outil : c'est un vrai noyau Linux, mais
compilé par Microsoft, pas celui de votre distribution. Contrairement à une VM
classique qui réserve CPU et RAM à l'avance, WSL2 partage dynamiquement les
ressources du poste, et c'est **Windows** qui tient les commandes de la machine :
`wsl --shutdown` arrête tout, `wsl --terminate Ubuntu` arrête une distribution,
et un fichier `.wslconfig` côté Windows fixe la mémoire et le nombre de
processeurs. Vous administrez un Linux, sans administrer la machine qui le porte.

Le **serveur distant chez un hébergeur** ne demande rien à votre poste et se
travaille par SSH, exactement comme le guide vous apprend à travailler sur votre
VM. Le bloc de fondamentaux ne le détaille pas ; retenez qu'une erreur de réseau
ou de pare-feu vous y laisse sans porte de secours, alors que la console d'une
VM locale reste toujours accessible.

### La virtualisation matérielle se vérifie, elle ne se suppose pas

Le guide d'installation de KVM est catégorique : sans les extensions **Intel
VT-x** ou **AMD-V**, vos machines virtuelles tournent en **émulation pure**,
c'est-à-dire très lentement. Et le tableau de dépannage du guide d'installation
de VM place le message « VT-x is not available » sur une seule cause : la
virtualisation désactivée dans le BIOS/UEFI du poste. Quatre contrôles, du plus
rapide au plus précis.

**1. Ce que le processeur annonce.**

```console
$ lscpu | grep -i virtu
Address sizes:                           39 bits physical, 48 bits virtual
Virtualization:                          VT-x
```

Seule la seconde ligne compte : la première ne sort que parce que `-i` fait
correspondre « virtual » dans « 48 bits virtual ». `VT-x` désigne un processeur
Intel ; sur AMD, cette ligne affiche `AMD-V`.

**2. Le compte des cœurs qui portent l'extension.**

```console
$ grep -Ec '(vmx|svm)' /proc/cpuinfo
32
```

Le guide donne la lecture de ce nombre : `0` signifie pas de support ou support
désactivé dans le BIOS, toute valeur supérieure signifie que la virtualisation
est active. `vmx` est l'extension Intel, `svm` l'extension AMD.

**3. Le point d'entrée du noyau.**

```console
$ ls -l /dev/kvm
crw-rw---- 1 root kvm 10, 232 juil. 22 20:02 /dev/kvm
```

Le fichier existe : le noyau expose l'accélération matérielle. S'il est absent,
le guide de KVM renvoie à la même cause que plus haut, la virtualisation
désactivée dans le BIOS. Notez le groupe propriétaire `kvm` et les droits
`rw-` qui lui sont accordés : c'est ce qui permet à un compte membre de ce
groupe de s'en servir sans passer administrateur.

**4. Les modules effectivement chargés.**

```console
$ lsmod | grep kvm
kvm_intel             487424  41
kvm                  1404928  16 kvm_intel
irqbypass              12288  1 kvm
```

Le module spécifique confirme le fabricant : `kvm_intel` va avec `vmx`,
`kvm_amd` irait avec `svm`. Le `41` de la première ligne est le nombre
d'utilisateurs du module : sur ce poste, des machines virtuelles s'en servent en
ce moment même.

Ces quatre contrôles valent aussi pour **WSL2**, qui repose sur Hyper-V : son
guide liste « Virtualization disabled » parmi les erreurs courantes, avec la
même correction dans le BIOS.

### Dimensionner une machine d'étude

Le guide donne le format qui suffit pour apprendre, et les prérequis côté poste :
au moins **4 Go de RAM** et **20 Go d'espace disque** disponibles.

| Ressource | Valeur recommandée par le guide |
|---|---|
| RAM | 2 Go |
| CPU | 2 vCPU |
| Disque | 20 Go, en allocation dynamique |
| Réseau | NAT |

Ce n'est pas un idéal théorique. Le parc de cette formation est déclaré dans le
fichier `meta.yml` du dépôt, et il tient dans ces valeurs, voire en dessous :

| Machine | RAM | vCPU | Disque |
|---|---|---|---|
| cible RHCSA principale | 2048 Mo | 2 | 20 Go (+ 10 Go) |
| seconde cible RHCSA | 1536 Mo | 1 | 15 Go |
| cible LFCS | 1536 Mo | 1 | 15 Go |

Résultat sur le poste hôte, au moment de la capture :

```console
$ virsh list
 Id   Name                   State
--------------------------------------
 14   web1.lab               running
 15   web2.lab               running
 16   control-node.lab       running
 [...]
 21   alma-rhcsa-2.lab       running
 22   ubuntu-lfcs-1.lab      running
 25   alma-rhcsa-1.lab       running
```

Plusieurs systèmes complets tournent en même temps, précisément parce qu'aucun
ne dépasse 2 Go. Un serveur sans interface graphique se contente de très peu : c'est
la raison pour laquelle le guide insiste sur l'installation **minimale**, sans
bureau et sans serveur web.

Deux règles de partage, tirées du guide sur les machines virtuelles : **le CPU se
prête**, l'hyperviseur distribuant le temps de calcul à tour de rôle, si bien que
promettre plus de vCPU qu'il n'y a de cœurs réels fonctionne tant que les
machines ne travaillent pas toutes à fond en même temps ; **la mémoire, elle, se
réserve**, et donner 4 Go à une machine retire 4 Go au poste même si elle n'en
utilise que 500 Mo. C'est donc elle qui limite le nombre de machines que vous
pourrez démarrer.

### Disque à taille fixe ou à allocation dynamique

Le disque d'une machine virtuelle est un **fichier** sur le poste hôte. Deux
manières de le remplir, indépendantes du format de fichier (`.vdi` pour
VirtualBox, `.qcow2` pour KVM, `.vmdk` pour VMware) :

| Critère | Allocation dynamique (thin) | Taille fixe (thick) |
|---|---|---|
| Espace consommé | ce qui est réellement écrit | tout, dès la création |
| Création | rapide | plus lente, l'espace est réservé |
| Performance | variable, l'espace s'alloue à chaud | constante |
| Risque | saturation du poste si on ne surveille pas | espace immobilisé pour rien |
| Cas d'usage retenu par le guide | labs, tests | production critique, bases de données |

Concrètement, un disque de 100 Go déclaré en dynamique commence à quelques Mo ;
après l'installation d'un système qui occupe 8 Go, le fichier fait environ 8 Go,
alors que la machine, elle, voit toujours 100 Go. D'où les **20 Go en dynamique**
du guide : de la marge, sans payer l'espace tout de suite. Le revers est réel,
plusieurs machines qui grossissent en même temps peuvent remplir le disque du
poste, et c'est le poste qui tombe, pas seulement la machine fautive.

### L'instantané, le filet de celui qui apprend

C'est ce qui change tout quand on débute, parce qu'apprendre consiste
précisément à casser des choses. Le guide distingue trois gestes qu'on confond
souvent :

| Geste | Ce que c'est | Indépendant du disque d'origine ? |
|---|---|---|
| **Instantané** (snapshot) | une photo de l'état à un instant donné | non |
| **Clone** | une copie complète de la machine | oui |
| **Sauvegarde** (backup) | l'export de la configuration et du disque | oui |

Il est quasi instantané à créer et coûte peu d'espace : avec un disque QCOW2, le
disque d'origine est gelé en lecture seule et les écritures suivantes partent
dans un fichier de différences, que revenir en arrière consiste à jeter. La
contrepartie tient en deux points que le guide ne cache pas : l'instantané
**dépend** du disque d'origine, et en empiler dégrade les performances, chaque
lecture devant traverser la chaîne.

La règle d'or se retient en une phrase : **un instantané protège des erreurs
logiques, pas des pannes matérielles**. Il vit dans le même stockage que la
machine ; si le disque du poste lâche, les deux disparaissent ensemble. Pour une
vraie sauvegarde, il faut exporter la machine ailleurs.

Les commandes, selon l'outil :

```bash
# VirtualBox
VBoxManage snapshot "debian-lab" take "avant-maj" --description "Système propre post-install"
VBoxManage snapshot "debian-lab" list
VBoxManage snapshot "debian-lab" restore "avant-maj"
```

```bash
# KVM / libvirt
virsh snapshot-create-as ma-vm --name "avant-upgrade" --description "État stable"
virsh snapshot-list ma-vm
virsh snapshot-revert ma-vm --snapshotname avant-upgrade
```

Prenez l'habitude de nommer l'instantané par ce qu'il précède
(`avant-upgrade-noyau`, `2026-01-31-stable`) et de le poser **avant** la
manipulation risquée, jamais après. Le retour en arrière arrête la machine si
elle tourne, restaure le disque et perd tout ce qui a été fait depuis : c'est
exactement l'effet recherché.

### Dépannage

| Symptôme | Cause probable | Vérification ou correction |
|---|---|---|
| « VT-x is not available » au démarrage de la VM | virtualisation désactivée dans le BIOS/UEFI | activer Intel VT-x ou AMD-V, puis `grep -Ec '(vmx\|svm)' /proc/cpuinfo` doit être supérieur à 0 |
| la VM démarre mais tout est d'une lenteur anormale | pas d'accélération matérielle, le système est émulé | `ls -l /dev/kvm` et `lsmod \| grep kvm` |
| la VM ne démarre pas sur l'ISO | ordre de démarrage incorrect | placer le lecteur CD/DVD en premier |
| écran noir après le redémarrage final | l'ISO est encore montée | retirer le média du lecteur virtuel et redémarrer |
| pas de réseau après l'installation | interface non configurée | `ip link` doit montrer l'interface UP, puis relancer le DHCP |
| `ping` passe mais la mise à jour des paquets échoue | résolution DNS absente | vérifier `/etc/resolv.conf` |
| impossible de joindre la VM en SSH depuis le poste, en mode NAT | la VM n'est pas exposée | ajouter une redirection de ports, puis `ssh -p 2222 utilisateur@127.0.0.1` |
| sous Windows, « Virtualization disabled » à l'installation de WSL2 | même cause que la première ligne | activer VT-x/AMD-V dans le BIOS |
| le poste sature alors que les VM semblent petites | disques en allocation dynamique qui ont grossi | surveiller l'espace réellement consommé sur l'hôte |
