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

### Tâche 1 — Mettre `/srv/deploiement` sous Git (5 pts)

Le répertoire `/srv/deploiement` contient deux fichiers de travail et un
sous-répertoire `.cache/` qui ne doit jamais être versionné.

- Initialise un dépôt Git **dans `/srv/deploiement`**
- `config.yml` et `notes.txt` sont **suivis et commités**
- `.cache/` est **ignoré** : `git status` ne doit plus le mentionner
- Crée une branche **`recette`**, sans y basculer obligatoirement

### Tâche 2 — Réparer `collecteur.service` (6 pts)

Le service `collecteur.service` est installé mais refuse de démarrer. Le script
qu'il doit lancer, `/usr/local/bin/collecteur.sh`, est correct : **ne le
réécris pas**, il y a deux défauts ailleurs.

- `systemctl start collecteur` doit réussir
- Le service doit être **actif** et **activé au boot**
- `/var/log/collecteur.log` doit se remplir

### Tâche 3 — Retrouver l'espace disque disparu (4 pts)

`df` annonce plusieurs centaines de mégaoctets occupés sous `/var` que `du` ne
retrouve pas. Un processus retient un fichier **supprimé mais toujours ouvert**.

- Écris dans **`/root/diskspace.txt`** le **nom de l'unité systemd** responsable
  (une ligne, le nom seul suffit)
- **Libère l'espace** : cette unité ne doit plus tourner, ni revenir au boot

### Tâche 4 — Certificat auto-signé (5 pts)

Produis un certificat pour le collecteur, dans `/etc/ssl/lab/` :

- Clé privée **`/etc/ssl/lab/collecteur.key`**, lisible **par root seul**
- Certificat **`/etc/ssl/lab/collecteur.crt`**, auto-signé par cette clé
- **CN = `collecteur.lab`**
- Valide **au moins 365 jours** à compter d'aujourd'hui

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

### Tâche 10 — Ouvrir `/srv/rapports` par ACL (5 pts)

`/srv/rapports` appartient à `root:root` en mode `0750` : l'utilisateur
`devops` n'y a aucun accès. Ouvre-lui la porte **sans changer le propriétaire
ni le groupe**, et **sans ouvrir quoi que ce soit au reste du monde**. Un
`chmod` qui donnerait l'accès à tous ne compte pas.

- `devops` obtient **`rwx`** sur `/srv/rapports`
- `devops` obtient **`rw`** sur le fichier `bilan.csv` déjà présent
- Tout **nouveau** fichier créé dans ce répertoire doit lui accorder **`rw`**
  automatiquement, sans intervention

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

### Tâche 16 — Automontage à la demande (7 pts)

Crée une seconde partition **`/dev/vdb2`** de **1 Gio** formatée en **XFS**,
puis fais-la monter **à la demande** par l'automonteur.

- Le point de montage est **`/mnt/auto/donnees`**
- Il ne doit **pas** apparaître dans `/etc/fstab` : c'est `autofs` qui le monte
- Un simple `ls /mnt/auto/donnees` déclenche le montage
- Le service `autofs` est **actif et activé au boot**

### Tâche 17 — Swap (5 pts)

Ajoute **256 Mio** de swap sous forme de **fichier** `/swapfile`, actif et
persistant au boot. Le swap total doit croître d'environ 256 Mio.

---

## Valider

```bash
dsoxlab check lfcs-mock-exam
```
