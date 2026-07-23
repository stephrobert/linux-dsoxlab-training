# Lab — paramètre noyau persistant au démarrage

## Rappel

[**GRUB sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/grub/)

`grubby --update-kernel=ALL --args="param"` ajoute un argument noyau aux noyaux
installés ; `--remove-args` le retire ; `--info=DEFAULT` montre les arguments du
noyau par défaut. Le modèle des **futurs** noyaux, lui, est `GRUB_CMDLINE_LINUX`
dans `/etc/default/grub`.

L'état à obtenir est le même dans tous les cas : le paramètre présent aux **deux**
endroits. Le nombre de gestes, lui, dépend de la machine : sur l'AlmaLinux 10
mesurée dans ce cours, `--update-kernel=ALL` écrit les deux ; en ciblant un noyau
précis ou `DEFAULT`, il n'écrit que l'entrée visée. D'où la seule règle qui tienne
partout : on **relit** les deux emplacements, on ne les suppose pas.

## Le cours

Les exemples ci-dessous posent les paramètres `audit=1` et `rd.timeout=30` : le
challenge, lui, vous demandera un autre paramètre. Le but est d'apprendre la
mécanique et surtout de savoir la **vérifier avant de redémarrer**, pas de
recopier une ligne. Toutes les sorties de cette page ont été relevées sur une
**AlmaLinux 10.2** (noyau `6.12.0-211.34.1.el10_2.x86_64`) démarrée en **UEFI**.

> Un paramètre fautif rend la machine non démarrable, et sur une VM sans console
> il n'y a pas de rattrapage. Avant toute chose : sauvegardez `/etc/default/grub`
> et relevez `cat /proc/cmdline`, qui est votre référence de retour. N'ajoutez
> jamais un paramètre que vous ne comprenez pas, et ne **retirez** jamais un
> paramètre déjà présent (`console=`, `root=` et `ro` servent à la plateforme).

### Trois fichiers, et aucun n'est celui qu'on croit

La ligne de commande réellement reçue par le noyau se lit dans `/proc/cmdline` :

```bash
cat /proc/cmdline
```

```text
BOOT_IMAGE=(hd0,gpt3)/vmlinuz-6.12.0-211.34.1.el10_2.x86_64 root=UUID=1f5fce98-2902-4ac3-b784-b4f10857f44e ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0
```

Ce fichier est une vue du noyau en cours d'exécution : on ne l'édite pas, on
change **ce qui le produit**. Trois fichiers y concourent, avec des statuts très
différents.

```bash
cat /etc/default/grub
```

```text
GRUB_TIMEOUT=0
GRUB_DEFAULT=saved
[...]
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0"
GRUB_ENABLE_BLSCFG=true
```

`/etc/default/grub` n'est **pas** lu au démarrage : c'est un fichier d'**entrée**
pour `grub2-mkconfig`. Et la dernière ligne, `GRUB_ENABLE_BLSCFG=true`, commande
tout le reste : les entrées de démarrage ne vivent pas dans `grub.cfg` mais dans
des fichiers **BLS** (*BootLoaderSpec*), un par noyau installé.

```bash
ls /boot/loader/entries/
sudo cat /boot/loader/entries/*-6.12.0-211.34.1.el10_2.x86_64.conf
```

```text
title AlmaLinux (6.12.0-211.34.1.el10_2.x86_64) 10.2 (Lavender Lion)
version 6.12.0-211.34.1.el10_2.x86_64
linux /vmlinuz-6.12.0-211.34.1.el10_2.x86_64
initrd /initramfs-6.12.0-211.34.1.el10_2.x86_64.img $tuned_initrd
options root=UUID=1f5fce98-[...] ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 $tuned_params
[...]
```

C'est la ligne **`options`** qui devient `/proc/cmdline`. Le `$tuned_params` final
est une variable que GRUB développe au démarrage : elle est normale, ne la
supprimez pas.

Quant au `grub.cfg`, il ne contient plus aucune entrée de noyau :

```bash
sudo grep -nE 'insmod blscfg|^blscfg|set kernelopts' /boot/grub2/grub.cfg
```

```text
132:  set kernelopts="root=UUID=1f5fce98-[...] no_timer_check biosdevname=0 net.ifnames=0 "
135:insmod blscfg
136:blscfg
```

La commande `blscfg` va lire `/boot/loader/entries/`. Le `set kernelopts` de la
ligne 132 n'est qu'un **repli**, utilisé si la variable n'est définie ni dans
`grubenv` ni dans l'entrée BLS. Ici chaque entrée porte sa propre ligne
`options` : ce repli ne sert jamais, et cela explique la surprise à venir.

### Le fichier généré : trouvez-le, ne le supposez pas

Le chemin du `grub.cfg` actif dépend du mode d'amorçage, et c'est une erreur
classique que de viser le mauvais. On commence donc par déterminer ce mode :

```bash
ls -d /sys/firmware/efi     # existe : UEFI ; absent : BIOS hérité
sudo find /boot -name grub.cfg
```

```text
/sys/firmware/efi
/boot/efi/EFI/almalinux/grub.cfg
/boot/grub2/grub.cfg
```

Deux fichiers, donc, et il faut savoir lequel régénérer. Celui de la partition
EFI ne fait que quatre lignes :

```text
search --no-floppy --root-dev-only --fs-uuid --set=dev cea79fb2-[...]
set prefix=($dev)/grub2
export $prefix
configfile $prefix/grub.cfg
```

C'est une **amorce** : elle cherche la partition portant cet UUID (ici `/dev/vda3`,
montée sur `/boot`, ce que `blkid` et `findmnt /boot` confirment), puis charge
`/boot/grub2/grub.cfg`. La configuration réelle est donc celle de `/boot/grub2/`,
même en UEFI, ce que confirment les liens symboliques de la distribution :

```bash
ls -l /etc/grub2.cfg /etc/grub2-efi.cfg
```

```text
/etc/grub2.cfg -> ../boot/grub2/grub.cfg
/etc/grub2-efi.cfg -> ../boot/grub2/grub.cfg
```

Le guide compagnon rapporte qu'en AlmaLinux 9.8 le `grub.cfg` actif était encore
dans `/boot/efi/EFI/almalinux/` et que `/boot/grub2/grub.cfg` n'existait pas. Sur
l'AlmaLinux 10.2 mesurée ici, l'unification est faite, et sa leçon reste entière :
**localisez votre `grub.cfg` avec `find` au lieu de supposer son chemin**. Dans
tous les cas on ne l'édite jamais à la main, il est réécrit à chaque mise à jour
de noyau.

### Éditer `/etc/default/grub` ne suffit pas : la démonstration

Ajoutons `audit=1` au modèle, sans rien régénérer. Le `sed` reprend le contenu
existant entre guillemets et lui ajoute le paramètre à la fin, ce qui garantit de
n'en supprimer aucun :

```bash
sudo cp /etc/default/grub /root/grub.bak
sudo sed -i 's/^GRUB_CMDLINE_LINUX="\(.*\)"/GRUB_CMDLINE_LINUX="\1 audit=1"/' /etc/default/grub
grep GRUB_CMDLINE_LINUX /etc/default/grub
```

```text
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 audit=1"
```

Rien d'autre n'a bougé sur le disque : les sommes de contrôle de `grub.cfg` et des
deux entrées BLS sont inchangées. Après un `sudo reboot`, `/proc/cmdline` est
strictement identique à celui du haut de cette page, **sans `audit=1`** : le
fichier que nous venons d'éditer n'est lu par personne au démarrage.

Régénérons maintenant la configuration :

```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

```text
Generating grub configuration file ...
Adding boot menu entry for UEFI Firmware Settings ...
done
```

Voici la deuxième surprise, propre aux systèmes BLS : seul le **repli** de
`grub.cfg` a reçu le paramètre.

```text
132:  set kernelopts="root=UUID=1f5fce98-[...] net.ifnames=0 audit=1 "
```

Les lignes `options` des entrées BLS, elles, ont gardé la même somme de contrôle,
et `grubby --info=DEFAULT` ne montre toujours pas `audit=1`. Un second
redémarrage l'a confirmé : `/proc/cmdline` est encore identique à l'original. Sur
une machine en mode BLS, `grub2-mkconfig` **ne réécrit pas les entrées de
démarrage déjà installées**.

Ce que la régénération a bien fait, en revanche, c'est mettre à jour le modèle des
**futurs** noyaux :

```bash
sudo cat /etc/kernel/cmdline
```

```text
root=UUID=1f5fce98-[...] ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 audit=1
```

C'est ce fichier que lit `/usr/lib/kernel/install.d/20-grub.install` pour
fabriquer l'entrée BLS d'un noyau fraîchement installé. Le script le dit
lui-même, et resynchronise au passage si `/etc/default/grub` est plus récent :

```text
if [[ /etc/kernel/cmdline -ot /etc/default/grub ]]; then
    grub2-mkconfig -o /etc/grub2.cfg      # user modified /etc/default/grub manually; sync
fi
read -r -d '' -a BOOT_OPTIONS < /etc/kernel/cmdline
```

### `grubby` : l'outil qui touche les entrées existantes

`grubby` (paquet `grubby`, installé d'origine) lit et écrit directement les
entrées de démarrage.

```bash
sudo grubby --default-kernel        # quel noyau démarre par défaut
sudo grubby --info=DEFAULT          # ses arguments
sudo grubby --info=ALL              # toutes les entrées, avec leur index
```

```text
index=1
kernel="/boot/vmlinuz-6.12.0-211.34.1.el10_2.x86_64"
args="ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 $tuned_params"
root="UUID=1f5fce98-[...]"
[...]
```

Ajoutons le paramètre aux noyaux installés :

```bash
sudo grubby --update-kernel=ALL --args="audit=1"
sudo grep -h ^options /boot/loader/entries/*.conf
```

```text
options root=UUID=1f5fce98-[...] net.ifnames=0 $tuned_params audit=1
options root=UUID=1f5fce98-[...] net.ifnames=0 audit=1
```

L'effet est immédiat dans les fichiers d'entrée, sans aucune régénération. Après
redémarrage, le paramètre est enfin là :

```text
BOOT_IMAGE=(hd0,gpt3)/vmlinuz-6.12.0-211.34.1.el10_2.x86_64 root=UUID=[...] ro console=tty0 console=ttyS0,115200n8 no_timer_check biosdevname=0 net.ifnames=0 audit=1
```

Deux comportements de `grubby` méritent d'être connus, parce qu'ils ont été
mesurés ici et que le guide ne les décrit pas. Le premier : avec
`--update-kernel=ALL`, `grubby` met aussi à jour `GRUB_CMDLINE_LINUX` dans
`/etc/default/grub` **et** `/etc/kernel/cmdline`. Une seule commande couvre donc
les noyaux installés et les futurs. Le second : ce n'est vrai **que** pour `ALL`.
En ciblant un noyau précis, ou avec le mot-clé `DEFAULT`, seule l'entrée visée
change et le modèle reste intact.

```bash
sudo grubby --update-kernel=/boot/vmlinuz-6.12.0-211.7.3.el10_2.x86_64 --args="rd.timeout=30"
grep GRUB_CMDLINE_LINUX /etc/default/grub    # inchangé
```

Le retrait suit la même logique, et `--remove-args` sur `ALL` nettoie lui aussi
les trois emplacements :

```bash
sudo grubby --update-kernel=/boot/vmlinuz-6.12.0-211.7.3.el10_2.x86_64 --remove-args="rd.timeout=30"
sudo grubby --update-kernel=ALL --remove-args="audit=1"
```

N'en concluez pas qu'il suffit de retenir « `ALL` fait tout » : relisez les deux
endroits après coup, c'est le geste qui vous sauvera sur une machine dont la
version de `grubby` se comporte autrement.

### Vérifier avant de redémarrer, puis après

C'est ce qui sépare une manipulation sûre d'un pari. **Avant** le redémarrage,
relisez la ligne qui sera réellement utilisée et assurez-vous qu'elle porte
toujours `root=`, `ro` et les paramètres d'origine :

```bash
sudo grep -h ^options /boot/loader/entries/*.conf
sudo grubby --info=DEFAULT
```

Une ligne `options` sans `root=` est une machine perdue. Sur un système sans BLS
(`GRUB_ENABLE_BLSCFG=false`, ou une Debian), la même vérification porte sur les
lignes `linux` du `grub.cfg` généré :

```bash
sudo grep -E '^[[:space:]]+linux' /boot/grub2/grub.cfg
```

**Après** le redémarrage, `/proc/cmdline` fait foi. Le journal du noyau donne la
même information, avec un bonus :

```bash
sudo journalctl -k -b | grep -i 'command line'
```

```text
kernel: Kernel command line: BOOT_IMAGE=[...] net.ifnames=0 audit=1
kernel: Unknown kernel command line parameters "BOOT_IMAGE=(hd0,gpt3)/vmlinuz-6.12.0-211.34.1.el10_2.x86_64 biosdevname=0", will be passed to user space.
```

La seconde ligne liste ce que le noyau n'a pas consommé : c'est là qu'apparaît un
paramètre mal orthographié. Ne la lisez pas trop vite, elle contient déjà des
entrées légitimes (ici `BOOT_IMAGE` et `biosdevname=0`, destinés à l'espace
utilisateur) ; mais un paramètre que vous venez d'ajouter et qui s'y retrouve est
un paramètre ignoré.

### La modification volatile au menu GRUB

Au menu GRUB, la touche **`e`** ouvre l'entrée sélectionnée en édition. On se
place sur la ligne commençant par `linux`, on ajoute ou on retire un paramètre,
puis **`Ctrl+X`** (ou `F10`) démarre avec cette ligne modifiée. Rien n'est écrit
sur le disque : au redémarrage suivant, l'entrée d'origine revient telle quelle.

C'est la compétence de récupération du sujet, et c'est aussi la raison d'être du
mot de passe GRUB décrit dans le guide compagnon : qui atteint ce menu peut
ajouter `init=/bin/bash` et obtenir un shell root sans authentification.

**Cette manipulation n'a pas été exécutée pour ce cours** : elle exige une console
graphique ou série, dont la machine d'atelier ne dispose pas, et le
`GRUB_TIMEOUT=0` de cette image ne laisse de toute façon aucun délai pour afficher
le menu. La différence à retenir est celle du support : l'édition au menu vit en
mémoire le temps d'un démarrage, `grubby` et `/etc/default/grub` écrivent sur le
disque et survivent aux redémarrages.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `/proc/cmdline` inchangé après édition de `/etc/default/grub` | pas de régénération, ou système en mode BLS où `grub2-mkconfig` ne touche pas les entrées existantes : passer par `grubby` |
| `grubby --info=DEFAULT` ne montre pas le paramètre | modification faite dans `/etc/default/grub` seulement |
| Paramètre présent aujourd'hui, perdu après une mise à jour du noyau | le modèle n'a pas suivi : vérifier `/etc/default/grub` et `/etc/kernel/cmdline` |
| Le paramètre apparaît dans `Unknown kernel command line parameters` | faute de frappe, ou paramètre destiné à l'espace utilisateur |
| Modifications perdues après une mise à jour de paquet | `grub.cfg` édité à la main, alors qu'il est régénéré : passer par `/etc/default/grub` |
| `grub.cfg` introuvable au chemin attendu | chemin variable selon BIOS ou UEFI : `find /boot -name grub.cfg` |
| Machine qui ne redémarre plus | ligne `options` sans `root=`, ou paramètre touchant au disque, au réseau ou à l'init : plus de réparation possible sans console, d'où la vérification systématique **avant** le redémarrage |

Pour tout défaire et revenir à l'état initial :

```bash
sudo grubby --update-kernel=ALL --remove-args="audit=1"
sudo cp /root/grub.bak /etc/default/grub
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo reboot
```

Au retour, `cat /proc/cmdline` doit redonner exactement la valeur relevée au
début. C'est le seul contrôle qui compte.
