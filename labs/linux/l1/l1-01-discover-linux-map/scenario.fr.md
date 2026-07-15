# Lab l1-01 — Cartographier Linux : noyau, distribution et répertoires clés

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B0) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 20 min |
| **Référence** | [Notions fondamentales Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/) |

---

## Ce que vous allez apprendre

À la fin de ce lab vous saurez :

- Distinguer Linux (le noyau) d'une distribution Linux
- Identifier la version du noyau qui tourne sur votre système
- Identifier le nom et la version de votre distribution
- Expliquer le rôle de `/etc`, `/var/log`, `/proc` et `/home`
- Utiliser `uname`, `cat /etc/os-release` et des listings pour recueillir des informations système

Aucun fichier système n'est modifié. Ce lab est une exploration en lecture seule.

---

## Référence des commandes

| Commande | Ce qu'elle fait |
|---------|----------------|
| `uname -r` | Affiche la version du noyau en cours d'exécution |
| `uname -a` | Affiche toutes les informations noyau |
| `cat /etc/os-release` | Affiche le nom et la version de la distribution |
| `hostnamectl` | Affiche le nom d'hôte et les détails OS (systèmes systemd) |
| `ls /etc \| head -20` | Liste les 20 premières entrées du répertoire de configuration |
| `ls /var/log` | Liste les fichiers de journaux |
| `ls /proc \| head -20` | Liste les premières entrées du système de fichiers virtuel |
| `ls /home` | Liste les répertoires personnels des utilisateurs |

---

## Exercice 1 — Identifier le noyau

Le **noyau** est le cœur du système d'exploitation. Il gère directement le matériel :
ordonnancement CPU, mémoire, entrées/sorties disque, réseau. Ce n'est pas une application
en espace utilisateur.

Exécutez ces deux commandes et comparez leur sortie :

```bash
uname -r
```

```bash
uname -a
```

Le premier nombre dans la sortie de `uname -r` (par exemple `6.1.0`) est la version du noyau.
La ligne complète de `uname -a` montre aussi l'architecture (`x86_64`, `aarch64`, etc.) et la date de compilation.

---

## Exercice 2 — Identifier votre distribution

Une **distribution Linux** regroupe le noyau avec un gestionnaire de paquets, des outils
système et une configuration par défaut. Ubuntu, Debian et AlmaLinux sont des distributions
construites sur le même noyau Linux.

```bash
cat /etc/os-release
```

Repérez les champs `NAME`, `VERSION` et `ID`. Sur les systèmes basés sur RHEL, vous pouvez aussi lire :

```bash
cat /etc/redhat-release
```

---

## Exercice 3 — Explorer /etc

`/etc` est l'endroit où vivent les **fichiers de configuration**. Presque chaque service
installé stocke sa configuration sous `/etc`.

```bash
ls /etc | head -20
```

Choisissez 3 entrées que vous reconnaissez et réfléchissez à quel service ou fonction chacune configure.

| Fichier / répertoire | Rôle |
|--------------------|------|
| `/etc/hostname` | Nom de la machine |
| `/etc/hosts` | Correspondances statiques nom d'hôte → IP |
| `/etc/passwd` | Comptes utilisateurs locaux |
| `/etc/fstab` | Table de montage des systèmes de fichiers |
| `/etc/ssh/` | Configuration du serveur et client SSH |

---

## Exercice 4 — Explorer /var/log

`/var/log` stocke les **fichiers de journaux** — la trace écrite de ce que font les programmes.

```bash
ls /var/log
```

Lisez les 10 dernières lignes du journal principal pour voir qu'il est vivant :

```bash
sudo tail -10 /var/log/syslog          # Debian/Ubuntu
sudo tail -10 /var/log/messages        # RHEL/AlmaLinux
```

---

## Exercice 5 — Jeter un œil à /proc

`/proc` n'est pas un vrai répertoire sur le disque. C'est un **système de fichiers virtuel**
créé par le noyau au démarrage. Il expose les structures de données du noyau sous forme de fichiers lisibles.

```bash
ls /proc | head -20
cat /proc/uptime          # secondes écoulées depuis le démarrage
cat /proc/cpuinfo | head -20   # détails du CPU
```

---

## Remplir votre carte des notions

Ouvrez le fichier de réponses préparé pour vous et remplacez chaque `VOTRE_RÉPONSE_ICI`
avec vos propres mots (1 à 3 phrases par question) :

```bash
cat challenge/work/notions.md        # lire le modèle
nano challenge/work/notions.md       # le compléter
```

```bash
dsoxlab check l1-01-discover-linux-map   # valider quand c'est fait
```
