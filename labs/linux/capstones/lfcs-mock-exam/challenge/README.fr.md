# Capstone LFCS — examen blanc

**Format** : 17 tâches, 100 points, 1 VM, 120 minutes.
**Score de réussite** : 70/100. **Aucun indice** ne sera révélé.

## Ta machine

| Hôte | Rôle |
|---|---|
| `ubuntu-lfcs-1.lab` | Ubuntu 24.04 — les 17 tâches |

Connexion : `dsoxlab ssh ubuntu-lfcs-1.lab`. Tu es `student` avec sudo NOPASSWD.

Les changements doivent être **persistants après reboot**. Une configuration qui
marche à l'instant mais n'a été appliquée qu'en commande live (sans persistance)
ne compte pas.

**Ne touche jamais à l'interface de gestion** — celle qui porte ta route par défaut. Les tâches réseau
utilisent l'interface dédiée `lab0`. Le disque `/dev/vdb` (5 Gio) est attaché et
vierge.

---

## Section A — Essential Commands (20 pts)

### Tâche 1 — Chercher et archiver (5 pts)

Sous `/srv/audit/`, des fichiers sont éparpillés dans des sous-répertoires. Crée
l'archive **`/root/logs.tar.gz`** (tar compressé gzip) contenant **tous les
fichiers dont le nom se termine par `.log`** trouvés n'importe où sous
`/srv/audit/`, et rien d'autre.

### Tâche 2 — Extraire un rapport (5 pts)

Le fichier `/srv/audit/access.log` mélange plusieurs niveaux. Écris dans
**`/root/errors.txt`** uniquement les lignes contenant `ERROR`, dans leur ordre
d'origine. Aucune autre ligne.

### Tâche 3 — Liens (4 pts)

Pour le fichier `/srv/audit/access.log`, crée :

- un **lien physique** en `/root/access.hard`
- un **lien symbolique** en `/root/access.soft`

### Tâche 4 — Répertoire collaboratif (6 pts)

Le groupe `auditors` doit partager `/srv/shared` :

- groupe propriétaire `auditors`, mode `2770`
- tout nouveau fichier créé dedans hérite du groupe `auditors`

---

## Section B — Operations Deployment (25 pts)

### Tâche 5 — Installer et geler un paquet (5 pts)

Installe **`tree`** et mets-le en **hold** pour qu'aucune mise à jour ne puisse
le bouger.

### Tâche 6 — Une unité de service (7 pts)

Crée le service systemd **`labwatch.service`** qui exécute
`/usr/local/bin/labwatch.sh` (déjà fourni, exécutable). Il doit être **activé**
et **démarré**, et revenir après un reboot.

### Tâche 7 — Un timer (7 pts)

Crée le timer systemd **`labreport.timer`** qui déclenche `labreport.service`
**tous les jours à 03:00**. L'unité `labreport.service` doit exécuter
`/usr/local/bin/labreport.sh` (déjà fourni). Le timer doit être **activé** et
**actif**.

### Tâche 8 — Une tâche cron (6 pts)

Pour l'utilisateur **`devops`**, planifie via **cron** la commande
`/usr/local/bin/labreport.sh` **toutes les 10 minutes**.

---

## Section C — Users and Groups (10 pts)

### Tâche 9 — Créer un compte (5 pts)

Crée l'utilisateur **`auditor1`** :

- UID **`3001`**
- shell de connexion **`/bin/bash`**
- membre du groupe supplémentaire **`auditors`**

### Tâche 10 — Déléguer sudo (5 pts)

Les membres du groupe **`auditors`** doivent pouvoir exécuter **uniquement**
`/usr/bin/systemctl status *` en root, **sans mot de passe**. Déclare-le dans un
fichier sous `/etc/sudoers.d/`.

---

## Section D — Networking (25 pts)

### Tâche 11 — IP statique (8 pts)

Sur l'interface dédiée **`lab0`** (dummy), déclare avec **netplan** l'adresse
statique **`198.51.100.10/24`**. Elle doit être active et persistante.

### Tâche 12 — Route statique (5 pts)

Toujours avec netplan, ajoute une route statique vers **`203.0.113.0/24` via
`198.51.100.1`**.

### Tâche 13 — Pare-feu (7 pts)

Avec **ufw** : autorise **`8080/tcp`**, et active le pare-feu. SSH (`OpenSSH`)
doit rester autorisé — si tu te verrouilles dehors, tu perds les tâches
restantes.

### Tâche 14 — Résolution de noms (5 pts)

Fais en sorte que le nom **`lab-target.lab`** résolve localement vers
**`198.51.100.10`**, sans aucun serveur DNS.

---

## Section E — Storage (20 pts)

### Tâche 15 — LVM et montage persistant (8 pts)

Sur `/dev/vdb` :

- crée une partition `/dev/vdb1` de **2 Gio**
- fais-en un volume physique LVM, dans le groupe de volumes **`vgdata`**
- crée le volume logique **`lvapp`** de **1 Gio**, formaté en **XFS**
- monte-le sur **`/data`** au boot, **par UUID** (pas par chemin de device)

### Tâche 16 — Quota (7 pts)

Sur une seconde partition `/dev/vdb2` de **1 Gio**, formatée en **XFS** et montée
sur **`/srv/quota`** de façon persistante avec les **quotas utilisateur**
activés : impose à l'utilisateur `devops` un quota de blocs de **20M souple /
30M dur**.

### Tâche 17 — Swap (5 pts)

Ajoute **256 Mio** de swap sous forme de **fichier** `/swapfile`, actif et
persistant au boot. Le swap total doit croître d'environ 256 Mio.

---

## Valider

```bash
dsoxlab check lfcs-mock-exam
```
