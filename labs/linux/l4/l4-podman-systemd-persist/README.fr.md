# Lab — conteneur persistant au boot avec Quadlet

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-podman-systemd-persist`

## Rappel

[**Quadlet sur le guide compagnon**](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/)

Quadlet transforme les fichiers `/etc/containers/systemd/*.container` en services
systemd au `daemon-reload`. Une section `[Container]` décrit l'image/la commande ;
la section `[Install] WantedBy=` fait démarrer le service généré au boot. Le nom
du service = nom du fichier + `.service` (ici `weblab.service`).

## Objectifs

- `/etc/containers/systemd/weblab.container` existe avec un `[Install] WantedBy` ;
- `weblab.service` est actif ;
- le conteneur `weblab` tourne.

## Valider

```bash
dsoxlab check l4-podman-systemd-persist
```
