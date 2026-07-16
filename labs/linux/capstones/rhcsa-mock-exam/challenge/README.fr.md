# Capstone RHCSA — Examen blanc EX200

**Format** : 20 tâches, 100 points, 2 VMs, 180 minutes.
**Score de passage** : 70/100. **Aucun indice** ne sera révélé.

## Vos 2 machines

| Hôte | IP initiale | Rôle |
|---|---|---|
| `alma-rhcsa-1.lab` | DHCP (variable) | Serveur principal — 16 tâches |
| `alma-rhcsa-2.lab` | DHCP (variable) | Client — 4 tâches dépendantes du serveur |

Connectez-vous via `dsoxlab ssh alma-rhcsa-1.lab` (ou `alma-rhcsa-2.lab` pour le client). Vous êtes `student` avec sudo NOPASSWD.

Les changements doivent être **persistants après reboot**. Une configuration qui marche après `reboot` mais a été appliquée uniquement par commande live (sans persistance) ne compte pas.

---

## Section A — Stockage et systèmes de fichiers

### Tâche 1 — Partitionner le disque additionnel (4 pts)

Le disque `/dev/vdb` (10 GiB) est attaché à `alma-rhcsa-1`. Créez une table GPT et 2 partitions :

- `/dev/vdb1` : 4 GiB, label `lvm-data`
- `/dev/vdb2` : 4 GiB, label `swap-extra`

### Tâche 2 — Créer LVM et monter `/data` (6 pts)

Sur `/dev/vdb1` :

- Créez un volume group `vgapp`
- Créez un logical volume `lvdata` de **3 GiB**
- Formatez en **XFS**
- Montez sur `/data` au boot via **UUID** (pas par chemin de device)

### Tâche 3 — Étendre `lvdata` à 3.5 GiB en ligne (5 pts)

Étendez `lvdata` à **3.5 GiB**. Le système de fichiers XFS doit refléter la nouvelle taille **sans démontage** ni reboot.

### Tâche 4 — Swap file de 512 MiB (4 pts)

Créez `/swapfile` de 512 MiB activé en swap, persistant au boot. Le swap total (`free -m`) doit augmenter de ~512 MiB.

### Tâche 5 — Exporter `/data/share` via NFS (6 pts)

Sur `alma-rhcsa-1` :

- Créez `/data/share` (mode 0775, owner root, group `developers` — voir tâche 7)
- Exportez via NFS en **lecture/écriture** uniquement pour `alma-rhcsa-2.lab`
- Ouvrez les ports nécessaires dans `firewalld` (zone publique, **permanent**)
- Le service `nfs-server` doit être actif et activé au boot

---

## Section B — Utilisateurs, groupes, permissions

### Tâche 6 — User `appuser` avec password aging (5 pts)

Créez le compte `appuser` :

- UID exactement **1500**
- Shell `/bin/bash`
- Password aging : expiration tous les **60 jours**, warning **7 jours** avant
- Pas de password initial (login par clé uniquement)

### Tâche 7 — Groupe `developers` partagé (5 pts)

Créez le groupe `developers` GID 2000.

- Créez le user `devuser` (UID auto), ajoutez `devuser` et `appuser` au groupe `developers`
- Créez `/srv/shared` avec :
  - Owner `root`, group `developers`
  - Permissions `2775` (setgid actif → tout fichier créé hérite du groupe)
  - Tout user du groupe peut écrire et tout le monde peut lire

### Tâche 8 — ACL POSIX sur `/var/log/myapp.log` (4 pts)

Le fichier `/var/log/myapp.log` existe (root:root, mode 0600). Donnez à `appuser` les droits **rwx** via une ACL POSIX **sans modifier** le owner/group/mode standard du fichier.

`getfacl /var/log/myapp.log` doit montrer la ligne `user:appuser:rwx`.

---

## Section C — Réseau

### Tâche 9 — IP statique + hostname + port firewalld sur `srv-1` (6 pts)

Sur `alma-rhcsa-1` :

- **Fige la configuration réseau** : la connexion de gestion est encore en DHCP.
  Convertis-la en configuration **statique permanente** (`manual`) — **en
  conservant l'adresse que la machine porte déjà** — en déclarant son adresse,
  la passerelle **`10.10.30.1`** et le DNS du réseau **`10.10.30.1`**. Ça doit survivre à un
  reboot.

  > Garde l'adresse que tu as. La changer coupe ton propre accès — et celui du
  > correcteur. Sur un vrai serveur, on fige ce qui est déjà là ; ici c'est le
  > même geste, et le même piège : un `nmcli con mod` jamais appliqué, ou un
  > `ip addr` tapé à la main, ne survit pas.
- Hostname permanent **`srv-rhcsa-1.lab`**
- Ouvrez le port **8080/tcp** dans firewalld zone publique, permanent

### Tâche 17 — Configuration réseau client `srv-2` (4 pts)

Sur `alma-rhcsa-2` :

- **Fige la configuration réseau** en statique permanent (`manual`), en
  conservant l'adresse que la machine porte déjà, avec la passerelle **`10.10.30.1`** et le DNS du réseau **`10.10.30.1`**
- Hostname permanent **`srv-rhcsa-2.lab`**

---

## Section D — Services et planification

### Tâche 10 — Unit systemd `myapp.service` (5 pts)

Sur `alma-rhcsa-1`, créez `/usr/local/bin/myapp.sh` (script qui boucle indéfiniment, fournit `/usr/local/bin/myapp.sh` shebang bash + `while true; do sleep 30; done`).

Créez l'unit `myapp.service` :

- `Type=simple`
- `ExecStart=/usr/local/bin/myapp.sh`
- `Restart=on-failure`
- `User=appuser`
- Démarrage **automatique au boot**
- Le service doit être actif (running) au moment de la validation

### Tâche 11 — Systemd timer `weekly-backup.timer` (4 pts)

Sur `alma-rhcsa-1`, créez :

- `weekly-backup.service` qui exécute `/usr/local/bin/weekly-backup.sh` (vous fournissez ce script ; il peut juste faire `date >> /var/log/backup.log`)
- `weekly-backup.timer` qui déclenche le service tous les **dimanches à 03:00**, persistant
- Le timer doit être **actif** et **activé au boot**

### Tâche 12 — Chrony serveur sur `srv-1` (4 pts)

Configurez chrony sur `alma-rhcsa-1` pour :

- Se synchroniser avec **`pool.ntp.org` iburst**
- **Autoriser `alma-rhcsa-2.lab`** à interroger ce serveur (`allow <adresse de srv-2>`)
- Service actif et activé au boot

---

## Section E — SELinux et sécurité

### Tâche 13 — Restorecon `/var/www/html/index.html` (4 pts)

Sur `alma-rhcsa-1`, le fichier `/var/www/html/index.html` existe mais a un contexte SELinux incorrect. Restaurez-le au contexte standard pour qu'`httpd_t` puisse le lire (`httpd_sys_content_t`).

### Tâche 14 — Boolean SELinux `httpd_can_network_connect` (3 pts)

Activez le boolean SELinux `httpd_can_network_connect` de manière **permanente** (persistant après reboot).

### Tâche 15 — Étiquette de port SELinux 8888/tcp (3 pts)

Ajoutez l'étiquette SELinux **`http_port_t`** sur le port **8888/tcp**, permanent.

`semanage port -l | grep http_port_t` doit lister 8888.

### Tâche 19 — SSH key-only `srv-2 → srv-1/appuser` (7 pts)

Sur `alma-rhcsa-2` :

- Générez une clé ed25519 dans `~/.ssh/id_ed25519` (NoPass) pour `appuser` (le user existe déjà après tâche 6 si vous l'avez créé sur `srv-2` aussi, sinon créez-le localement avec UID 1500)
- Déposez la clé publique dans `appuser@alma-rhcsa-1.lab:~/.ssh/authorized_keys`
- `ssh appuser@<srv-1> hostname` depuis `srv-2` doit retourner `srv-rhcsa-1.lab` **sans password prompt**
- Désactivez **`PasswordAuthentication no`** dans `/etc/ssh/sshd_config` sur `alma-rhcsa-2` (permanent, recharger sshd)

---

## Section F — Stockage réseau client

### Tâche 18 — Mount NFS au boot sur `srv-2` (6 pts)

Sur `alma-rhcsa-2`, montez le partage NFS exposé par `srv-1` (tâche 5) :

- Mount point : `/mnt/share`
- Source : `alma-rhcsa-1.lab:/data/share`
- Persistant au boot via `/etc/fstab` avec `_netdev` (et idéalement `nofail` pour ne pas bloquer le boot si le serveur est down)

`mountpoint /mnt/share` doit retourner `is a mountpoint` et le contenu doit être lisible.

---

## Section G — Logiciel et boot

### Tâche 16 — Installer `tree` via DNF + Flatpak `org.gnome.Calculator` (5 pts)

Sur `alma-rhcsa-1` :

- Installez le paquet **`tree`** via `dnf` (depuis EPEL si pas dans les repos par défaut — activez le repo `epel-release` si nécessaire)
- Configurez l'accès au repo Flatpak **`flathub`**
- Installez **`org.gnome.Calculator`** depuis Flathub (system-wide, pas user)

### Tâche 20 — Reset password root sur `srv-2` via rd.break (6 pts)

Le password root sur `alma-rhcsa-2` est **inconnu** (votre setup l'a randomisé). Vous devez le reset via la procédure RHCSA standard :

1. Reboot la VM
2. Interrompre GRUB (touche `e` au menu)
3. Ajouter `rd.break` à la ligne `linux …`
4. Démarrer (Ctrl+X)
5. `mount -o remount,rw /sysroot`
6. `chroot /sysroot`
7. `passwd root` → définir comme nouveau password : **`SecureP@ss2026!`**
8. `touch /.autorelabel` (sinon SELinux bloque le password file après reboot)
9. Sortir, reboot

Validation : `ssh root@alma-rhcsa-2.lab` (depuis `alma-rhcsa-1` ou local) avec le nouveau password doit fonctionner.

---

## Conseils stratégiques

- **Ordre** : commencez par les tâches **persistantes au boot** (1-9, 17) puis les services. Le reset root (tâche 20) en **dernier** car il nécessite 2 reboots.
- **Pas de bricolage live** : tout doit être configuré pour persister au reboot. Si vous avez modifié `/etc/sshd_config`, faites `systemctl restart sshd` ; si vous avez modifié `firewalld`, ajoutez `--permanent` puis `--reload`.
- **Vérification finale** : reboot les 2 VMs avant `dsoxlab check` pour confirmer la persistance.
- **Pas d'aide internet** : les tests `dsoxlab check` valident **l'état observable**, pas le chemin pris. man, `--help`, `/usr/share/doc/` sont vos seuls amis.

---

## Validation

```bash
dsoxlab check rhcsa-mock-exam       # affiche le score temps réel (sans le sauvegarder)
dsoxlab submit rhcsa-mock-exam       # soumission finale, enregistre dans l'historique
```

Le score affiche la pondération de chaque tâche réussie. **70/100 = succès**.
