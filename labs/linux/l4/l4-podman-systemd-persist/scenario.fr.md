# Contexte — un conteneur qui revient après reboot

Un conteneur lancé avec `podman run` meurt avec la machine et ne revient jamais.
Sur RHEL, la façon moderne d'en faire un service à part entière, persistant au
boot, c'est **Quadlet** : une unité `.container` que systemd transforme en vrai
service.

L'idée : Quadlet décrit un conteneur dans une unité déclarative que systemd
convertit en service ordinaire, câblable au démarrage comme n'importe quel autre.
C'est ce que veut dire aujourd'hui l'objectif RHCSA « démarrer un conteneur au
boot », et pas un `podman run` bricolé dans rc.local.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/
