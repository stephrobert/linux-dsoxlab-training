# Lab — lancer un conteneur détaché avec Podman

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-podman-basic`

## Rappel

[**Podman sur le guide compagnon**](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/)

`podman run -d --name <nom> <image> <cmd>` lance un conteneur détaché.
`podman ps` liste les conteneurs actifs ; `podman inspect -f '{{.State.Running}}'`
lit s'il tourne. `podman rm -f` le supprime.

## Objectifs

- un conteneur nommé `web` existe ;
- il **tourne** (`State.Running` = true) ;
- il utilise l'image `ubi9/ubi-micro`.

## Valider

```bash
dsoxlab check l4-podman-basic
```
