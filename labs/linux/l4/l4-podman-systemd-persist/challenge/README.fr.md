# Challenge — l4-podman-systemd-persist

## Mission

Fais du conteneur `weblab` un service systemd persistant au boot avec Quadlet.

## Objectif (état attendu)

1. `/etc/containers/systemd/weblab.container` existe et a un `[Install] WantedBy`.
2. `weblab.service` est actif.
3. Le conteneur `weblab` tourne.

## Contraintes

- Ça doit être une unité Quadlet (pas un `podman run` manuel) : c'est le fichier
  `.container` sur disque avec une section `[Install]` qui survit au reboot.
- On lit l'état systemd et Podman, pas ton historique.

## Validation

```bash
dsoxlab check l4-podman-systemd-persist
```
