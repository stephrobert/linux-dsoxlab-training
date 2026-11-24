# Un conteneur qui revient après reboot

## La situation

Un conteneur lancé avec `podman run` meurt avec la machine et ne revient jamais.
Sur RHEL, la façon moderne d'en faire un service à part entière, persistant au
boot, c'est **Quadlet** : une unité `.container` que systemd transforme en vrai
service.

L'idée : Quadlet décrit un conteneur dans une unité déclarative que systemd
convertit en service ordinaire, câblable au démarrage comme n'importe quel autre.
C'est ce que veut dire aujourd'hui l'objectif RHCSA « démarrer un conteneur au
boot », et pas un `podman run` bricolé dans rc.local.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/

## Ce qui est demandé

### Mission

Fais du conteneur `weblab` un service systemd persistant au boot avec Quadlet.

### Objectif (état attendu)

1. `/etc/containers/systemd/weblab.container` existe et a un `[Install] WantedBy`.
2. `weblab.service` est actif.
3. Le conteneur `weblab` tourne.

### Contraintes

- Ça doit être une unité Quadlet (pas un `podman run` manuel) : c'est le fichier
  `.container` sur disque avec une section `[Install]` qui survit au reboot.
- On lit l'état systemd et Podman, pas ton historique.

### Validation

```bash
dsoxlab check l4-podman-systemd-persist
```
