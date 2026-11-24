# Récupérer une image, l'étiqueter, la livrer

## La situation

Les conteneurs partent d'images. Le travail quotidien sur les images : en
récupérer une depuis un registre, lui donner une étiquette parlante, et la
sauvegarder dans un fichier qu'on peut déplacer ou archiver, puis inspecter cette
archive pour être sûr de ce qu'elle contient.

L'idée : une image vit d'abord dans un registre, puis localement sous un ou
plusieurs noms, puis éventuellement dans une archive que l'on peut transporter.
Savoir passer d'une forme à l'autre, et savoir lire ce que contient une image
sans jamais l'exécuter, c'est le cœur de la gestion d'images.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/conteneurs/images-conteneurs/

## Ce qui est demandé

### Mission

Récupère, étiquette, sauvegarde et inspecte une image de conteneur.

### Objectif (état attendu)

1. L'image `localhost/rapport:v1` existe (pull depuis le registre + tag).
2. `/root/rapport.tar` est une archive d'image sauvegardée (`podman save`).
3. `skopeo inspect docker-archive:/root/rapport.tar` réussit.

### Contraintes

- Image de base : `registry.access.redhat.com/ubi9/ubi-micro`.
- On lit le magasin d'images de Podman et l'archive avec skopeo.

### Validation

```bash
dsoxlab check l4-podman-images
```
