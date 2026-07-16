# Contexte — récupérer une image, l'étiqueter, la livrer

Les conteneurs partent d'images. Le travail quotidien sur les images : en
récupérer une depuis un registre, lui donner une étiquette parlante, et la
sauvegarder dans un fichier qu'on peut déplacer ou archiver — puis inspecter cette
archive pour être sûr de ce qu'elle contient.

Ta mission, sur la VM :

1. **Récupère** `registry.access.redhat.com/ubi9/ubi-micro` (`podman pull`).
2. **Étiquette**-la en **`localhost/rapport:v1`** (`podman tag`).
3. **Sauvegarde** l'image étiquetée dans **`/root/rapport.tar`**
   (`podman save -o /root/rapport.tar localhost/rapport:v1`).
4. **Inspecte** l'archive avec skopeo :
   `skopeo inspect docker-archive:/root/rapport.tar`.

L'idée : `podman pull` récupère depuis un registre, `podman tag` donne un nom
local à une image, `podman save` l'écrit dans une archive portable, et
`skopeo inspect` lit une image (registre ou archive) sans l'exécuter — le cœur de
la gestion d'images.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/
