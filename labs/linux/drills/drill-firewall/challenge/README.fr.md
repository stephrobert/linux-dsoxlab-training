# Drill — pare-feu

**Format** : 5 tâches, 100 points, 20 minutes. **Aucun indice.**

Le sujet **ne nomme pas l'outil** : emploie celui de ta distribution.

> **Attention** : tu travailles à travers SSH. Perds-le et tu perds le drill.

```bash
dsoxlab check drill-firewall                  # AlmaLinux — firewalld
dsoxlab check drill-firewall --target ubuntu  # Ubuntu — ufw
```

---

### Tâche 1 — L'activer (20 pts)

Le pare-feu doit être **actif**, et l'être encore **après un reboot**.

### Tâche 2 — HTTP (20 pts)

Autorise **`80/tcp`**.

### Tâche 3 — L'application (20 pts)

Autorise **`8443/tcp`**.

### Tâche 4 — Garder la porte ouverte (20 pts)

**SSH doit rester autorisé.**

### Tâche 5 — Telnet, jamais (20 pts)

**`23/tcp`** doit être **explicitement rejeté** — pas seulement « non autorisé ».

---

**Tes règles sont vérifiées après un rechargement du pare-feu.** Une règle qui
n'y survit pas ne compte pas.

## Valider

```bash
dsoxlab check drill-firewall
```
