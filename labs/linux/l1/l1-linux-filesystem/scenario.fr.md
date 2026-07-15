# Lab l1-07 — Hiérarchie du système de fichiers Linux (FHS)

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B1) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 20 min |
| **Référence** | [Système de fichiers Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/filesystem/) |

---

## Ce que vous allez apprendre

- Nommer le rôle de chaque répertoire Linux standard de premier niveau
- Localiser les fichiers de configuration, journaux, binaires et périphériques sur n'importe quelle distribution
- Distinguer `/bin`, `/sbin`, `/usr/bin` et `/usr/local/bin`
- Comprendre pourquoi `/tmp` est dangereux pour le stockage long terme
- Classer des fichiers selon leur emplacement FHS correct

---

## La carte FHS

Toutes les distributions Linux suivent le Filesystem Hierarchy Standard (FHS).
La racine `/` est au sommet. Tout le reste se trouve en dessous :

| Répertoire | Rôle |
|------------|------|
| `/bin` | Binaires utilisateur essentiels (ls, cp, cat) |
| `/sbin` | Binaires d'administration système (fdisk, reboot) |
| `/usr` | Hiérarchie secondaire — la plupart des logiciels installés |
| `/usr/bin` | Binaires utilisateur non essentiels |
| `/usr/local/bin` | Binaires compilés/installés localement |
| `/etc` | Fichiers de configuration système |
| `/var` | Données variables : journaux, spools, caches |
| `/var/log` | Fichiers journaux |
| `/tmp` | Fichiers temporaires — effacés au redémarrage |
| `/home` | Répertoires personnels des utilisateurs |
| `/root` | Répertoire personnel de root |
| `/dev` | Fichiers de périphériques (disques, terminaux, null) |
| `/proc` | Système de fichiers virtuel — infos noyau et processus |
| `/sys` | Système de fichiers virtuel — état matériel et noyau |
| `/lib` | Bibliothèques partagées essentielles |
| `/mnt` | Points de montage temporaires |
| `/media` | Supports amovibles (USB, CD) |
| `/boot` | Noyau et fichiers du chargeur de démarrage |
| `/opt` | Logiciels tiers optionnels |
| `/srv` | Données de services (racines web, FTP) |

---

## Exercice 1 — Explorer le premier niveau

```bash
ls /
ls /etc | head -20
ls /var/log | head -10
```

---

## Exercice 2 — Où se trouve-t-il ?

Pour chaque chemin, quel répertoire le contient ?

```bash
ls /etc/hostname
ls /var/log/syslog 2>/dev/null || ls /var/log/messages 2>/dev/null
ls /usr/bin/git 2>/dev/null || which git
ls /dev/null
ls /proc/version
```

---

## Exercice 3 — Classifier les fichiers

Consultez le modèle `fhs.txt`. Pour chaque chemin listé, écrivez le rôle de son
répertoire parent (un ou deux mots, ex : "configuration", "journaux", "binaires utilisateur").

Puis pour chacun des cinq fichiers fictifs, écrivez où il **devrait** se trouver
selon les conventions FHS.

```bash
cat challenge/work/fhs.txt    # lire le modèle
nano challenge/work/fhs.txt   # le remplir
dsoxlab check l1-linux-filesystem
```
