# Faire tourner un conteneur

## La situation

Podman est installé et l'image est déjà tirée. Lance un conteneur qui reste actif
en arrière-plan : le geste quotidien de Podman, un conteneur nommé et détaché.

L'idée : un conteneur tourne soit au premier plan, soit détaché en tâche de fond,
et c'est ce second mode, avec un nom explicite, qui sert au quotidien. Son état
se lit auprès de Podman, pas dans ton historique shell. C'est la fondation sur
laquelle s'appuie le lab de persistance de conteneur.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/

## Ce qui est demandé

### Mission

Lance un conteneur détaché nommé `web` et prouve qu'il tourne.

### Objectif (état attendu)

1. Un conteneur nommé `web` existe.
2. Il tourne (`podman inspect -f '{{.State.Running}}' web` → `true`).
3. Il utilise l'image `ubi9/ubi-micro`.

### Contraintes

- On lit l'état du conteneur via Podman, pas ton historique shell.

### Validation

```bash
dsoxlab check l4-podman-basic
```
