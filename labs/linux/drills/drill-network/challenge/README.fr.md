# Drill — réseau statique

**Format** : 4 tâches, 100 points, 20 minutes. **Aucun indice.**

Tout se passe sur l'**interface dédiée `lab0`** (dummy).

> **Ne touche jamais à l'interface de gestion** — celle qui porte ta route par
> défaut. Coupe-la et tu perds la machine, et le drill avec.

Le sujet **ne nomme pas l'outil** : emploie celui de ta distribution.

```bash
dsoxlab check drill-network                  # AlmaLinux — nmcli
dsoxlab check drill-network --target ubuntu  # Ubuntu — netplan
```

---

### Tâche 1 — Une adresse statique (25 pts)

**`lab0`** doit porter **`203.0.113.20/24`**.

### Tâche 2 — Une route statique (25 pts)

Une route vers **`192.0.2.0/24` via `203.0.113.1`**.

### Tâche 3 — MTU (25 pts)

**`lab0`** doit porter un **MTU de 1400**.

### Tâche 4 — Nom local (25 pts)

**`lab-net.lab`** doit résoudre vers **`203.0.113.20`**, sans aucun serveur DNS.

---

**Tout est vérifié après un rechargement du réseau.** Ce que tu as tapé à la
main n'y survit pas.

## Valider

```bash
dsoxlab check drill-network
```
