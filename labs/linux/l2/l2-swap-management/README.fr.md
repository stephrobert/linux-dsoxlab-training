# Lab — Ajouter et gérer le swap

## Rappel

[**Gérer le swap sous Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/)

Le swap est un espace disque que le noyau utilise comme extension de la RAM :
quand la mémoire se remplit, les pages inactives y sont déplacées. Il absorbe
les pics et permet l'hibernation, mais un système qui swappe en permanence est
lent. Le swap file est l'option la plus souple ; il doit être en `0600` car il
contient des pages mémoire.

## Le cours

Les exemples ci-dessous travaillent sur `/var/swap-demo`, un fichier de
démonstration : le challenge, lui, vous en demandera un autre, ailleurs et
d'une autre taille. Le but est d'apprendre la méthode, pas de recopier une
ligne.

### Où en est la machine

Avant de toucher à quoi que ce soit, regardez ce qui existe déjà :

```bash
free -h                # colonne « Swap » : total, utilisé, libre
swapon --show          # les espaces de swap actifs, ou rien du tout
```

Une sortie vide de `swapon --show` signifie qu'aucun swap n'est actif. C'est le
cas de départ sur une VM de lab.

### Créer un swap file

Quatre gestes, dans cet ordre. L'ordre compte : on sécurise **avant** de
formater.

```bash
sudo dd if=/dev/zero of=/var/swap-demo bs=1M count=64 status=none
sudo chmod 0600 /var/swap-demo
sudo mkswap /var/swap-demo
sudo swapon /var/swap-demo
```

- **`dd`** alloue le fichier bloc par bloc. `bs=1M count=64` donne 64 Mio :
  la taille est le produit des deux.
- **`chmod 0600`** n'est pas une précaution de style. Le fichier contient des
  pages de mémoire, donc potentiellement des mots de passe ou des clés en
  clair. Lisible par tous, il expose la mémoire de la machine.
- **`mkswap`** écrit la signature d'espace de swap et lui attribue un UUID.
- **`swapon`** l'active immédiatement.

Vérifiez, puis désactivez pour tester la suite proprement :

```bash
swapon --show          # /var/swap-demo doit apparaître, type « file »
sudo swapoff /var/swap-demo
```

> **`dd` plutôt que `fallocate`.** Le manuel `swapon(8)` est explicite : un
> fichier créé avec `fallocate` n'est pas fiable comme swap sur certains
> systèmes de fichiers, parce qu'il peut contenir des trous (extents non
> alloués) que le noyau refuse. `dd` écrit réellement les blocs.

### Rendre le swap persistant

`swapon` ne survit pas au redémarrage. Pour que le swap revienne, il faut une
ligne dans `/etc/fstab` :

```text title="/etc/fstab"
/var/swap-demo none swap sw 0 0
```

Les cinq champs, dans l'ordre : le fichier (ou l'UUID pour une partition), le
point de montage qui n'existe pas pour du swap d'où `none`, le type `swap`, les
options (`sw` suffit), puis `0 0` pour dump et fsck.

Testez **sans redémarrer**, avec `swapon -a` qui active toutes les entrées swap
déclarées dans `fstab` :

```bash
sudo swapon -a
swapon --show
```

> **Une erreur dans `fstab` peut bloquer le démarrage.** Sauvegardez avant
> d'éditer (`sudo cp -a /etc/fstab /etc/fstab.bak`) et vérifiez toujours par
> `sudo swapon -a` : si la commande passe sans erreur, la ligne est correcte.

### Régler la swappiness

`vm.swappiness` contrôle l'**agressivité** du noyau à déplacer des pages vers
le swap. Contrairement à une idée répandue, ce n'est pas un pourcentage de RAM
restante : c'est un poids relatif entre récupérer de la mémoire cache et
déplacer des pages.

```bash
sysctl -n vm.swappiness         # 60 sur beaucoup de distributions,
                                # 30 sur la VM de ce lab : vérifiez, ne supposez pas
```

Une valeur **basse** garde les données en RAM et ne swappe qu'en dernier
recours, ce qu'on veut sur un serveur qui a assez de mémoire. Une valeur haute
swappe plus tôt.

Un réglage à chaud disparaît au redémarrage. Pour qu'il tienne, on dépose un
fichier dans `/etc/sysctl.d/` :

```bash
echo "vm.swappiness = 45" | sudo tee /etc/sysctl.d/99-demo.conf
sudo sysctl -p /etc/sysctl.d/99-demo.conf
sysctl -n vm.swappiness         # doit renvoyer 45
```

Le nom du fichier importe peu, mais il se termine par `.conf` et son préfixe
numérique fixe l'ordre de lecture : `99-` passe en dernier, donc l'emporte.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `swapon: insecure permissions 0644` | le `chmod 0600` a été oublié ou fait après `mkswap` |
| `swapon: read swap header failed` | le fichier n'a pas été formaté par `mkswap` |
| Le swap disparaît au reboot | pas de ligne dans `/etc/fstab` |
| `vm.swappiness` revient à sa valeur initiale au reboot | réglage fait à chaud (`sysctl -w`), sans fichier dans `/etc/sysctl.d/` |
| La valeur ne redescend pas après avoir supprimé le fichier | supprimer le fichier ne réinitialise rien : la valeur vit en mémoire jusqu'au reboot. Reposez-la avec `sudo sysctl -w vm.swappiness=<valeur>` |

Pour tout défaire et repartir de zéro :

```bash
sudo swapoff /var/swap-demo
sudo rm -f /var/swap-demo /etc/sysctl.d/99-demo.conf
sudo sysctl -w vm.swappiness=30      # supprimer le fichier ne suffit pas
```
