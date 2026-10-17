# Lab : durcir un réglage noyau et le rendre durable

## Rappel

[**Durcir eBPF sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/durcir-ebpf/)

Le noyau Linux expose des centaines de réglages, lisibles et modifiables avec
la commande `sysctl`. Certains décident de qui a le droit de faire quoi, par
exemple de charger un programme eBPF dans le noyau. Ce lab apprend les trois
gestes qui font un durcissement fiable : **lire** un réglage, le **changer**, et
surtout le rendre **durable**, c'est-à-dire s'assurer qu'il sera toujours là
après le prochain démarrage. Le piège classique n'est pas de poser la valeur,
c'est de croire qu'elle tient.

## Le cours

Les exemples ci-dessous portent sur un réglage sans rapport avec eBPF
(`vm.swappiness`, qui décide à quel point le noyau pousse la mémoire vers le
swap) : le challenge posera un problème différent, à vous de transférer ce que
vous aurez vu. Toutes les sorties reproduites ici ont été obtenues sur
AlmaLinux 10.2 (noyau 6.12) et sur Ubuntu 24.04 (noyau 6.8), sur une machine
fraîche.

### Lire et changer un réglage noyau : `sysctl`

Un réglage noyau est un fichier du pseudo-système `/proc/sys`, et `sysctl` le
lit sous la forme `clé = valeur`. Les points de la clé remplacent les barres
obliques du chemin.

```bash
sysctl vm.swappiness
```

```text
vm.swappiness = 30
```

Sur Ubuntu 24.04, la valeur d'origine est `60` : **la valeur par défaut change
d'une distribution à l'autre**, ce qui est une raison de plus de la lire avant
de la fixer. Pour la changer tout de suite, on ajoute l'option `-w`, avec les
droits root :

```bash
sudo sysctl -w vm.swappiness=10
```

```text
vm.swappiness = 10
```

Le noyau applique la nouvelle valeur immédiatement. Certains réglages ne se
lisent pas non plus avec un compte ordinaire : `sysctl` répond alors
`permission denied on key '<clé>'`, et c'est `sudo` qui règle la question. Le
réglage `net.core.bpf_jit_harden`, qui concerne le compilateur à la volée des
programmes eBPF, en fait partie :

```bash
sysctl net.core.bpf_jit_harden
sudo sysctl net.core.bpf_jit_harden
```

```text
sysctl: permission denied on key 'net.core.bpf_jit_harden'
net.core.bpf_jit_harden = 1
```

La seconde ligne vient d'AlmaLinux ; Ubuntu 24.04 rend `0` avec le même `sudo`.
Là encore, **les deux distributions ne partent pas du même état**.

### Les deux réglages eBPF, et ce que veulent dire leurs valeurs

eBPF permet de charger de petits programmes dans le noyau, par un appel système
nommé `bpf()`. Deux réglages encadrent cet appel. Le premier,
`kernel.unprivileged_bpf_disabled`, décide si un utilisateur **sans privilège**
(un compte ordinaire, sans `root` ni capacité particulière) a le droit de
l'appeler. La documentation du noyau donne trois valeurs :

| Valeur | Effet sur un appelant sans privilège | Réversible ? |
| --- | --- | --- |
| `0` | `bpf()` est autorisé | oui |
| `1` | `bpf()` est refusé | **non**, jusqu'au prochain redémarrage |
| `2` | `bpf()` est refusé | oui |

Le second, `net.core.bpf_jit_harden`, agit sur le **JIT** (*just-in-time*), le
compilateur qui traduit à la volée un programme eBPF en instructions du
processeur. Une attaque dite de « JIT spraying » consiste à influencer le code
généré ; le durcissement « aveugle » les constantes pour la déjouer :

| Valeur | Effet |
| --- | --- |
| `0` | durcissement désactivé |
| `1` | activé pour les programmes chargés par des appelants sans privilège |
| `2` | activé pour **tous** les programmes, y compris ceux chargés par `root` |

Retenez la colonne « réversible » du premier tableau : elle compte plus loin.

### Changer à chaud ne dure pas

Une valeur posée avec `sysctl -w` vit dans la mémoire du noyau, et nulle part
ailleurs. Au démarrage suivant, le noyau repart de ses défauts, puis le service
`systemd-sysctl` applique les fichiers de configuration. Ce qui n'est écrit dans
aucun fichier disparaît donc. Un rechargement de ces fichiers à la demande se
fait avec :

```bash
sudo sysctl --system > /dev/null
sysctl vm.swappiness
```

```text
vm.swappiness = 10
```

La valeur est toujours `10`, mais pour une raison trompeuse : `sysctl --system`
applique **ce que les fichiers disent** et ne touche pas aux clés qu'ils ne
mentionnent pas. Il ne ramène pas la valeur d'origine, il ne remet rien en
ordre. Seul un vrai redémarrage prouve qu'un réglage n'existe que dans la
mémoire. Il se trouve que ce rechargement est aussi le moyen d'obtenir, sans
redémarrer, ce que le démarrage ferait : tout ce qu'un fichier fixe est
réappliqué.

### Rendre durable : un fichier dans `/etc/sysctl.d/`

La configuration durable vit dans des fichiers `.conf`, lus dans deux
répertoires : `/usr/lib/sysctl.d/` pour ceux que fournissent les paquets, et
`/etc/sysctl.d/` pour ceux de l'administrateur, auquel on écrit. Sur
AlmaLinux 10, le second ne contient au départ qu'un fichier, `99-sysctl.conf` ;
sur Ubuntu 24.04, il en contient une dizaine (`10-kernel-hardening.conf`,
`10-ptrace.conf`...). Chaque ligne d'un fichier est un `clé = valeur`.

Créons deux fichiers de démonstration, avec deux valeurs différentes pour la même
clé :

```bash
echo 'vm.swappiness = 20' | sudo tee /etc/sysctl.d/50-demo-reglage.conf
echo 'vm.swappiness = 40' | sudo tee /etc/sysctl.d/90-demo-reglage.conf
sudo sysctl --system | grep -E "demo|swappiness"
sysctl vm.swappiness
```

```text
* Applying /etc/sysctl.d/50-demo-reglage.conf ...
* Applying /etc/sysctl.d/90-demo-reglage.conf ...
vm.swappiness = 20
vm.swappiness = 40
vm.swappiness = 40
```

C'est la lecture la plus utile du cours. `sysctl --system` annonce chaque
fichier qu'il lit (`Applying ...`), **dans l'ordre alphabétique des noms**, tous
répertoires confondus, et applique chaque valeur au passage. Quand deux
fichiers fixent la même clé, **le dernier lu gagne** : ici `90-demo-reglage.conf`
écrase `50-demo-reglage.conf`, et le noyau retient `40`. C'est pour cela que les
fichiers portent un préfixe numérique, et qu'un fichier nommé `99-...` a le
dernier mot sur presque tous les autres.

Pour savoir **qui fixe une clé**, sans deviner, cherchez son nom dans tous les
endroits que `sysctl` lit :

```bash
sudo grep -rn swappiness /etc/sysctl.d /usr/lib/sysctl.d /etc/sysctl.conf
```

```text
/etc/sysctl.d/50-demo-reglage.conf:1:vm.swappiness = 20
/etc/sysctl.d/90-demo-reglage.conf:1:vm.swappiness = 40
```

Le résultat nomme chaque fichier, avec son numéro de ligne. Si l'un d'eux n'a
pas de raison d'être, on le supprime ou on le corrige, puis on recharge : en
retirant `90-demo-reglage.conf`, `sudo sysctl --system` redonne `20`. Pour
terminer, nettoyez la démonstration :

```bash
sudo rm /etc/sysctl.d/50-demo-reglage.conf /etc/sysctl.d/90-demo-reglage.conf
sudo sysctl -w vm.swappiness=30
```

(`30` est la valeur d'origine d'AlmaLinux ; mettez `60` sur Ubuntu.)

### Vérifier le comportement, pas seulement la valeur

Lire une valeur prouve ce qu'a écrit l'administrateur. Pour prouver ce que fait
le noyau, on lui pose la question. Le programme Python ci-dessous appelle `bpf()`
pour créer une petite table eBPF (opération `BPF_MAP_CREATE`), en se faisant
passer par l'utilisateur `nobody`, un compte sans privilège présent sur toutes
les distributions. Le numéro de l'appel système change avec l'architecture :
321 sur x86_64, 280 sur aarch64.

```bash
sudo -u nobody python3 - <<'PY'
import ctypes, errno, os, platform, struct

numeros = {"x86_64": 321, "aarch64": 280}
libc = ctypes.CDLL(None, use_errno=True)
attr = ctypes.create_string_buffer(128)
struct.pack_into("IIIII", attr, 0, 2, 4, 4, 1, 0)
retour = libc.syscall(numeros[platform.machine()], 0, attr, 128)
if retour >= 0:
    print("accepté : le noyau a créé la table (uid %d)" % os.getuid())
else:
    code = ctypes.get_errno()
    print("refusé : %s (%s), uid %d" % (errno.errorcode[code], os.strerror(code), os.getuid()))
PY
```

```text
refusé : EPERM (Operation not permitted), uid 65534
```

`EPERM` est le code d'erreur « opération non permise » : le noyau a refusé
l'appel, c'est la preuve que la porte est fermée pour cet utilisateur. Selon
l'état de départ de la machine, vous verrez au contraire la ligne « accepté » :
c'est alors le signe que la porte est ouverte. Le même programme lancé avec
`sudo python3 -` (donc en `root`) est, lui, toujours accepté. Ce résultat se
décide à l'instant de l'appel, dans le noyau en marche : un fichier de
configuration correct ne change rien tant que sa valeur n'a pas été appliquée.

### Pourquoi la valeur `1` est un piège sur une machine de lab

La valeur `1` de `kernel.unprivileged_bpf_disabled` ferme la porte **sans retour
possible**. Voici ce qu'un noyau répond, sur une VM jetable, quand on tente de
la rouvrir après l'avoir posée (ne le faites pas sur la machine du lab) :

```text
sudo sysctl -w kernel.unprivileged_bpf_disabled=1
kernel.unprivileged_bpf_disabled = 1
sudo sysctl -w kernel.unprivileged_bpf_disabled=0
sysctl: setting key "kernel.unprivileged_bpf_disabled": Operation not permitted
sudo sysctl -w kernel.unprivileged_bpf_disabled=2
sysctl: setting key "kernel.unprivileged_bpf_disabled": Operation not permitted
```

Même vers `2`, le noyau refuse : la valeur `1` est verrouillée jusqu'au
redémarrage de la machine. C'est une protection voulue sur un serveur de
production, où l'on ne veut pas qu'un attaquant la rouvre. C'est un obstacle sur
un lab qui doit pouvoir se remettre à zéro entre deux essais, d'où la valeur
attendue par le challenge.
