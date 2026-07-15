# Lab l1-04 — Premiers pas dans le terminal

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B0) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 15 min |
| **Référence** | [Terminal Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/terminal/) |

---

## Ce que vous allez apprendre

- Identifier l'utilisateur courant avec `whoami`
- Afficher le répertoire personnel via une variable d'environnement
- Afficher l'heure et la date courantes
- Rediriger la sortie d'une commande dans un fichier avec `>`
- Ajouter du contenu à un fichier existant avec `>>`

---

## Référence des commandes

| Commande | Ce qu'elle fait |
|----------|----------------|
| `whoami` | Affiche l'utilisateur courant |
| `hostname` | Affiche le nom de la machine |
| `echo $HOME` | Affiche le répertoire personnel (variable d'environnement) |
| `date` | Affiche la date et l'heure complètes |
| `echo "texte" > fichier.txt` | Écrit dans un fichier (écrase si existant) |
| `echo "texte" >> fichier.txt` | Ajoute à un fichier (sans écraser) |
| `cat fichier.txt` | Affiche le contenu d'un fichier |

---

## Exercice 1 — Qui suis-je ?

```bash
whoami
```

Cette commande affiche le nom de l'utilisateur actuellement connecté.
Sur un serveur partagé vous n'êtes pas toujours le même utilisateur — c'est un réflexe de base.

```bash
id
```

`id` affiche votre identifiant utilisateur (uid), le groupe principal (gid) et tous les groupes supplémentaires.

---

## Exercice 2 — Où suis-je ?

```bash
hostname
echo $HOME
pwd
```

`$HOME` est une **variable d'environnement** : une valeur nommée conservée par le shell.
Elle contient toujours le chemin vers votre répertoire personnel.

```bash
echo $USER    # identique à whoami mais via la variable d'environnement
env           # afficher toutes les variables d'environnement
```

---

## Exercice 3 — Quelle heure est-il ?

```bash
date
date +"%Y-%m-%d"          # date ISO seulement
date +"%H:%M:%S"          # heure seulement
date +"%Y-%m-%d %H:%M"    # combiné
```

---

## Exercice 4 — Écrire la sortie dans un fichier

L'opérateur `>` redirige ce qu'une commande affiche vers un fichier au lieu de l'écran.
Si le fichier existe déjà, il est **écrasé**.

```bash
echo "quelque chose" > premiers-pas.txt
cat premiers-pas.txt
```

L'opérateur `>>` **ajoute** au fichier sans écraser :

```bash
echo "première ligne" > premiers-pas.txt
echo "deuxième ligne" >> premiers-pas.txt
cat premiers-pas.txt
```

---

## Remplir le modèle

Ouvrez le modèle et capturez les vraies valeurs de votre machine :

```bash
cat challenge/work/premiers-pas.txt   # lire le modèle
nano challenge/work/premiers-pas.txt  # le remplir
```

Ensuite validez :

```bash
dsoxlab check l1-first-terminal
```
