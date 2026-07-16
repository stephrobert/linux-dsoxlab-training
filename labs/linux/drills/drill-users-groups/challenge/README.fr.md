# Drill — utilisateurs, groupes et délégation

**Format** : 5 tâches, 100 points, 20 minutes. **Aucun indice.**

```bash
dsoxlab check drill-users-groups                  # AlmaLinux (défaut)
dsoxlab check drill-users-groups --target ubuntu  # Ubuntu
```

---

### Tâche 1 — Un compte aux specs (20 pts)

Crée **`deploy`** : UID **`4200`**, shell de connexion **`/bin/bash`**, membre
du groupe supplémentaire **`ops`**.

### Tâche 2 — Vieillissement du mot de passe (20 pts)

Sur le compte **`intern`** : le mot de passe doit expirer au bout de **30 jours**
maximum, avec un **avertissement 7 jours** avant, et le **compte** lui-même doit
expirer le **2027-01-01**.

### Tâche 3 — Répertoire collaboratif (20 pts)

**`/srv/ops`** doit appartenir au groupe **`ops`** en mode **`2770`** : les
fichiers créés dedans héritent du groupe, et *les autres* n'ont rien.

### Tâche 4 — Déléguer sudo, au plus juste (20 pts)

Les membres d'**`ops`** doivent pouvoir lancer **`/usr/local/bin/ops-report.sh`**
en root **sans mot de passe** — et rien de plus.

### Tâche 5 — Un départ (20 pts)

**`former`** s'en va. Verrouille le compte : son mot de passe doit être
**verrouillé**, et son shell doit **interdire la connexion**. Verrouiller le mot
de passe ne suffit pas — une clé SSH passerait encore.

---

## Valider

```bash
dsoxlab check drill-users-groups
```
