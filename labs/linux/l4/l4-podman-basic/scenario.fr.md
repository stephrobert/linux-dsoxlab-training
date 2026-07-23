# Contexte — faire tourner un conteneur

Podman est installé et l'image est déjà tirée. Lance un conteneur qui reste actif
en arrière-plan : le geste quotidien de Podman, un conteneur nommé et détaché.

L'idée : un conteneur tourne soit au premier plan, soit détaché en tâche de fond,
et c'est ce second mode, avec un nom explicite, qui sert au quotidien. Son état
se lit auprès de Podman, pas dans ton historique shell. C'est la fondation sur
laquelle s'appuie le lab de persistance de conteneur.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/
