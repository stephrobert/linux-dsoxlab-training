# Systemd, contre la montre

## La situation

`systemd`, c'est là qu'un administrateur Linux passe ses journées : un service
qui doit revenir, une tâche qui doit tourner au bon moment, une unité qui ne
doit plus jamais démarrer. À l'examen, rien de tout ça n'est la question : c'est
l'**outillage** avec lequel tu réponds.

Ce drill est un **chrono** : 5 tâches, 25 minutes, aucun indice. Les mêmes
compétences servent RHCSA et LFCS, car systemd est systemd, sur RHEL comme sur
Debian.

Lis le sujet : `dsoxlab challenge drill-systemd`.

## Drill — systemd, timers et planification

**Format** : 5 tâches, 100 points, 25 minutes. **Aucun indice.**

```bash
dsoxlab check drill-systemd                  # AlmaLinux (défaut)
dsoxlab check drill-systemd --target ubuntu  # Ubuntu
```

---

### Tâche 1 — Un service qui survit (20 pts)

Crée **`labapi.service`**, qui exécute `/usr/local/bin/labapi.sh`. Il doit être
**activé**, **démarré**, et **redémarrer automatiquement en cas d'échec**.

### Tâche 2 — Un timer hebdomadaire (20 pts)

Crée **`labclean.timer`**, qui déclenche **`labclean.service`** tous les **lundis
à 04:00**. `labclean.service` doit exécuter `/usr/local/bin/labclean.sh`. Le
timer doit être activé et actif.

### Tâche 3 — Une tâche cron (20 pts)

Pour l'utilisateur **`opsuser`**, planifie `/usr/local/bin/labclean.sh` via
**cron**, **toutes les 15 minutes**.

### Tâche 4 — La bonne cible de démarrage (20 pts)

Ce serveur démarre en **`graphical.target`** — sur une machine sans écran. Fais
en sorte qu'il démarre par défaut en **`multi-user.target`**.

### Tâche 5 — Plus jamais (20 pts)

**`labdanger.service`** ne doit plus jamais démarrer, ni à la main, ni par
dépendance. Le désactiver ne suffit pas.

---

## Valider

```bash
dsoxlab check drill-systemd
```
