# Lab — gérer les images de conteneurs avec podman & skopeo

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-podman-images`

## Rappel

[**Les images de conteneurs sur le guide compagnon**](https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/)

`podman pull <ref>` récupère une image depuis un registre ; `podman tag <src>
<nom>` lui donne un nom local ; `podman save -o <fichier> <nom>` écrit une archive
portable ; `skopeo inspect docker-archive:<fichier>` lit les métadonnées d'une
archive sans l'exécuter. `podman image exists <nom>` teste la présence.

## Objectifs

- `localhost/rapport:v1` existe (pull + tag) ;
- `/root/rapport.tar` est une archive d'image sauvegardée ;
- `skopeo inspect docker-archive:/root/rapport.tar` réussit.

## Valider

```bash
dsoxlab check l4-podman-images
```
