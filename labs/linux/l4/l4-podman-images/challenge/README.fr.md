# Challenge — l4-podman-images

## Mission

Récupère, étiquette, sauvegarde et inspecte une image de conteneur.

## Objectif (état attendu)

1. L'image `localhost/rapport:v1` existe (pull depuis le registre + tag).
2. `/root/rapport.tar` est une archive d'image sauvegardée (`podman save`).
3. `skopeo inspect docker-archive:/root/rapport.tar` réussit.

## Contraintes

- Image de base : `registry.access.redhat.com/ubi9/ubi-micro`.
- On lit le magasin d'images de Podman et l'archive avec skopeo.

## Validation

```bash
dsoxlab check l4-podman-images
```
