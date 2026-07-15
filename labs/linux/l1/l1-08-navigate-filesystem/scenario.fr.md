# Lab l1-08 — Naviguer dans le système de fichiers

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B1) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 30 min |
| **Référence** | [Système de fichiers Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/filesystem/) |

---

## Ce que vous allez apprendre

- Naviguer dans les répertoires avec `cd`, `pwd` et `ls`
- Créer une arborescence avec `mkdir -p`
- Copier des fichiers avec `cp` et des répertoires avec `cp -r`
- Déplacer et renommer des fichiers avec `mv`
- Supprimer des fichiers et répertoires avec `rm` et `rm -r`
- Vérifier l'arborescence construite avec `tree` ou `find`

---

## Référence des commandes

| Commande | Ce qu'elle fait |
|----------|----------------|
| `pwd` | Affiche le répertoire courant |
| `cd <rép>` | Change de répertoire |
| `cd ..` | Monte d'un niveau |
| `cd -` | Retourne au répertoire précédent |
| `ls -la` | Liste les fichiers avec détails et fichiers cachés |
| `mkdir rép` | Crée un répertoire |
| `mkdir -p a/b/c` | Crée une arborescence imbriquée d'un coup |
| `cp fichier dest` | Copie un fichier |
| `cp -r rép dest` | Copie un répertoire récursivement |
| `mv src dest` | Déplace ou renomme |
| `rm fichier` | Supprime un fichier |
| `rm -r rép` | Supprime un répertoire et son contenu |
| `rmdir rép` | Supprime un répertoire vide |
| `tree` | Affiche l'arborescence (si installé) |
| `find . -type f` | Liste tous les fichiers récursivement |

---

## Structure cible

Votre objectif : construire cette arborescence dans `challenge/work/projet/` :

```
projet/
├── src/
│   ├── app.py
│   └── utils.py
├── tests/
│   └── test_app.py
├── docs/
│   └── README.txt
└── config/
    └── settings.conf
```

---

## Validation

```bash
dsoxlab check l1-08-navigate-filesystem
```
