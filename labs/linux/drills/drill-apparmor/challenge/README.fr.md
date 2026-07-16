# Drill — AppArmor

**Format** : 4 tâches, 100 points, 15 minutes. **Aucun indice.**

Trois profils sont actuellement dans le mauvais mode.

```bash
dsoxlab check drill-apparmor
```

---

### Tâche 1 — AppArmor tourne (25 pts)

Le service **`apparmor`** doit être **activé**, et des profils doivent être
chargés.

### Tâche 2 — ping, sous surveillance (25 pts)

Le profil **`ping`** doit être en mode **complain** : il journalise les
violations sans les bloquer.

### Tâche 3 — man, appliqué (25 pts)

Le profil **`man`** doit être en mode **enforce**.

### Tâche 4 — tcpdump, appliqué (25 pts)

Le profil **`tcpdump`** doit être en mode **enforce**.

---

## Valider

```bash
dsoxlab check drill-apparmor
```
