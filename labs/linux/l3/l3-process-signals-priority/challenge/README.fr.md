# Faire s'effacer la tâche batch

## La situation

Un worker d'arrière-plan (`labworker.service`) tourne à fond en priorité normale
et rend la machine poussive pour tout le monde. Donne-lui un **nice de 10** pour
que l'ordonnanceur laisse passer le travail interactif d'abord — et que ça tienne
au redémarrage.

L'idée : la priorité d'un processus se fixe au lancement, et se corrige à chaud
sur un processus déjà en cours. Mais un service géré par systemd repart de sa
définition à chaque redémarrage : une correction à chaud ne lui survit pas.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/

## Ce qui est demandé

### Mission

Abaisse la priorité du service `labworker` à nice 10, durablement.

### Objectif (état attendu)

1. Le service `labworker` tourne.
2. Son processus tourne à **nice 10** (`ps -o ni= -p <MainPID>`).
3. `Nice=10` figure dans l'unit ou un drop-in (persistance).

### Contraintes

- Idéalement `systemctl edit labworker` (drop-in), puis `daemon-reload` + restart.
  La validation lit la **priorité live** du processus, pas la commande.

### Validation

```bash
dsoxlab check l3-process-signals-priority
```
