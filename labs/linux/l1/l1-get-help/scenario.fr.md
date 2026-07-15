# Lab l1-06 — Obtenir de l'aide en ligne de commande

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B0) — **Checkpoint** |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 20 min |
| **Référence** | [Terminal Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/terminal/) |

---

## Ce que vous allez apprendre

- Naviguer dans une page `man` pour trouver une option précise
- Utiliser `--help` pour un résumé rapide des options
- Chercher des commandes par mot-clé avec `apropos`
- Lire la section SYNOPSIS pour comprendre la syntaxe
- Trouver la bonne option sans utiliser un moteur de recherche

---

## Les trois outils d'aide

| Outil | Idéal pour |
|-------|-----------|
| `man <commande>` | Référence complète — toutes les options, exemples, codes de retour |
| `<commande> --help` | Résumé rapide — tient souvent sur un écran |
| `apropos <mot-clé>` | Quand vous ne connaissez pas le nom de la commande |
| `whatis <commande>` | Description en une ligne d'une commande |

---

## Exercice 1 — Lire une page man

```bash
man ls
```

Dans `man` :
- Les flèches ou `j`/`k` font défiler ligne par ligne
- `Espace` descend d'une page, `b` remonte
- `/mot` cherche vers l'avant, `n` saute à l'occurrence suivante
- `q` quitte

Trouvez l'option qui affiche les tailles de fichiers en format lisible (Ko, Mo, Go).

```bash
man ls | grep -A1 "human"
```

---

## Exercice 2 — Utiliser --help

```bash
cp --help
```

`--help` affiche un résumé compact. Utilisez `| grep` pour filtrer :

```bash
cp --help | grep -i recursive
```

Trouvez l'option qui copie un répertoire de façon récursive.

---

## Exercice 3 — Chercher avec apropos

Quand vous savez ce que vous voulez faire mais pas quelle commande :

```bash
apropos "copy files"
apropos "disk space"
apropos "show running processes"
```

Chaque résultat affiche `commande (section) — description`.
Sections : 1 = commandes utilisateur, 5 = fichiers de config, 8 = commandes admin.

---

## Exercice 4 — Trouver la bonne option

Utilisez `man`, `--help` ou `apropos` pour répondre aux trois questions dans `aide.txt`.

**N'utilisez pas le web.** Servez-vous uniquement des outils d'aide intégrés.

```bash
cat challenge/work/aide.txt    # lire les questions
nano challenge/work/aide.txt   # remplir les réponses
```

Ensuite validez :

```bash
dsoxlab check l1-get-help
```
