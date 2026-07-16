# Drill — partitions, LVM et swap

**Format** : 5 tâches, 100 points, 25 minutes. **Aucun indice.**
Le disque **`/dev/vdb`** est attaché et **vierge**.

```bash
dsoxlab check drill-storage                  # AlmaLinux (défaut)
dsoxlab check drill-storage --target ubuntu  # Ubuntu
```

---

### Tâche 1 — Partitionner (20 pts)

Sur `/dev/vdb`, crée une table **GPT** et deux partitions : **`/dev/vdb1` de
2 Gio** et **`/dev/vdb2` de 1 Gio**.

### Tâche 2 — La pile LVM (20 pts)

Fais de `/dev/vdb1` un volume physique, dans le groupe de volumes **`vgdrill`**.
Crée le volume logique **`lvdata`** de **1 Gio**, formaté en **XFS**.

### Tâche 3 — Montage persistant (20 pts)

Monte `lvdata` sur **`/mnt/data`**, de façon persistante, **par UUID** — pas par
chemin de device.

### Tâche 4 — Swap (20 pts)

Ajoute **128 Mio** de swap sous forme du fichier **`/swapfile`**, actif et
persistant.

### Tâche 5 — Étendre à chaud (20 pts)

Étends **`lvdata` à 1,5 Gio**. Le système de fichiers doit refléter la nouvelle
taille **sans démontage** — un volume étendu dont le système de fichiers n'a pas
suivi ne donne aucun espace utilisable.

---

## Valider

```bash
dsoxlab check drill-storage
```
