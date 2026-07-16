# Drill — commandes essentielles

**Format** : 5 tâches, 100 points, 20 minutes. **Aucun indice.**

Jouable sur **l'une ou l'autre distribution** — ces commandes sont identiques
sur RHEL et Debian :

```bash
dsoxlab check drill-essential-commands                  # AlmaLinux (défaut)
dsoxlab check drill-essential-commands --target ubuntu  # Ubuntu
```

---

### Tâche 1 — Archiver par taille (25 pts)

Sous `/srv/drill/data/`, crée **`/root/big.tar.gz`** (tar gzip) contenant tous
les fichiers de **plus de 1 Mio**, et rien d'autre. Le critère est la
**taille**, pas le nom.

### Tâche 2 — Qui est le plus actif ? (20 pts)

`/srv/drill/access.csv` a le format `date,niveau,utilisateur,message`. Écris
dans **`/root/top-user.txt`** le **nom seul** de l'utilisateur qui totalise le
plus de lignes.

### Tâche 3 — Liens (15 pts)

Pour `/srv/drill/access.csv`, crée un **lien physique** en `/root/access.hard`
et un **lien symbolique** en `/root/access.soft`.

### Tâche 4 — Rapport confidentiel (20 pts)

`/srv/drill/report.txt` est en `root:root` `0644` — tout le monde peut le lire.
Fais-le appartenir à **`drilluser:drillers`** en **`0640`**.

### Tâche 5 — Séparer les flux (20 pts)

`/usr/local/bin/noisy.sh` écrit sur **les deux** flux, stdout et stderr. Lance-le
de façon que sa sortie standard atterrisse dans **`/root/out.log`** et sa sortie
d'erreur dans **`/root/err.log`** — chaque fichier ne contenant que son flux.

---

## Valider

```bash
dsoxlab check drill-essential-commands
```
