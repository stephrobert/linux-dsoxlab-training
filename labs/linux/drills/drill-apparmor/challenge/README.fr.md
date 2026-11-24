# AppArmor, l'autre MAC

## La situation

Debian et Ubuntu n'utilisent pas SELinux : ils utilisent **AppArmor**. Même but,
confiner un programme à ce dont il a légitimement besoin, mais un modèle
différent. AppArmor lie un profil à un **chemin**, là où SELinux étiquette
chaque objet.

Un profil peut être chargé et ne rien protéger du tout : il existe un mode où il
se contente de prendre des notes. C'est cette illusion de protection que ce
drill traque.

**Chrono** : 4 tâches, 15 minutes, aucun indice. LFCS uniquement ; RHEL a
SELinux, travaillé dans `drill-selinux`.

Lis le sujet : `dsoxlab challenge drill-apparmor`.

## Drill — AppArmor

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
