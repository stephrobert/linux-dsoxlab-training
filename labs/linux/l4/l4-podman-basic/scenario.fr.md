# Contexte — faire tourner un conteneur

Podman est installé et l'image est déjà tirée. Lance un conteneur qui reste actif
en arrière-plan — le geste quotidien de Podman : un conteneur nommé, détaché.

Ta mission, sur la VM :

1. Lance un conteneur **détaché** nommé **`web`** à partir de
   `registry.access.redhat.com/ubi9/ubi-micro`, maintenu actif avec
   `sleep infinity`.
2. Confirme qu'il tourne (`podman ps`).

L'idée : `podman run -d --name web <image> <cmd>` démarre un conteneur en
arrière-plan ; `podman ps` liste les conteneurs actifs ; `podman inspect` lit leur
état. C'est la fondation sur laquelle s'appuie le lab de persistance de conteneur.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/
