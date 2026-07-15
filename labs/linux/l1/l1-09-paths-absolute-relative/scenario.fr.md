# Lab l1-09 — Chemins absolus et relatifs

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B1) — **Checkpoint** |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 25 min |
| **Référence** | [Système de fichiers Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/filesystem/) |

---

## Ce que vous allez apprendre

- Distinguer visuellement un chemin absolu d'un chemin relatif
- Copier un fichier avec un chemin absolu
- Copier un fichier avec un chemin relatif depuis un autre répertoire
- Calculer mentalement le résultat d'une navigation avec `..`
- Résoudre des puzzles de chemins sans exécuter un shell

---

## Concepts clés

### Chemin absolu

Commence par `/`. Toujours correct peu importe où vous êtes.

```
/home/bob/docs/rapport.txt
/etc/nginx/nginx.conf
```

### Chemin relatif

Part du **répertoire courant**. Dépend de l'endroit où vous vous trouvez.

```
docs/rapport.txt      (relatif à /home/bob/ si vous y êtes)
../bob/docs/          (monter d'un niveau, puis descendre)
./script.sh          (répertoire courant explicitement)
```

---

## Validation

```bash
dsoxlab check l1-09-paths-absolute-relative
```
