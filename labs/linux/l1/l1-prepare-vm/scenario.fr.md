# Lab l1-03 — Identifier sa machine Linux

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B0) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 15 min |
| **Référence** | [Installer une VM Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/) |

---

## Ce que vous allez apprendre

- Obtenir le nom d'hôte d'une machine Linux
- Identifier la distribution et sa version avec une seule commande
- Lire la version du noyau en cours d'exécution
- Trouver l'adresse IP locale de la machine
- Rédiger une carte d'identité machine réutilisable sur n'importe quel serveur

---

## Référence des commandes

| Commande | Ce qu'elle affiche |
|----------|-------------------|
| `hostname` | Nom d'hôte court |
| `hostname -f` | Nom d'hôte pleinement qualifié (si configuré) |
| `cat /etc/hostname` | Nom d'hôte stocké dans le fichier de configuration |
| `cat /etc/os-release` | Nom, version, identifiant de la distribution |
| `grep PRETTY_NAME /etc/os-release` | Résumé lisible de la distribution sur une ligne |
| `hostnamectl` | Nom d'hôte + OS + noyau (systèmes systemd) |
| `uname -r` | Version du noyau actif |
| `ip addr show` | Toutes les interfaces réseau avec leurs adresses IP |
| `hostname -I` | Toutes les adresses IP locales, séparées par des espaces |
| `ip route` | Table de routage — indique la passerelle par défaut |

---

## Exercice 1 — Nom d'hôte

Le nom d'hôte identifie la machine sur le réseau. Il est stocké dans `/etc/hostname`
et affiché par la commande `hostname`.

```bash
hostname
cat /etc/hostname
```

Notez la différence : `hostname` lit l'état courant du système ; `/etc/hostname` est
le fichier persistant qui le définit au démarrage.

---

## Exercice 2 — Distribution

```bash
cat /etc/os-release
```

Repérez :
- `NAME` — nom court de la distribution (ex. `Ubuntu`, `Debian GNU/Linux`, `AlmaLinux`)
- `VERSION` — la chaîne de version
- `PRETTY_NAME` — une ligne lisible combinant les deux

Plus court :

```bash
grep PRETTY_NAME /etc/os-release
```

---

## Exercice 3 — Version du noyau

```bash
uname -r
```

La version suit le format `MAJEUR.MINEUR.PATCH-extra`.
Exemple : `6.8.0-55-generic`

```bash
uname -a     # ligne complète : noyau + nom d'hôte + date + architecture
```

---

## Exercice 4 — Adresse IP

```bash
hostname -I
```

Affiche toutes les adresses IP configurées sur une ligne.
Si vous avez plusieurs interfaces (loopback, ethernet, Wi-Fi), elles sont toutes présentes.

Pour plus de détails avec les noms d'interfaces :

```bash
ip addr show
```

Cherchez les lignes commençant par `inet ` (IPv4) — l'adresse est la valeur avant le `/`.
Ignorez `127.0.0.1` (loopback) — ce n'est pas une vraie adresse réseau.

---

## Remplir la carte d'identité machine

Ouvrez le modèle et renseignez les quatre champs avec les valeurs réelles de votre système :

```bash
cat challenge/work/vm-info.txt   # lire le modèle
nano challenge/work/vm-info.txt  # le remplir
```

```bash
dsoxlab check l1-prepare-vm
```
