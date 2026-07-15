# Lab l1-02 — Choisir sa distribution Linux de référence

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B0) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 15 min |
| **Référence** | [Choisir sa distribution Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions/) |

---

## Ce que vous allez apprendre

À la fin de ce lab vous saurez :

- Nommer les deux grandes familles de distributions Linux et leurs gestionnaires de paquets
- Décrire au moins deux critères pour choisir une distribution
- Associer une distribution à un cas d'usage : apprentissage, certification, serveur perso
- Expliquer pourquoi le choix de la distribution est important au début du parcours Linux

---

## Les deux grandes familles

### Famille Debian / Ubuntu

| Critère | Debian | Ubuntu LTS |
|---------|--------|------------|
| Gestionnaire de paquets | `apt` / `.deb` | `apt` / `.deb` |
| Cycle de sortie | ~2 ans (très stable) | 2 ans LTS (5 ans de support) |
| Cible | Serveurs, utilisateurs avancés | Débutants, postes de travail, serveurs |
| Certifications cibles | Linux général | Linux général |

Commandes clés :

```bash
apt search <paquet>
apt install <paquet>
apt update && apt upgrade
```

### Famille RHEL (Red Hat Enterprise Linux)

| Critère | AlmaLinux / Rocky Linux | RHEL |
|---------|------------------------|------|
| Gestionnaire de paquets | `dnf` / `.rpm` | `dnf` / `.rpm` |
| Cycle de sortie | ~5 ans (aligné RHEL) | ~5 ans |
| Cible | Serveurs, entreprise, préparation certif | Production entreprise |
| Certifications cibles | **RHCSA**, **RHCE** | **RHCSA**, **RHCE** |

Commandes clés :

```bash
dnf search <paquet>
dnf install <paquet>
dnf check-update && dnf update
```

---

## Trois scénarios — quelle distribution ?

Lisez chaque scénario. Puis remplissez `choix-distro.txt` avec votre choix et une justification.

Il n'y a pas de réponse unique correcte. Ce qui compte, c'est votre raisonnement.

---

### Scénario A — Débutant complet

> Vous n'avez jamais utilisé Linux. Vous voulez apprendre les bases : le terminal,
> les fichiers, les utilisateurs, les services. Vous avez un PC de rechange.
> Vous suivrez principalement des tutoriels trouvés sur le web.

**Réfléchissez à :**
- Quelle distribution a la documentation la plus accessible aux débutants ?
- Laquelle est le plus souvent couverte dans les tutoriels que vous trouverez ?
- Quel gestionnaire de paquets est plus facile à découvrir en premier ?

---

### Scénario B — Préparation RHCSA

> Vous voulez passer l'examen RHCSA (EX200) dans 6 mois.
> Vous avez besoin d'un environnement de labo gratuit qui se comporte exactement comme RHEL.

**Réfléchissez à :**
- Quelles distributions sont des reconstructions binaires compatibles avec RHEL ?
- Le gestionnaire de paquets compte-t-il pour l'examen ?
- La version (RHEL 9, RHEL 10) compte-t-elle ?

---

### Scénario C — Serveur perso de test

> Vous avez une petite VM ou un Raspberry Pi. Vous voulez héberger quelques services :
> serveur web, base de données, reverse proxy. Le serveur doit être stable et peu contraignant.

**Réfléchissez à :**
- Quelle distribution privilégie la stabilité plutôt que les dernières fonctionnalités ?
- Quelle est la durée de la fenêtre de support ?
- Avez-vous besoin d'un support commercial ?

---

## Remplir votre fichier de réponses

```bash
cat challenge/work/choix-distro.txt        # lire le modèle
nano challenge/work/choix-distro.txt       # le compléter
```

```bash
dsoxlab check l1-choose-distro   # valider quand c'est fait
```
