# Drill — gestion des paquets

**Format** : 5 tâches, 100 points, 20 minutes. **Aucun indice.**

Le sujet **ne nomme pas l'outil** : emploie celui de ta distribution.
L'objectif est le même pour RHCSA et LFCS.

```bash
dsoxlab check drill-packages                  # AlmaLinux — dnf
dsoxlab check drill-packages --target ubuntu  # Ubuntu — apt
```

---

### Tâche 1 — Installer (20 pts)

Le paquet **`tree`** doit être installé.

### Tâche 2 — Le geler (20 pts)

**`tree`** doit être **gelé** : aucune mise à jour ne doit pouvoir le bouger,
même une montée de version complète du système.

### Tâche 3 — À qui appartient ce fichier ? (20 pts)

Trouve quel **paquet fournit `/usr/bin/ssh`**, et écris son **nom seul** dans
**`/root/owner.txt`**.

### Tâche 4 — Qu'a-t-il installé ? (20 pts)

Écris dans **`/root/tree-files.txt`** la liste des fichiers installés par le
paquet **`tree`**.

### Tâche 5 — Supprimer (20 pts)

Le paquet **`nano`** ne doit plus être installé.

---

## Valider

```bash
dsoxlab check drill-packages
```
